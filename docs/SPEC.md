# Spec: experiment1, a prompt experiment lab

Status: implemented on `fix/experiment1-modernize` (based on `experiment1`), 2026-10-03.

## 1. Goal

`experiment1` is the experimentation direction of GPT3-wellbeingAssist, kept as its own
project. You pick a few-shot dataset, such as Chinese → English summarization or Hindi →
English translation, write a prompt, and run it against one or more **free** models side by
side. Each run is saved, and a Results page compares models by output and latency. The
patient check-in chat stays as a demo page.

It must install and run with one command on a current Python, using free OpenRouter models
only.

## 2. What is broken

- E1. **No entry point.** `scripts.py` and the README launch `app/home.py`, which doesn't
  exist. `app/ui.py` and `pages/experimentation.py` only define functions and never call them,
  so every page renders blank.
- E2. **No working install.** Poetry targets Python ^3.6, `streamlit ^0.65`, and
  `openai ^0.2.4`. `scripts.py` mixes tabs and spaces (an IndentationError) and does
  `str / str` path math. `run.sh` has the shebang `#!bin/sh`.
- E3. **Dead model API.** `openai.Completion.create`, `openai.openai_object`, and the
  `davinci`/`curie`/`codex` engines are all gone.
- E4. **Streamlit APIs removed.** `st.cache` no longer exists. `use_column_width` is
  deprecated.
- E5. **`results.py` doesn't parse.** It has mixed indentation, nested quotes in an
  f-string, and imports of `pathlab`, `app.app_config`, and `openai.openai_objects`, none of
  which exist. It is a broken copy of the experiment page.
- E6. **DB:** the Alembic migration uses a Postgres-only default, so it fails on SQLite.
  The experiment page also connects to `app/db/` instead of `db/`.
- E7. **Chat:** state is kept in `state.npy`/`storage.txt` on disk, errors are hidden by bare
  `except`, symptoms from the first message are dropped, and three duplicate copies of the
  prompt functions exist.
- E8. **Hygiene:** `.DS_Store`, runtime files, and an empty `results.db` are committed.

## 3. Design

```
app/
  Home.py                 # entry: the experiment lab (the home.py scripts.py intended)
  pages/1_Results.py      # compare saved runs; per-model summary
  pages/2_Check-in.py     # patient check-in chat (demo)
  config.py  llm.py  prompts.py  db.py  sidebar.py   # shared, from the fixed working1 line
datasets/*.yml            # unchanged
tests/
pyproject.toml  uv.lock  run.sh  .env.example
```

- D1. **Tooling:** `uv` and PEP 621 on Python 3.12+. Dependencies: `streamlit`, `openai`
  (used as the OpenRouter client), `python-dotenv`, and `pyyaml`. Poetry, Alembic,
  `scripts.py`, and loguru are removed.
- D2. **Models:** OpenRouter, free models only. The default is `qwen/qwen3.8-27b:free`, with
  `apodex/apodex-1.1-mini:free` as a fallback; `OPENROUTER_MODEL` overrides it. Anything other
  than `openrouter/free` or a `:free` id is refused before a request is sent.
- D3. **Lab (`Home.py`):**
  - Choose a dataset (an example, or upload YAML, which is validated) and one or more models.
  - Set max tokens and temperature, then run.
  - Each model runs one after another (free models are rate-limited) and gets its own column
    showing its output, latency, or a short error.
  - Every successful run is saved with its model in `api_params`.
  - Experiments allow 300 seconds per request, since long generations are expected.
- D4. **Results:** a table of runs filtered by experiment. A per-model summary shows run
  count and median latency. CSV download comes from the table's own toolbar.
- D5. **Check-in:** the same flow as the fixed chat. State lives in `st.session_state`; the
  follow-up question is re-asked if not answered; the symptom table includes the first
  complaint; errors are short.
- D6. **DB:** one SQLite table, `gpt3_results` (same columns as the old migration), created
  on first write. Reading never creates the file.
- D7. **Tests:** fake model client for `llm.py`; the real SDK against a local fake server;
  `AppTest` for every page, including multi-model runs and errors. No key or network needed.

## 4. Work breakdown

1. Hygiene: remove Poetry, Alembic, `scripts.py`, `.bak`, the duplicates, runtime files, and
   the conda env (E2, E6, E8).
2. Packaging: `pyproject.toml`, `uv.lock`, `run.sh`, `.env.example` (E2).
3. Shared modules: config, llm, prompts, db, sidebar (E3, E4, E6, E7).
4. Pages: `Home.py` (lab), Results, Check-in (E1, E5, E7).
5. Tests, then the README.

## 5. Acceptance criteria

- `uv sync && uv run pytest` passes with no key and no network. `ruff check` is clean.
- `./run.sh` serves the app from any directory, and all three pages load.
- With an OpenRouter key, comparing two free models on a dataset shows both outputs with
  latencies, saves two runs, and Results summarizes them per model.
