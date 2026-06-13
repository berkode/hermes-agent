"""Tests for Ollama length-continuation acceptance."""

from unittest.mock import MagicMock

from run_agent import AIAgent


def _agent(model: str, base_url: str) -> AIAgent:
    agent = object.__new__(AIAgent)
    agent.model = model
    agent.base_url = base_url
    agent._strip_think_blocks = AIAgent._strip_think_blocks.__get__(agent, AIAgent)
    return agent


class TestOllamaLengthAcceptance:
    def test_greeting_without_punctuation_accepted(self):
        agent = _agent("ollama/gemma3:12b", "http://127.0.0.1:5102/v1")
        assert agent._should_accept_length_as_complete(
            "Hello Master, how can I help",
            has_tool_calls=False,
        )

    def test_cloud_requires_natural_ending(self):
        agent = _agent("openrouter/owl-alpha", "http://127.0.0.1:5102/v1")
        assert not agent._should_accept_length_as_complete(
            "Hello Master, how can I help",
            has_tool_calls=False,
        )
        assert agent._should_accept_length_as_complete(
            "Hello Master!",
            has_tool_calls=False,
        )

    def test_ellipsis_not_accepted_on_ollama(self):
        agent = _agent("gemma3:12b", "http://127.0.0.1:5102/v1")
        assert not agent._should_accept_length_as_complete(
            "Let me think about this...",
            has_tool_calls=False,
        )

    def test_tool_calls_never_accepted(self):
        agent = _agent("ollama/gemma3:12b", "http://127.0.0.1:5102/v1")
        assert not agent._should_accept_length_as_complete(
            "Running the command now.",
            has_tool_calls=True,
        )
