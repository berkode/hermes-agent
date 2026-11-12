"""``redact_tool_result``: every string is scanned before it reaches the model.

Split out of ``test_redact.py`` so the tool-result / egress contract has its own file. The scrub
fails closed on unscannable containers, and the original credential never appears in a log record,
the outgoing provider payload, or the persisted transcript.
"""

import logging

import pytest


@pytest.fixture(autouse=True)
def _ensure_redaction_enabled(monkeypatch):
    """Ensure HERMES_REDACT_SECRETS is not disabled by prior test imports."""
    monkeypatch.delenv("HERMES_REDACT_SECRETS", raising=False)
    monkeypatch.setattr("agent.redact._REDACT_ENABLED", True)


class TestRedactToolResult:
    """``redact_tool_result`` scrubs key-like material from tool output before it reaches the model,
    failing closed on scan errors."""

    def test_prefix_api_keys_are_redacted(self):
        from agent.redact import redact_tool_result
        out = redact_tool_result("file contents: sk-live-0123456789abcdefghijklmnopqrstuvwxyz")
        assert "sk-live-" not in out
        assert "[REDACTED_SECRET]" in out

    def test_ghp_github_token_redacted(self):
        from agent.redact import redact_tool_result
        token = "ghp_" + "A" * 40
        out = redact_tool_result(f"leaked {token} here")
        assert token not in out
        assert "[REDACTED_SECRET]" in out

    def test_slack_token_redacted(self):
        from agent.redact import redact_tool_result
        token = "xoxb-" + "0" * 12 + "-" + "a" * 14
        out = redact_tool_result(f"slack {token}")
        assert token not in out
        assert "[REDACTED_SECRET]" in out

    def test_private_key_pem_redacted(self):
        from agent.redact import redact_tool_result
        pem = "-----BEGIN RSA PRIVATE KEY-----\nMIIEpAIBAAKCAQEA...\n-----END RSA PRIVATE KEY-----"
        out = redact_tool_result(f"key block:\n{pem}")
        assert "MIIEpAIBAAKCAQEA" not in out
        assert "[REDACTED_SECRET]" in out

    def test_jwt_redacted(self):
        from agent.redact import redact_tool_result
        jwt = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNtPn"
        out = redact_tool_result(f"token {jwt}")
        assert jwt not in out
        assert "[REDACTED_SECRET]" in out

    def test_high_entropy_hex_adjacent_to_secret_redacted(self):
        from agent.redact import redact_tool_result
        blob = "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2"
        out = redact_tool_result(f"secret: {blob}")
        assert blob not in out
        assert "[REDACTED_SECRET]" in out

    def test_high_entropy_base64_adjacent_to_secret_redacted(self):
        from agent.redact import redact_tool_result
        blob = "ZGF0YWJhc2U2NF9oaWdoX2VudHJvcHlfdmFsdWUxMjM0NTY3ODkw"
        out = redact_tool_result(f"password={blob}")
        assert blob not in out
        assert "[REDACTED_SECRET]" in out

    def test_ordinary_git_sha_not_mangled(self):
        from agent.redact import redact_tool_result
        sha = "0123456789abcdef0123456789abcdef01234567"
        text = f"commit {sha}\nfixup! {sha}"
        assert redact_tool_result(text) == text

    def test_ordinary_uuid_not_mangled(self):
        from agent.redact import redact_tool_result
        uuid = "550e8400-e29b-41d4-a716-446655440000"
        text = f"id={uuid} ref={uuid}"
        assert redact_tool_result(text) == text

    def test_long_hex_without_secret_keyword_not_mangled(self):
        from agent.redact import redact_tool_result
        blob = "deadbeef" * 8  # 64 hex chars, no secret keyword nearby
        text = f"hash={blob}"
        assert redact_tool_result(text) == text

    def test_encrypted_passthrough_placeholder_stays(self):
        from agent.redact import redact_tool_result
        text = "«redacted:ghp_…»"
        assert redact_tool_result(text) == text

    def test_multimodal_envelope_text_parts_redacted(self):
        from agent.redact import redact_tool_result
        token = "sk-live-0123456789abcdefghijklmnopqrstuvwxyz"
        env = {
            "_multimodal": True,
            "content": [
                {"type": "text", "text": f"found {token} in page"},
                {"type": "image", "image": "base64..."},
            ],
        }
        out = redact_tool_result(env)
        assert token not in str(out)
        assert "[REDACTED_SECRET]" in out["content"][0]["text"]
        assert out["content"][1]["type"] == "image"

    def test_fail_closed_on_scanner_error(self, monkeypatch):
        from agent.redact import redact_tool_result
        from agent import redact as R

        class ExplodingPattern:
            def sub(self, *args, **kwargs):
                raise RuntimeError("scan exploded")

        orig = R._PREFIX_RE
        monkeypatch.setattr(R, "_PREFIX_RE", ExplodingPattern())
        try:
            out = redact_tool_result("sk-live-0123456789abcdefghijklmnopqrstuvwxyz")
        finally:
            monkeypatch.setattr(R, "_PREFIX_RE", orig)
        assert out == "[REDACTED_SECRET]", out

    def test_non_string_content_passthrough(self):
        from agent.redact import redact_tool_result
        assert redact_tool_result(42) == 42
        assert redact_tool_result(None) is None


