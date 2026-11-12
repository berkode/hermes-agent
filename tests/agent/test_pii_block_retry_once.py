"""The masked privacy relay's "disallowed PII" rejection: one scrub, then stop.

Every string that can reach a chat-completions body gets scrubbed, and a scrub that changes
nothing is never resent: the rejection is deterministic for the payload, so replaying an
identical body only burns the retry budget. The credential itself must never appear in the log
line or the terminal copy that reports the block.
"""

import logging

import pytest

from agent.error_classifier import FailoverReason, classify_api_error, is_pii_secret_block
from agent.redact import redact_outbound_messages
from agent.turn_recovery_privacy import recover_pii_redaction
from agent.turn_retry_state import TurnRetryState
from tests.agent.test_error_classifier import MockAPIError

# Shaped like a credential so the scanners treat it as one; not a real key.
FAKE_SECRET = "sk-test-FAKE0000000000000000000000000000000000000000"

PII_MESSAGE = "HTTP 400 request blocked: disallowed PII type SECRET"


def _pii_error(status_code=400) -> MockAPIError:
    return MockAPIError(
        PII_MESSAGE,
        status_code=status_code,
        body={"error": {"message": PII_MESSAGE, "type": "invalid_request_error"}},
    )


class _FakeAgent:
    """The only AIAgent surface this recovery touches: a prefix and a forced printer."""

    log_prefix = "[test] "

    def __init__(self):
        self.printed: list[str] = []

    def _vprint(self, text, force=False, diagnostic=False):
        self.printed.append(text)


# ── Classification ────────────────────────────────────────────────────────


class TestPiiSecretClassification:
    def test_the_verbatim_cron_error_is_terminal_content_policy(self):
        """Without the pattern this 400 landed on format_error and walked the whole chain."""
        result = classify_api_error(_pii_error(), provider="nous")
        assert result.reason == FailoverReason.content_policy_blocked
        assert result.retryable is False
        assert result.should_fallback is False
        assert result.should_compress is False
        assert result.should_rotate_credential is False

    def test_a_status_less_block_is_still_content_policy(self):
        result = classify_api_error(_pii_error(status_code=None), provider="nous")
        assert result.reason == FailoverReason.content_policy_blocked
        assert result.should_fallback is False

    @pytest.mark.parametrize("message", [
        PII_MESSAGE,
        "request blocked: disallowed_pii",
        "disallowed PII type secret",
        "blocked: PII blocked by the privacy route",
    ])
    def test_the_predicate_matches_the_wording_variants(self, message):
        assert is_pii_secret_block(message) is True

    @pytest.mark.parametrize("message", [
        "Unsupported parameter: 'max_tokens'",
        "Invalid JSON body",
        "",
        None,
    ])
    def test_the_predicate_ignores_everything_else(self, message):
        assert is_pii_secret_block(message) is False


# ── Outbound scrub ────────────────────────────────────────────────────────


class TestRedactOutboundMessages:
    def test_scrubs_user_content_and_reasoning(self):
        messages = [
            {"role": "user", "content": f"deploy with {FAKE_SECRET} please"},
            {"role": "assistant", "content": "ok", "reasoning_content": f"the key was {FAKE_SECRET}"},
        ]
        assert redact_outbound_messages(messages) is True
        assert FAKE_SECRET not in repr(messages)
        # Masked in place (head/tail form for a long token), not merely dropped.
        assert "sk-tes" in messages[0]["content"] and "please" in messages[0]["content"]
        assert messages[1]["reasoning_content"] != f"the key was {FAKE_SECRET}"

    def test_scrubs_tool_call_arguments(self):
        messages = [{"role": "assistant", "tool_calls": [
            {"id": "c1", "function": {"name": "run", "arguments": f'{{"key": "{FAKE_SECRET}"}}'}},
        ]}]
        assert redact_outbound_messages(messages) is True
        assert FAKE_SECRET not in repr(messages)

    def test_scrubs_nested_multimodal_text_parts(self):
        messages = [{"role": "user", "content": [
            {"type": "text", "text": f"token {FAKE_SECRET}"},
            {"type": "image_url", "image_url": {"url": "data:image/png;base64,AAAA"}},
        ]}]
        assert redact_outbound_messages(messages) is True
        assert FAKE_SECRET not in repr(messages)

    def test_reports_a_clean_payload_as_unchanged(self):
        """No secret means no mutation -- the caller must not resend an identical body."""
        messages = [{"role": "user", "content": "a normal question"},
                    {"role": "assistant", "content": "an answer"}]
        assert redact_outbound_messages(messages) is False
        assert messages[0]["content"] == "a normal question"

    def test_tolerates_shapes_it_does_not_own(self):
        assert redact_outbound_messages(None) is False
        assert redact_outbound_messages({"not": "a list"}) is False
        assert redact_outbound_messages([None, 3, "a bare string"]) is False


