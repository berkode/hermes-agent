"""Tests for Ollama history trim and compressor threshold."""

from agent.context_compressor import _threshold_tokens_for_context
from agent.model_metadata import trim_conversation_history_for_local_model


class TestOllamaCompressorThreshold:
    def test_small_runtime_ctx_not_floored_to_64k(self):
        # 16K Ollama window at 50% → 8K threshold, not 64K minimum.
        assert _threshold_tokens_for_context(16_384, 0.50) == 8_192

    def test_large_ctx_keeps_64k_floor(self):
        assert _threshold_tokens_for_context(128_000, 0.50) == 64_000


class TestTrimConversationHistory:
    def test_trims_long_history(self):
        history = [{"role": "user", "content": f"msg {i}"} for i in range(40)]
        trimmed = trim_conversation_history_for_local_model(
            history, "ollama/gemma3:12b", "http://127.0.0.1:5102/v1",
            max_messages=10,
        )
        assert len(trimmed) == 10

    def test_cloud_unchanged(self):
        history = [{"role": "user", "content": "hi"}] * 40
        assert trim_conversation_history_for_local_model(
            history, "openrouter/owl-alpha", "http://127.0.0.1:5102/v1",
        ) == history
