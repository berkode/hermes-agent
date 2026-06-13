"""Tests for Ollama/local model max-token routing."""

from agent.model_metadata import (
    is_ollama_routed_model,
    resolve_request_max_tokens,
    resolve_toolsets_for_model,
    should_skip_heavy_context_for_model,
)


class TestIsOllamaRoutedModel:
    def test_ollama_prefix(self):
        assert is_ollama_routed_model("ollama/gemma3:12b", "http://127.0.0.1:5102/v1")

    def test_bare_tag_on_pimono_proxy(self):
        assert is_ollama_routed_model("gemma3:12b", "http://127.0.0.1:5102/v1")

    def test_openrouter_not_ollama(self):
        assert not is_ollama_routed_model(
            "openrouter/owl-alpha",
            "http://127.0.0.1:5102/v1",
        )

    def test_direct_ollama_port(self):
        assert is_ollama_routed_model("qwen2.5:7b", "http://127.0.0.1:11434/v1")


class TestShouldSkipHeavyContext:
    def test_ollama_skips(self):
        assert should_skip_heavy_context_for_model(
            "ollama/gemma3:12b", "http://127.0.0.1:5102/v1",
        )

    def test_cloud_does_not_skip(self):
        assert not should_skip_heavy_context_for_model(
            "openrouter/owl-alpha", "http://127.0.0.1:5102/v1",
        )


class TestResolveToolsetsForModel:
    def test_ollama_all_becomes_light_bundle(self):
        got = resolve_toolsets_for_model(
            None, "ollama/gemma3:12b", "http://127.0.0.1:5102/v1",
        )
        assert got == ["safe", "file", "terminal", "todo", "search"]

    def test_cloud_unchanged(self):
        enabled = ["browser", "delegation"]
        assert resolve_toolsets_for_model(
            enabled, "openrouter/owl-alpha", "http://127.0.0.1:5102/v1",
        ) == enabled

    def test_full_toolsets_env_opt_out(self, monkeypatch):
        monkeypatch.setenv("HERMES_OLLAMA_FULL_TOOLSETS", "1")
        enabled = ["browser", "delegation"]
        assert resolve_toolsets_for_model(
            enabled, "ollama/gemma3:12b", "http://127.0.0.1:5102/v1",
        ) == enabled


class TestResolveRequestMaxTokens:
    def test_cloud_cap_unchanged(self):
        assert resolve_request_max_tokens(
            model="openrouter/owl-alpha",
            base_url="http://127.0.0.1:5102/v1",
            max_tokens=300,
        ) == 300

    def test_ollama_floor_when_cloud_cap_low(self):
        assert resolve_request_max_tokens(
            model="ollama/gemma3:12b",
            base_url="http://127.0.0.1:5102/v1",
            max_tokens=300,
        ) == 2048

    def test_ollama_explicit_override(self):
        assert resolve_request_max_tokens(
            model="ollama/gemma3:12b",
            base_url="http://127.0.0.1:5102/v1",
            max_tokens=300,
            max_tokens_ollama=4096,
        ) == 4096
