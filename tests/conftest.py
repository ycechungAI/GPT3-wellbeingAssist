from types import SimpleNamespace

import pytest


class FakeClient:
    """Stands in for openai.OpenAI: returns queued replies and records each request."""

    def __init__(self, *replies: str):
        self.replies = list(replies) or ["ok"]
        self.calls: list[dict] = []
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self._create))

    def _create(self, **kwargs):
        self.calls.append(kwargs)
        reply = self.replies.pop(0) if len(self.replies) > 1 else self.replies[0]
        message = SimpleNamespace(message=SimpleNamespace(content=reply))
        return SimpleNamespace(id=f"resp-{len(self.calls)}", choices=[message])


@pytest.fixture(autouse=True)
def fake_key(monkeypatch):
    """A fake key by default; no test touches the network or a real key."""
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