class TestToolResultWholeWordKeywordAdjacency:
    """High-entropy hex/base64 adjacency uses whole-word keyword matches, not substring stems."""

    def test_git_log_block_unchanged(self):
        """commit SHA plus an ``Author:`` line must not trip the adjacency matcher:
        "author" is not a secret keyword, and even "auth" (in "Author") must not
        substring-match the keyword set."""
        from agent.redact import redact_tool_result
        sha = "0123456789abcdef0123456789abcdef01234567"
        block = (
            f"commit {sha}\n"
            "Author: Jane Doe <jane@example.com>\n"
            "Date:   Wed Nov 11 11:21:05 2026 +0000\n"
            "\n"
            "    Fix redaction of tool-result secrets\n"
        )
        assert redact_tool_result(block) == block

    def test_hex_near_auth_prose_is_not_redacted(self):
        """``Authorization`` in prose contains ``auth`` as a stem, not a whole word —
        no redaction of adjacent hex."""
        from agent.redact import redact_tool_result
        blob = "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2"
        text = f"The Authorization header carried {blob}"
        assert redact_tool_result(text) == text

    def test_hex_near_passed_is_not_redacted(self):
        """``passed`` contains ``pass`` as a stem — no redaction of adjacent hex."""
        from agent.redact import redact_tool_result
        blob = "deadbeef" * 8
        text = f"The check passed with hash {blob}"
        assert redact_tool_result(text) == text

    def test_hex_next_to_whole_word_secret_is_redacted(self):
        """Whole-word ``secret`` adjacent to hex still redacts."""
        from agent.redact import redact_tool_result
        blob = "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2"
        text = f"secret: {blob}"
        assert "[REDACTED_SECRET]" in redact_tool_result(text)
        assert blob not in redact_tool_result(text)


class TestToolResultBearerAndDSN:
    """Prefix-less bearer tokens and DSN passwords must not survive redact_tool_result."""

    def test_prefixless_bearer_is_redacted(self):
        from agent.redact import redact_tool_result
        token = "sk-live-0123456789abcdefghijklmnopqrstuvwxyz"
        bearer = f"Authorization: Bearer {token}"
        out = redact_tool_result(bearer)
        assert bearer not in out
        assert token not in out
        assert "[REDACTED_SECRET]" in out

    def test_dsn_password_is_redacted(self):
        from agent.redact import redact_tool_result
        token = "sk-live-0123456789abcdefghijklmnopqrstuvwxyz"
        dsn = f"postgresql://app_user:{token}@db.example.com:5432/appdb"
        out = redact_tool_result(dsn)
        assert token not in out
        assert "[REDACTED_SECRET]" in out


