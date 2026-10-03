from types import SimpleNamespace

import pytest

import config


class FakeClient:
    """Stands in for openai.OpenAI: returns queued replies and records each request."""

    def __init__(self, *replies: str, api_key: str | None = None):
        self.replies = list(replies) or ["ok"]
        self.calls: list[dict] = []
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self._create))

    def _create(self, **kwargs):
        self.calls.append(kwargs)
        reply = self.replies.pop(0) if len(self.replies) > 1 else self.replies[0]
        choices = [
            SimpleNamespace(message=SimpleNamespace(content=reply))
            for _ in range(kwargs.get("n", 1))
        ]
        return SimpleNamespace(id=f"resp-{len(self.calls)}", choices=choices)


@pytest.fixture(autouse=True)
def isolated(tmp_path, monkeypatch):
    """Every test gets its own DB and a fake key; nothing touches the real config or network."""
    monkeypatch.setattr(config, "DB_PATH", tmp_path / "results.db")
    monkeypatch.setattr(config, "LEGACY_CONFIG_PATH", tmp_path / "missing.yml")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
