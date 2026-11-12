"""Recovery for the masked privacy route's ``disallowed PII type SECRET`` refusal (#77484).

Tool results are scrubbed at construction (``make_tool_result_message``), so a block at this
point means the credential rode something else: a user turn, replayed assistant reasoning, a
tool-call argument, or a row restored from a session written before that boundary existed.
One re-scrub of the outgoing message list is worth a retry; the block is deterministic for the
payload, so an unchanged body is never resent and a second refusal is terminal.

The scrub also covers the turn's durable rows. A credential in the transcript outranks prompt
prefix stability: leaving it in ``messages`` would both re-trigger the block on the next API
call in this turn and persist it to ``state.db``, which is a leak the block itself just
reported. The same trade the persistence redactor (``_redact_display_metadata``) makes.
"""

from __future__ import annotations

import logging
from typing import Any

from agent.turn_failure_copy import CONTENT_POLICY_NEXT_STEPS, PII_BLOCK_NEXT_STEPS
from agent.turn_retry_state import TurnRetryState

logger = logging.getLogger("agent.conversation_loop")


def _pii_lines(agent: Any, *lines: str) -> None:
    """Force-``_vprint`` each line with the agent's prefix (sibling of ``turn_recovery._vlines``)."""
    for line in lines:
        agent._vprint(f"{agent.log_prefix}{line}", force=True, diagnostic=True)


def content_policy_block_lines(api_error: Exception) -> tuple[str, ...]:
    """The ``💡`` guidance for a content-policy block; the PII case names its own fix.

    A safety refusal is a rewording/other-model problem, so it also points at the fallback chain.
    A credential block is a redaction problem: another provider refuses it verbatim, so offering
    ``hermes fallback add`` would be advice that cannot help.
    """
    from agent.error_classifier import is_pii_secret_block

    if is_pii_secret_block(api_error):
        return (f"   💡 {PII_BLOCK_NEXT_STEPS}",)
    return (
        f"   💡 {CONTENT_POLICY_NEXT_STEPS}",
        "      To route future blocks to another provider automatically: hermes fallback add",
    )


def recover_pii_redaction(
    agent: Any, api_error: Exception, _retry: TurnRetryState,
    api_messages: Any, messages: Any = None,
) -> bool:
    """One re-scrub-and-retry after a ``disallowed PII type SECRET`` 400; True when retrying.

    Runs from ``recover_after_classification`` ahead of the format strips (a payload-content
    problem, not a request shape). Guarded by ``_retry.pii_redaction_retry_attempted`` so it
    fires at most once per API call, and it returns False when the scrub changed nothing — the
    caller then reports the block instead of resending an identical request."""
    if _retry.pii_redaction_retry_attempted:
        return False
    from agent.error_classifier import is_pii_secret_block

    if not is_pii_secret_block(api_error):
        return False

    from agent.redact import redact_outbound_messages

    _retry.pii_redaction_retry_attempted = True
    changed = redact_outbound_messages(api_messages)
    # Durable rows: same scrub, so the next request this turn and the persisted transcript
    # never carry the credential the provider just rejected.
    changed = redact_outbound_messages(messages) or changed
    if not changed:
        logger.warning(
            "%sPII block: re-scrub found no secret in the outgoing payload — "
            "not resending the identical request", agent.log_prefix,
        )
        return False
    _pii_lines(
        agent,
        "🔒 The provider's privacy filter rejected a credential in the request — "
        "removed it from the outgoing payload and retrying once...",
    )
    logger.warning("%sPII block: re-scrubbed the outgoing payload; retrying once", agent.log_prefix)
    return True


def recover_rejected_credentials(
    agent: Any, api_error: Exception, _retry: TurnRetryState, status_code: Any,
    api_messages: Any, messages: Any = None,
) -> bool:
    """The two one-shot credential repairs, in order: a PII-blocked payload, then a rejected key.

    Both fix the REQUEST's own material (what it carries, then which key it presents), which is
    why they run before the request-shape strips. Kept together so ``recover_after_classification``
    stays under its complexity cap while the order stays visible in one place.
    """
    from agent.turn_recovery import _refresh_credentials_after_401

    if recover_pii_redaction(agent, api_error, _retry, api_messages, messages):
        return True
    return _refresh_credentials_after_401(agent, api_error, _retry, status_code)


__all__ = ["content_policy_block_lines", "recover_pii_redaction", "recover_rejected_credentials"]
