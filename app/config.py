"""Paths, model choices, dataset discovery and API-key lookup shared by every page."""

import os
from pathlib import Path

import yaml
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
ASSETS_DIR = ROOT / "assets"
DATASETS_DIR = ROOT / "datasets"
DB_PATH = ROOT / "db" / "results.db"

load_dotenv(ROOT / ".env")

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
# Free models only. Measured 2026-10-03 as fast and accurate on the check-in prompts; the
# second is the fallback. "openrouter/free" picks a random free model and can land on slow ones.
FREE_ROUTER = "openrouter/free"
FREE_MODELS = ["qwen/qwen3.8-27b:free", "apodex/apodex-1.1-mini:free"]
DEFAULT_MODEL = os.getenv("OPENROUTER_MODEL", FREE_MODELS[0])
MODELS = list(dict.fromkeys([DEFAULT_MODEL, *FREE_MODELS, FREE_ROUTER]))
# Free models can stall. Give each model this long, then move on to the next free model,
# rather than waiting out the SDK's 10-minute default.
TIMEOUT_SECONDS = 45
# OpenRouter's unified switch. Reasoning models can otherwise spend the whole token budget
# thinking and return an empty answer; models without reasoning ignore it.
NO_REASONING = {"reasoning": {"enabled": False}}


def is_free(model: str) -> bool:
    return model == FREE_ROUTER or model.endswith(":free")


def dataset_files() -> dict[str, Path]:
    """Map a human-readable name ("Hindi Translation") to each YAML file in datasets/."""
    files = sorted([*DATASETS_DIR.glob("*.yml"), *DATASETS_DIR.glob("*.yaml")])
    return {f.stem.replace("_", " ").title(): f for f in files}


def load_dataset(path: Path) -> dict:
    with open(path, encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def api_key(session_key: str | None = None) -> str | None:
    """Key from the sidebar, then OPENROUTER_API_KEY (environment or .env)."""
    return session_key or os.getenv("OPENROUTER_API_KEY") or None
