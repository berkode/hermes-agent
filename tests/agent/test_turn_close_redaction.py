"""Tests for turn-close behavior: failed / content-policy-blocked turns whose
transcript tail is a tool message end with a valid assistant closer and keep
tool_call_id pairing intact — via close_interrupted_tool_sequence.
"""

from agent.conversation_loop import _content_policy_blocked_result
from agent.turn_recovery import _failed_turn_result


def _tool_tail():
    return [
        {"role": "user", "content": "run it"},
        {
            "role": "assistant",
            "content": "",
            "tool_calls": [
                {"id": "call_1", "function": {"name": "terminal", "arguments": "{}"}}
            ],
        },
        {"role": "tool", "tool_call_id": "call_1", "content": "raw output with sk-live-abc123secret"},
    ]


def test_failed_turn_tool_tail_ends_with_assistant_closer():
    """A failed turn whose transcript tail is a tool message ends with a valid
    assistant closer (role alternation preserved) and tool_call_id pairing intact."""
    messages = _tool_tail()
    result = _failed_turn_result("stopped", messages, 1, "boom")

    assert result["failed"] is True
    assert result["completed"] is False
    # The tail is now an assistant row, not a raw tool row.
    assert messages[-1]["role"] == "assistant"
    # The raw error string ("boom") is NOT placed into a transcript row the model sees.
    assert "boom" not in messages[-1]["content"]
    assert messages[-1]["content"] == "stopped"
    # The tool result row keeps its tool_call_id pairing intact.
    assert messages[-2]["role"] == "tool"
    assert messages[-2]["tool_call_id"] == "call_1"


def test_content_policy_blocked_turn_tool_tail_ends_with_assistant_closer():
    """A content-policy-blocked turn whose tail is a tool message ends with an
    assistant closer and keeps tool_call_id pairing intact."""
    messages = _tool_tail()
    result = _content_policy_blocked_result(
        messages, 1, final_response="blocked", error_detail="provider refused",
    )

    assert result["failed"] is True
    assert result["failure_reason"] == "content_policy_blocked"
    assert messages[-1]["role"] == "assistant"
    assert messages[-1]["content"] == "blocked"
    # The raw error detail ("provider refused") is NOT placed into a transcript row.
    assert "provider refused" not in messages[-1]["content"]
    assert messages[-2]["tool_call_id"] == "call_1"


def test_failed_turn_without_tool_tail_is_untouched():
    """A failed turn whose tail is already an assistant message needs no closer."""
    messages = [{"role": "user", "content": "hi"}, {"role": "assistant", "content": "partial"}]
    before = len(messages)
    result = _failed_turn_result("stopped", messages, 1, "boom")
    assert len(messages) == before
    assert result["failed"] is True
