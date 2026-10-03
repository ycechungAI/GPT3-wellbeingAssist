import llm


def test_api_key_order(monkeypatch):
    monkeypatch.delenv("OPENROUTER_API_KEY")
    assert llm.api_key() is None and llm.api_key("") is None
    monkeypatch.setenv("OPENROUTER_API_KEY", "from-env")
    assert llm.api_key() == "from-env"
    assert llm.api_key("from-sidebar") == "from-sidebar"


def test_client_has_short_timeout():
    c = llm.client("k")
    assert c.timeout == llm.TIMEOUT_SECONDS and c.max_retries == 0
    assert str(c.base_url).startswith("https://openrouter.ai/api/v1")


def test_free_models_only():
    assert all(llm.is_free(m) for m in llm.FREE_MODELS)
    assert llm.is_free("openrouter/free") and llm.is_free("google/gemma-4-31b-it:free")
    assert not llm.is_free("openai/gpt-4o")
