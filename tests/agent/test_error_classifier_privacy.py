"""PII-SECRET 400 and deterministic 422 verdicts.

Companion to ``test_error_classifier.py`` (split out so the ratchet stays green). The two
deterministic classes:

* The masked privacy route's ``HTTP 400 request blocked: disallowed PII type SECRET`` must
  classify as ``content_policy_blocked`` with ``should_fallback=False`` — without the pattern it
  fell through ``_classify_400`` to ``format_error`` and walked the whole chain on a block every
  provider repeats verbatim.
* A 422 that NAMES what it rejected is deterministic for the payload, so it stops at one provider.
  A bare 422 keeps ``format_error``'s fallback: another provider may accept a different shape.
"""

import pytest

from agent.error_classifier import FailoverReason, classify_api_error
from tests.agent.test_error_classifier import MockAPIError


class TestPiiSecretBlock:
    @pytest.mark.parametrize(("status", "message"), [
        # The real cron error, verbatim (masked privacy route, HTTP 400).
        (400, "HTTP 400 request blocked: disallowed PII type SECRET"),
        (400, "Error code: 400 - {'error': {'message': "
              "'Request blocked: disallowed PII type SECRET', 'type': 'invalid_request_error'}}"),
        # Underscore spelling and the bare class name both ship from the same route.
        (400, "request blocked: disallowed_pii_type_secret"),
        (None, "disallowed PII type SECRET"),
    ], ids=["cron-verbatim", "sdk-envelope", "underscore", "status-less"])
    def test_disallowed_pii_secret_is_terminal_content_policy(self, status, message):
        """The masked route's 400 is a deterministic content block, NOT a fallback-walking
        format_error: every provider sees the same credential in the same payload."""
        e = MockAPIError(message, status_code=status,
                         body={"error": {"message": message, "type": "invalid_request_error"}})
        result = classify_api_error(e, provider="nous", model="m")
        assert result.reason == FailoverReason.content_policy_blocked
        assert result.retryable is False
        assert result.should_fallback is False
        assert result.should_compress is False
        assert result.should_rotate_credential is False

    def test_disallowed_pii_secret_does_not_disable_a_real_400_format_error(self):
        """A generic request-shape 400 keeps format_error's fallback — the PII patterns are narrow."""
        e = MockAPIError("Unsupported parameter: 'max_tokens'", status_code=400)
        result = classify_api_error(e, provider="openai", model="gpt-5")
        assert result.reason == FailoverReason.format_error
        assert result.should_fallback is True

    # ── Deterministic 422 ──

    def test_422_naming_its_rejected_field_does_not_walk_the_chain(self):
        """A pydantic relay's 422 names ``loc``: the same transcript rebuilds the same body on
        every provider, so the rejection is terminal instead of replaying down the chain."""
        body = {"detail": [{"loc": ["body", "stream_options", "include_usage"],
                            "msg": "Extra inputs are not permitted", "type": "extra_forbidden"}]}
        e = MockAPIError("Unprocessable Entity", status_code=422, body=body)
        result = classify_api_error(e, provider="azure-foundry", model="m")
        assert result.reason == FailoverReason.format_error
        assert result.retryable is False
        assert result.should_fallback is False

    def test_422_without_a_named_field_keeps_the_format_error_fallback(self):
        """A bare 422 states no cause: another provider may accept the request shape."""
        e = MockAPIError("Unprocessable Entity", status_code=422)
        result = classify_api_error(e, provider="custom", model="m")
        assert result.reason == FailoverReason.format_error
        assert result.should_fallback is True

    def test_422_naming_a_content_field_keeps_its_recovery_rung(self):
        """An image/tool-content 422 must reach its own recovery, not the terminal 422 verdict."""
        e = MockAPIError(
            "Error code: 422 - {'error': {'param': 'messages.67.tool.content.str', "
            "'type': 'invalid_request_error', 'message': 'Input should be a valid string'}}",
            status_code=422,
            body={"error": {"param": "messages.67.tool.content.str",
                            "message": "Input should be a valid string"}},
        )
        result = classify_api_error(e, provider="opencode-go", model="m")
        assert result.reason == FailoverReason.multimodal_tool_content_unsupported
