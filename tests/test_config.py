import config


def test_api_key_order(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY")
    assert config.api_key() is None
    config.LEGACY_CONFIG_PATH.write_text("GPT3_API: from-yaml\n")
    assert config.api_key() == "from-yaml"
    monkeypatch.setenv("OPENAI_API_KEY", "from-env")
    assert config.api_key() == "from-env"
    assert config.api_key("from-sidebar") == "from-sidebar"


def test_api_key_ignores_non_mapping_yaml(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY")
    config.LEGACY_CONFIG_PATH.write_text("sk-just-a-string\n")
    assert config.api_key() is None
