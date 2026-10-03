# Spec: Fix and modernize GPT3-wellbeingAssist

Status: implemented on `fix/modernize-app` (based on `working1`), 2026-10-03.

## 1. Goal

A patient opens the app and checks in. The assistant asks how they feel and decides whether
they are unwell. If they are, it asks a targeted follow-up question and turns the answer into
a structured symptom table. A second page lets a developer test prompts against the model and
save the results. A third page shows the saved results.

All of this should run with one command on a current Python, without any manual edits.

## 2. Branch audit

| Branch | What it was | Outcome |
|---|---|---|
| `working1` (default) | The current app | Fixed here (this spec) |
| `main` | The first prototype of the same app (flat layout) | Archived as tag `archive/main`, branch deleted |
| `experiment1` | The same app after the move to `app/`, with old GPT-3 models | Archived as tag `archive/experiment1`, branch deleted |
| `temp` | `experiment1` plus dependency bumps | Archived as tag `archive/temp`, branch deleted |
| `fix/dependabot-errors` | Merged as PR #11 | Stale |
| `dependabot/pip/pip-c4ff2e68b4` (PR #13) | `filelock` bump in `poetry.lock` | Closed by PR #14 (`poetry.lock` replaced by `uv.lock`) |

The archived branches held older snapshots of the same check-in app, each with the bugs below.
They were not fixed separately; `working1` is the one maintained app. To look at one, run
`git checkout archive/main` (or `archive/temp`, `archive/experiment1`).

## 3. What is broken on `working1`

### 3.1 Install and launch
- B1. `pyproject.toml` sets the build backend to `requires = ["poetry==2.2"]`, which is not a
  valid build requirement (it should be `poetry-core`). As a result, `poetry install` fails.
- B2. Dependencies are wrong:
  - Missing but imported: `click`, `numpy`.
  - Listed but unused and heavy: `transformers`, `tokenizers`, `openai-finetune`
    (abandoned), `fpdf`, `requests`.
- B3. `scripts.py` mixes tabs and spaces, which causes an `IndentationError`. Both
  `poetry run st-server` and `poetry run migrate` crash as a result.
- B4. `run.sh` and `app/ui.py` use paths that are relative to the current working directory
  (`../assets`, `storage.txt`, `state.npy`). They work only when you run from `app/`.

### 3.2 Main check-in page (`app/ui.py`)
- B5. `ui()` is defined but never called, so the page renders blank.
- B6. Conversation state is stored in `state.npy` and `storage.txt` on disk. All users share
  this state, it persists between sessions, and the files are committed to git. Bare
  `except: pass` blocks hide every error.
- B7. The page uses `use_column_width`, which Streamlit has deprecated.

### 3.3 OpenAI calls (`prompts.py`, `backend_functions.py`, `backend_functions/`, `logic1.py`)
- B8. The code uses the pre-1.0 SDK (`openai.Completion.create`). The current SDK removed this
  API, so every call raises an error.
- B9. The model `davinci-codex` was retired years ago.
- B10. The same 4 functions exist in 3 copies. `logic1.py` makes a paid API call on import.
- B11. `patient_answered_question` ignores its input, and its prompt never includes the text.
  The code parses the symptom table with brittle string splitting.

### 3.4 Experimentation and results pages
- B12. `experimentation.py` imports `openai.openai_object`, which no longer exists. It also
  uses `st.cache`, which Streamlit removed. It uses `logger` without importing it. The DB path
  points to `app/db/` and not `db/`. The page function is never called. The model list holds
  only legacy completion models.
- B13. `results.py` has syntax errors and mixed indentation, and it imports modules that do
  not exist (`pathlab`, `app.app_config`). It is a broken copy of the experimentation page.
- B14. The stray file `pages/__init.py` shows up as an extra page.

### 3.5 Database
- B15. The Alembic migration uses `now() at time zone 'IST'`, which works only on Postgres.
  On SQLite the migration fails, so `db/results.db` is committed with no table in it.

### 3.6 Repo hygiene
- B16. Runtime and OS files are committed: `.DS_Store`, `app/state.npy`, `app/storage.txt`,
  and `db/results.db`. These patterns are missing from `.gitignore`: `gpt3_config.yml` (which
  holds secrets) and the DB.
- B17. Dead files: `.bak`, `app/environment_droplet.yml` (conda, `openai==0.6.3`), and the
  root `__init__.py`.
- B18. The test depends on the working directory and calls the real API. CI has no test job.
  The dependency-review workflow uses outdated action versions.
- B19. The README is out of date and contradicts itself (it gives two different ports and
  three different setup methods).

## 4. Design

Keep it small. One app folder, plain modules, no framework beyond Streamlit.

```
app/
  Home.py                   # entry point: patient check-in chat
  pages/1_Experimentation.py
  pages/2_Results.py
  config.py                 # paths, model list, dataset discovery, API-key lookup
  llm.py                    # OpenAI client + the 4 assistant functions
  prompts.py                # prompt text only
  db.py                     # sqlite3: init + insert + read
datasets/*.yml              # unchanged
tests/                      # pytest; OpenAI is always mocked
pyproject.toml              # PEP 621, managed by uv
uv.lock
run.sh                      # `uv run streamlit run app/Home.py`
```

Decisions:
- D1. **Tooling:** `uv` with a standard PEP 621 `pyproject.toml`, on Python ≥ 3.12. Running
  `uv sync` installs everything, and `./run.sh` starts the app. This replaces Poetry, its
  broken build backend, and `scripts.py`.
- D2. **Dependencies:** `streamlit`, `openai` (used as the OpenRouter client),
  `python-dotenv`, and `pyyaml`. For dev: `pytest` and `ruff`. Everything else is removed (B2).
- D3. **Model API: OpenRouter, free models only.** Calls go through the `openai` SDK pointed
  at `https://openrouter.ai/api/v1`, using Chat Completions. The default model is
  `openrouter/free`, a router over whichever free models are live, so the app survives
  individual free models being withdrawn. `OPENROUTER_MODEL` can pin a `:free` id. Any model
  that is not `openrouter/free` or `*:free` is refused before a request is sent. OpenRouter
  ignores unsupported parameters, so no per-model parameter handling is needed. Prompts keep
  the original few-shot examples. Symptom extraction requests JSON mode and tolerates
  prose or code fences around the JSON. It returns `list[{"symptom", "when"}]` (B8–B11).
- D4. **API key:** the key entered in the sidebar (kept for the session), then
  `OPENROUTER_API_KEY` from the environment or `.env` (template: `.env.example`).
- D5. **State:** conversation state lives in `st.session_state`. Nothing is written to disk
  for the chat. The page uses `st.chat_message` and `st.chat_input`, and a "New check-in"
  button resets it (B5–B7).
- D6. **Check-in flow (state machine):**
  1. `greet`: the bot asks "How is your wellbeing today?"
  2. Patient answers. `is_unwell(text)` returns no → the bot ends the check-in warmly
     (`done`). Returns yes → the bot calls `next_question(text)` (`follow_up`).
  3. Patient answers. `answered_question(question, answer)` returns no → the bot repeats
     the question. Returns yes → `extract_symptoms(first message + answer)` produces a table → `done`.
  4. API errors appear as an error in the chat and never crash the page or fail silently.
- D7. **DB:** a single `sqlite3` table, `gpt3_results`, created with
  `CREATE TABLE IF NOT EXISTS` on first use. Its columns match the old migration, and
  timestamps use SQLite's `CURRENT_TIMESTAMP`. The DB file path is `db/results.db`, and the
  file is gitignored. Alembic and SQLAlchemy are removed because one table does not need a
  migration framework (B15).
- D8. **Experimentation page:** pick a dataset (or upload YAML) and a free model, set
  max_tokens, temperature and top_p, then enter a prompt. The dataset examples go in as
  few-shot context. Submit, view the outputs and latency, and save to the DB.
- D9. **Results page:** a table of saved runs that you can filter by experiment. CSV download
  comes from the table's own toolbar.
- D10. **Tests:** cover `llm.py` with a fake client; cover `db.py` against a temp DB; and
  run all three pages through `streamlit.testing.v1.AppTest` with `llm` monkeypatched.
  Tests do not need a network connection or an API key.
- D11. **No GitHub CI:** checks run locally (`uv run ruff check . && uv run pytest`), and
  reviews are done by hand, not by a bot. The Actions workflows are removed. `dependabot.yml`
  keeps `uv` dependencies up to date.

## 5. Work breakdown (in order)

1. Repo hygiene: delete dead and runtime files, extend `.gitignore` (B14, B16, B17).
2. Packaging: write the new `pyproject.toml` and `uv.lock`, rewrite `run.sh`, delete
   Poetry, Alembic, and `scripts.py` (B1–B4, B15).
3. Core: `config.py`, `prompts.py`, `llm.py`, `db.py` (B8–B11, B15).
4. Pages: `ui.py` → `Home.py`, `1_Experimentation.py`, `2_Results.py` (B5–B7, B12, B13).
5. Tests; remove GitHub Actions workflows (B18).
6. README (B19).
7. Other branches: archive `main`, `temp`, and `experiment1` as tags, and close PR #13 (§2).

## 6. Acceptance criteria

- `uv sync && uv run pytest` passes on a clean clone with no API key.
- `uv run ruff check` is clean.
- `./run.sh` serves the app from any working directory. All three pages load without
  exceptions.
- With a valid OpenRouter key, the check-in flow completes end to end on a free model and
  shows a symptom table.
- `git status` stays clean after you use the app (no runtime files are tracked).
