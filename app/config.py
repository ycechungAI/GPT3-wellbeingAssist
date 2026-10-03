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
# Free models only. "openrouter/free" routes to whichever free model is available, so it keeps
# working as individual free models come and go; the others are pinned alternatives.
FREE_ROUTER = "openrouter/free"
DEFAULT_MODEL = os.getenv("OPENROUTER_MODEL", FREE_ROUTER)
MODELS = list(
    dict.fromkeys(
        [
            DEFAULT_MODEL,
            FREE_ROUTER,
            "google/gemma-4-31b-it:free",
            "nvidia/nemotron-3-super-120b-a12b:free",
        ]
    )
)


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
