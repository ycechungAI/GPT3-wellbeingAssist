"""Paths, model choices, dataset discovery and API-key lookup shared by every page."""

import os
from pathlib import Path

import yaml
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
ASSETS_DIR = ROOT / "assets"
DATASETS_DIR = ROOT / "datasets"
DB_PATH = ROOT / "db" / "results.db"
LEGACY_CONFIG_PATH = ROOT / "gpt3_config.yml"

load_dotenv(ROOT / ".env")

DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
REASONING_PREFIXES = ("o1", "o3", "o4", "gpt-5")
MODELS = list(dict.fromkeys([DEFAULT_MODEL, "gpt-4o-mini", "gpt-4o", "gpt-4.1-mini", "gpt-4.1"]))


def is_reasoning(model: str) -> bool:
    """Reasoning models reject sampling params (temperature, top_p, penalties)."""
    return model.startswith(REASONING_PREFIXES)


def dataset_files() -> dict[str, Path]:
    """Map a human-readable name ("Hindi Translation") to each YAML file in datasets/."""
    files = sorted([*DATASETS_DIR.glob("*.yml"), *DATASETS_DIR.glob("*.yaml")])
    return {f.stem.replace("_", " ").title(): f for f in files}


def load_dataset(path: Path) -> dict:
    with open(path, encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def api_key(session_key: str | None = None) -> str | None:
    """Key from the sidebar, then OPENAI_API_KEY / .env, then gpt3_config.yml."""
    if session_key:
        return session_key
    if key := os.getenv("OPENAI_API_KEY"):
        return key
    if LEGACY_CONFIG_PATH.exists():
        with open(LEGACY_CONFIG_PATH, encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
        return data.get("GPT3_API") if isinstance(data, dict) else None
    return None
