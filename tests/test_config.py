import config


def test_api_key_order(monkeypatch):
    monkeypatch.delenv("OPENROUTER_API_KEY")
    assert config.api_key() is None
    assert config.api_key("") is None
    monkeypatch.setenv("OPENROUTER_API_KEY", "from-env")
    assert config.api_key() == "from-env"
    assert config.api_key("from-sidebar") == "from-sidebar"


def test_model_list_is_free_only():
    assert config.FREE_ROUTER in config.MODELS
    assert all(config.is_free(m) for m in config.MODELS)
    assert not config.is_free("openai/gpt-4o")
