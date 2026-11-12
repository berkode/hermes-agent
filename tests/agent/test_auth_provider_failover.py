"""Auth-failure provider failover (conversation loop).

A 401/403 that survives the per-provider credential-refresh attempt
(revoked OAuth, blocked/expired key, an account pinned to a dead/staging
endpoint) must escalate to the configured fallback chain instead of
thrashing on the same dead credential every turn.

Before the fix, the conversation loop's generic failover dispatch only
fired for ``{rate_limit, billing}`` reasons; ``auth`` / ``auth_permanent``
fell through to "switch providers manually" advice and never called
``_try_activate_fallback()``. These tests pin:

  1. 401/403 classify as auth (``classified.is_auth`` True).
  2. ``_try_activate_fallback`` advances the chain on an auth reason.
"""

from unittest.mock import MagicMock, patch

from run_agent import AIAgent
from agent.error_classifier import classify_api_error, FailoverReason

def _make_agent(fallback_model=None):
    with (
        patch("model_tools.get_tool_definitions", return_value=[]),
        patch("model_tools.check_toolset_requirements", return_value={}),
        patch("agent.process_bootstrap.OpenAI"),
    ):
        agent = AIAgent(
            api_key="test-key",
            base_url="https://openrouter.ai/api/v1",
            quiet_mode=True,
            skip_context_files=True,
            skip_memory=True,
            fallback_model=fallback_model,
        )
        agent.client = MagicMock()
        return agent

def _mock_client(base_url="https://openrouter.ai/api/v1", api_key="fb-key"):
    mock = MagicMock()
    mock.base_url = base_url
    mock.api_key = api_key
    return mock

def _auth_error(status=401, msg="Your API key is invalid, blocked or out of funds."):
    err = Exception(f"Error code: {status} - {msg}")
    err.status_code = status
    return err

class TestAuthErrorClassification:
    def test_401_is_auth(self):
        c = classify_api_error(_auth_error(401))
        assert c.reason in {FailoverReason.auth, FailoverReason.auth_permanent}
        assert c.is_auth is True

    def test_500_is_not_auth(self):
        err = Exception("Error code: 500 - internal server error")
        err.status_code = 500
        c = classify_api_error(err)
        assert c.is_auth is False

class TestAuthFailoverActivation:
    """The decision the loop makes on a persistent auth failure: when a
    fallback chain exists and the guard hasn't fired, escalate to it."""

    def test_auth_failover_fires_when_chain_present(self):
        agent = _make_agent(fallback_model=[{"provider": "openai", "model": "gpt-4o"}])
        classified = classify_api_error(_auth_error(401))
        # The activation primitive advances the chain on an auth reason.
        with patch(
            "agent.auxiliary_client.resolve_provider_client",
            return_value=(_mock_client(), "gpt-4o"),
        ):
            advanced = agent._try_activate_fallback(reason=classified.reason)
        assert advanced is True
        assert agent._fallback_index == 1




# ── The loop-level contract (full run_conversation drive) ─────────────────────
#
# The activation primitive already advances on an auth reason (above). These pin
# the end-to-end consequence: a credential verdict is per-PROVIDER, so a 401/403
# on A must still reach B — while a content/PII block is per-PAYLOAD and must
# stop at one provider.

def _mock_response(content: str):
    from types import SimpleNamespace

    msg = SimpleNamespace(content=content, tool_calls=None)
    choice = SimpleNamespace(message=msg, finish_reason="stop")
    return SimpleNamespace(choices=[choice], model="fallback/model", usage=None)


def _pii_400():
    err = Exception("HTTP 400 request blocked: disallowed PII type SECRET")
    err.status_code = 400
    err.body = {"error": {"message": "request blocked: disallowed PII type SECRET"}}
    return err


def _drive_turn(agent, failures):
    """Run one turn whose API call raises ``failures`` in order; return (result, calls)."""
    calls = []

    def fake_api_call(api_kwargs):
        calls.append((agent.provider, agent.model))
        idx = len(calls) - 1
        if idx < len(failures):
            raise failures[idx]
        return _mock_response("answered by the second provider")

    with (
        patch.object(agent, "_interruptible_api_call", side_effect=fake_api_call),
        patch.object(agent, "_persist_session"),
        patch.object(agent, "_save_trajectory"),
        patch.object(agent, "_cleanup_task_resources"),
        patch("agent.process_bootstrap.OpenAI", return_value=MagicMock()),
        patch("agent.agent_runtime_helpers.time.sleep"),
        patch(
            "agent.auxiliary_client.resolve_provider_client",
            return_value=(_mock_client(), "gpt-4o"),
        ),
        patch("hermes_cli.model_normalize.normalize_model_for_provider", side_effect=lambda m, p: m),
        patch("agent.model_metadata.get_model_context_length", return_value=200000),
    ):
        return agent.run_conversation("hello"), calls


class TestAuthFailoverReachesTheSecondProvider:
    def test_401_on_provider_a_tries_provider_b(self):
        agent = _make_agent(fallback_model=[{"provider": "openai", "model": "gpt-4o"}])
        agent._api_max_retries = 1
        result, calls = _drive_turn(agent, [_auth_error(401)])

        assert len(calls) == 2, calls
        assert calls[0][0] != calls[1][0], calls
        assert agent._fallback_activated is True
        assert result["completed"] is True

    def test_403_on_provider_a_tries_provider_b(self):
        agent = _make_agent(fallback_model=[{"provider": "openai", "model": "gpt-4o"}])
        agent._api_max_retries = 1
        result, calls = _drive_turn(agent, [_auth_error(403)])
        assert len(calls) == 2, calls
        assert result["completed"] is True

    def test_a_pii_400_stops_at_the_first_provider(self):
        """Every provider sees the same credential verbatim: walking the chain only repeats it."""
        agent = _make_agent(fallback_model=[{"provider": "openai", "model": "gpt-4o"}])
        agent._api_max_retries = 2
        result, calls = _drive_turn(agent, [_pii_400()])

        assert len(calls) == 1, calls
        assert result["completed"] is False
        assert result["failed"] is True
        assert agent._fallback_activated is False