# ── One notification, one retry ───────────────────────────────────────────


class TestRecoverPiiRedaction:
    def test_first_block_with_a_secret_scrubs_and_retries(self):
        agent = _FakeAgent()
        api_messages = [{"role": "user", "content": f"key={FAKE_SECRET}"}]
        durable = [{"role": "user", "content": f"key={FAKE_SECRET}"}]
        retry = TurnRetryState()

        assert recover_pii_redaction(agent, _pii_error(), retry, api_messages, durable) is True
        assert FAKE_SECRET not in repr(api_messages)
        # The durable transcript is what persists and replays; it is scrubbed in the same pass.
        assert FAKE_SECRET not in repr(durable)
        assert retry.pii_redaction_retry_attempted is True

    def test_a_second_block_is_terminal(self):
        agent = _FakeAgent()
        api_messages = [{"role": "user", "content": f"key={FAKE_SECRET}"}]
        retry = TurnRetryState()

        assert recover_pii_redaction(agent, _pii_error(), retry, api_messages) is True
        assert recover_pii_redaction(agent, _pii_error(), retry, api_messages) is False

    def test_an_unchanged_payload_is_never_resent(self, caplog):
        agent = _FakeAgent()
        api_messages = [{"role": "user", "content": "an innocuous request"}]
        retry = TurnRetryState()

        with caplog.at_level(logging.WARNING):
            assert recover_pii_redaction(agent, _pii_error(), retry, api_messages) is False

        assert "not resending the identical request" in caplog.text
        assert not any("retrying once" in line for line in agent.printed)

    def test_other_errors_are_not_this_recovery(self):
        agent = _FakeAgent()
        api_messages = [{"role": "user", "content": f"key={FAKE_SECRET}"}]
        retry = TurnRetryState()

        assert recover_pii_redaction(
            agent, MockAPIError("Rate limit exceeded", status_code=429), retry, api_messages,
        ) is False
        # Untouched: the flag belongs to this recovery, not to "some recovery ran".
        assert retry.pii_redaction_retry_attempted is False
        assert FAKE_SECRET in repr(api_messages)

    def test_the_raw_credential_never_reaches_the_log_or_the_terminal(self, caplog):
        agent = _FakeAgent()
        api_messages = [{"role": "user", "content": f"key={FAKE_SECRET}"}]
        retry = TurnRetryState()

        with caplog.at_level(logging.DEBUG):
            assert recover_pii_redaction(agent, _pii_error(), retry, api_messages) is True
            assert recover_pii_redaction(agent, _pii_error(), retry, api_messages) is False

        assert FAKE_SECRET not in caplog.text
        assert FAKE_SECRET not in "\n".join(agent.printed)


# ── Failure copy ──────────────────────────────────────────────────────────


class TestPiiBlockCopy:
    def test_the_pii_guidance_names_the_credential_fix_not_a_fallback(self):
        """A credential block is a redaction problem: ``hermes fallback add`` cannot help."""
        from agent.turn_recovery_privacy import content_policy_block_lines

        lines = content_policy_block_lines(_pii_error())
        assert len(lines) == 1
        assert "credential" in lines[0]
        assert "fallback add" not in lines[0]

    def test_a_plain_safety_block_keeps_the_fallback_suggestion(self):
        from agent.turn_recovery_privacy import content_policy_block_lines

        lines = content_policy_block_lines(Exception("violates our usage policies"))
        assert any("hermes fallback add" in line for line in lines)

    def test_the_terminal_copy_names_the_credential_case(self):
        from agent.turn_failure_copy import content_policy_copy

        copy = content_policy_copy(label="nous", summary="blocked", pii_block=True)
        assert "credential" in copy
        plain = content_policy_copy(label="nous", summary="blocked")
        assert "credential" not in plain


# ── Loop-level: retry once, then stop ─────────────────────────────────────