class TestToolResultWalksEveryString:
    """redact_tool_result must walk raw strings, lists, dicts, multimodal parts, and text_summary."""

    def test_text_summary_is_redacted(self):
        from agent.redact import redact_tool_result
        token = "sk-live-0123456789abcdefghijklmnopqrstuvwxyz"
        result = {
            "_multimodal": True,
            "content": [{"type": "text", "text": "page snapshot"}],
            "text_summary": f"summary contains {token}",
        }
        out = redact_tool_result(result)
        assert token not in out["text_summary"]
        assert "[REDACTED_SECRET]" in out["text_summary"]

    def test_nested_dict_strings_redacted(self):
        from agent.redact import redact_tool_result
        token = "ghp_" + "A" * 40
        result = {"metadata": {"credential": token, "count": 3}, "other": "plain"}
        out = redact_tool_result(result)
        assert token not in str(out)
        assert "[REDACTED_SECRET]" in str(out)
        assert out["other"] == "plain"
        assert out["metadata"]["count"] == 3

    def test_list_of_strings_redacted(self):
        from agent.redact import redact_tool_result
        token = "xoxb-" + "0" * 12 + "-" + "a" * 14
        result = ["line one", f"line two {token} here", "line three"]
        out = redact_tool_result(result)
        assert token not in str(out)
        assert "[REDACTED_SECRET]" in out[1]

    def test_nested_list_of_lists_redacted(self):
        """Nested lists inside dicts must be walked (not skipped)."""
        from agent.redact import redact_tool_result
        token = "xoxb-" + "0" * 12 + "-" + "a" * 14
        result = {"rows": [["line one", f"line two {token} here"], ["line three"]]}
        out = redact_tool_result(result)
        assert token not in str(out)
        assert "[REDACTED_SECRET]" in str(out)

    def test_tuple_and_bytes_fail_closed(self):
        """Tuples, bytes, and other unscannable containers fail closed to
        [REDACTED_SECRET], never returned raw. Ints/None pass through."""
        from agent.redact import redact_tool_result
        token = "sk-live-0123456789abcdefghijklmnopqrstuvwxyz"

        out = redact_tool_result(b"raw bytes with " + token.encode())
        assert token not in str(out)
        assert "[REDACTED_SECRET]" in str(out)

        result = {"data": ("tuple contains", token), "count": 42, "note": None}
        out = redact_tool_result(result)
        assert token not in str(out)
        assert "[REDACTED_SECRET]" in str(out)
        assert out["count"] == 42
        assert out["note"] is None

    def test_int_and_none_pass_through(self):
        from agent.redact import redact_tool_result
        assert redact_tool_result(42) == 42
        assert redact_tool_result(None) is None
        assert redact_tool_result(True) is True
        assert redact_tool_result(3.14) == 3.14

    def test_unscannable_value_fails_closed(self, monkeypatch):
        """If a value cannot be scanned, fail closed — never return raw structured content."""
        from agent.redact import redact_tool_result
        from agent import redact as R

        class ExplodingPattern:
            def sub(self, *args, **kwargs):
                raise RuntimeError("scan exploded")

        orig = R._PREFIX_RE
        monkeypatch.setattr(R, "_PREFIX_RE", ExplodingPattern())
        try:
            out = redact_tool_result({"nested": {"credential": "sk-live-0123456789abcdefghijklmnopqrstuvwxyz"}})
        finally:
            monkeypatch.setattr(R, "_PREFIX_RE", orig)
        # The unscannable string value becomes [REDACTED_SECRET]; no raw secret survives.
        assert out == {"nested": {"credential": "[REDACTED_SECRET]"}}, out