def _agent_with_fallback():
    """A real AIAgent with one fallback provider and a fake API call, per test."""
    from unittest.mock import MagicMock, patch

    from run_agent import AIAgent

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
            fallback_model=[{"provider": "openai", "model": "gpt-4o"}],
        )
    agent.client = MagicMock()
    return agent


def _drive(agent, failures, secret):
    """Run one turn; the first API call carries ``secret`` in a user row, later calls answer.

    Returns ``(result, sent)`` where ``sent`` is the payload each call actually sent.
    """
    from unittest.mock import MagicMock, patch

    sent: list[str] = []

    def fake_api_call(api_kwargs):
        payload = repr(api_kwargs)
        sent.append(payload)
        idx = len(sent) - 1
        if idx < len(failures):
            raise failures[idx]
        return _mock_answer("done")

    with (
        patch.object(agent, "_interruptible_api_call", side_effect=fake_api_call),
        patch.object(agent, "_persist_session"),
        patch.object(agent, "_save_trajectory"),
        patch.object(agent, "_cleanup_task_resources"),
        patch("agent.process_bootstrap.OpenAI", return_value=MagicMock()),
        patch("agent.agent_runtime_helpers.time.sleep"),
        patch("agent.auxiliary_client.resolve_provider_client",
              return_value=(MagicMock(), "gpt-4o")),
        patch("hermes_cli.model_normalize.normalize_model_for_provider", side_effect=lambda m, p: m),
        patch("agent.model_metadata.get_model_context_length", return_value=200000),
    ):
        return agent.run_conversation(f"deploy using {secret} now"), sent


def _mock_answer(content: str):
    from types import SimpleNamespace

    return SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content=content, tool_calls=None),
                                 finish_reason="stop")],
        model="fallback/model", usage=None,
    )


class TestLoopRetryOnceThenStop:
    def test_the_first_pii_400_resends_a_different_payload(self):
        """The retry exists only because the scrub changed the body: assert it did."""
        agent = _agent_with_fallback()
        agent._api_max_retries = 2
        result, sent = _drive(agent, [_pii_error()], FAKE_SECRET)

        assert len(sent) == 2, sent
        assert FAKE_SECRET in sent[0]
        assert FAKE_SECRET not in sent[1]
        assert result["completed"] is True

    def test_a_second_pii_400_stops_and_reports(self):
        """Two refusals mean the scrub cannot fix it: fail, do not walk the chain or loop."""
        agent = _agent_with_fallback()
        agent._api_max_retries = 2
        result, sent = _drive(agent, [_pii_error(), _pii_error()], FAKE_SECRET)

        assert len(sent) == 2, sent
        assert result["completed"] is False
        assert result["failed"] is True
        assert agent._fallback_activated is False

    def test_an_unrepairable_block_is_not_resent_at_all(self):
        """No credential in the payload ⇒ nothing to scrub ⇒ no second, identical request."""
        agent = _agent_with_fallback()
        agent._api_max_retries = 2
        result, sent = _drive(agent, [_pii_error()], "not-a-secret")

        assert len(sent) == 1, sent
        assert result["completed"] is False
        assert result["failed"] is True

    def test_the_secret_never_reaches_the_persisted_rows_or_the_formatted_logs(self):
        """The durable rows and every formatted log line are scrubbed.

        The raw user echo in ``turn_context`` is not the log surface;
        ``RedactingFormatter`` is, so assert on its output."""
        from agent.redact import RedactingFormatter

        agent = _agent_with_fallback()
        agent._api_max_retries = 2
        persisted: list[str] = []
        records: list[logging.LogRecord] = []

        class _Capture(logging.Handler):
            def emit(self, record):
                records.append(record)

        handler = _Capture()
        handler.setFormatter(RedactingFormatter("%(message)s"))
        root = logging.getLogger()
        root.addHandler(handler)
        from unittest.mock import patch as _patch
        try:
            with _patch.object(
                agent, "_persist_session",
                side_effect=lambda m, h=None: persisted.append(repr(m)),
            ):
                _result, _sent = _drive(agent, [_pii_error()], FAKE_SECRET)
        finally:
            root.removeHandler(handler)

        formatted = "\n".join(handler.format(record) for record in records)
        assert FAKE_SECRET not in formatted
        assert all(FAKE_SECRET not in blob for blob in persisted)