class TestProviderEgressContainsNoToolSecret:
    """A mocked outgoing provider request (assembled messages or HTTP body) contains
    none of a tool-returned key-like fixture, including prefix-less bearer tokens
    and DSN passwords."""

    def _make_tool_result_messages(self, token: str, tool_call_id: str = "call_1"):
        from agent.redact import redact_tool_result
        from agent.tool_dispatch_helpers import make_tool_result_message

        dsn = f"postgresql://app_user:{token}@db.example.com:5432/appdb"
        tool_msg = make_tool_result_message(
            "read_file", f"file contents:\n{dsn}", tool_call_id
        )
        messages = [
            {"role": "user", "content": "read the file"},
            {
                "role": "assistant",
                "content": "",
                "tool_calls": [
                    {
                        "id": tool_call_id,
                        "type": "function",
                        "function": {"name": "read_file", "arguments": "{}"},
                    }
                ],
            },
            tool_msg,
        ]
        return messages, tool_msg, dsn

    def test_assembled_messages_have_no_tool_returned_secret(self):
        """Outgoing provider messages assembled from tool results must not contain
        a tool-returned DSN password or prefix-less bearer token raw."""
        from agent.redact import redact_tool_result

        token = "sk-live-0123456789abcdefghijklmnopqrstuvwxyz"
        bearer = f"Authorization: Bearer {token}"
        messages, tool_msg, _dsn = self._make_tool_result_messages(bearer)

        # Simulate assembling the outgoing provider request from messages.
        assembled = "\n".join(str(m) for m in messages)
        assert bearer not in assembled
        assert token not in assembled
        assert "[REDACTED_SECRET]" in tool_msg["content"]

    def test_http_body_contains_no_tool_returned_dsn_password(self):
        """Mock an HTTP request body assembled from tool results; the DSN password
        and prefix-less bearer token must not appear raw."""
        import json

        token = "sk-live-0123456789abcdefghijklmnopqrstuvwxyz"
        bearer = f"Authorization: Bearer {token}"
        messages, _tool_msg, _dsn = self._make_tool_result_messages(bearer)

        body = json.dumps({"messages": messages})
        assert bearer not in body
        assert token not in body
        assert "[REDACTED_SECRET]" in body



class TestRedactionTurnContinuesAndNoLogLeak:
    """Redaction of secret-like spans lets the turn continue, and the original
    secret value never appears in logs or outgoing provider payloads.
    """

    def test_redacted_tool_result_lets_turn_continue(self, monkeypatch, caplog):
        """A tool result containing a secret is redacted before reaching the model,
        so the turn continues instead of being blocked with HTTP 400 PII."""
        from agent.redact import redact_tool_result

        secret = "sk-test-FAKE-key-that-looks-like-a-real-key"
        tool_output = f"Obsidian vault note:\nAPI_KEY={secret}\nmore content here"

        # Redact before the request goes to the masked privacy route
        redacted = redact_tool_result(tool_output)
        assert secret not in redacted
        assert redacted == "[REDACTED_SECRET]"

        # The original secret must not appear in log records:
        # only the redacted form may be logged.
        caplog.set_level(logging.DEBUG)
        logger = logging.getLogger("agent.redact")
        logger.debug("processing tool output: %s", redacted)
        for record in caplog.records:
            assert secret not in record.getMessage(), "secret leaked into log"

        # The redacted output can safely go to the model (turn continues)
        assert "[REDACTED_SECRET]" in redacted

    def test_prefixless_bearer_redacted_in_outgoing_payload(self):
        """A prefix-less 'Authorization: Bearer <opaque 20+ char token>' and a
        postgres DSN password must not survive redact_tool_result."""
        from agent.redact import redact_tool_result

        token = "sk-live-0123456789abcdefghijklmnopqrstuvwxyz"
        bearer = f"Authorization: Bearer {token}"
        dsn = f"postgresql://app_user:{token}@db.example.com:5432/appdb"

        assert token not in redact_tool_result(bearer)
        assert token not in redact_tool_result(dsn)

    def test_normal_git_log_block_unchanged(self):
        """A normal git log / git show block (commit SHA plus an Author: line)
        must remain unchanged — whole-word keyword matches, not substring stems."""
        from agent.redact import redact_tool_result

        text = """commit 0123456789abcdef0123456789abcdef01234567
Author: Jane Doe <jane@example.com>
Date:   Mon Nov 9 10:00:00 2026 +0000

    Fix cron timeout on bej profile

diff --git a/cron/scheduler.py b/cron/scheduler.py
index abcdef1..1234567 100644
--- a/cron/scheduler.py
+++ b/cron/scheduler.py
@@ -1 +1 @@
-old code
+new code
"""
        result = redact_tool_result(text)
        assert result == text, f"git log block was mangled: {result!r}"
