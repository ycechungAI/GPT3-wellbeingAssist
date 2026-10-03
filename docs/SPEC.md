# Spec: Fix and modernize the `main` prototype

Status: implemented on `fix/main-modernize` (based on `main`), 2026-10-03.

## 1. Goal

`main` is the original single-page prototype of the wellbeing check-in. It is its own project:
a flat layout, one Streamlit page, and no database. A patient says how they feel. If they are
unwell, the assistant asks one follow-up question and turns the answers into a symptom table.

Keep that scope. Make it install and run with one command on a current Python, using free
OpenRouter models only.

## 2. What is broken

- M1. **No working install.** The only setup is a conda file pinned to Python 3.8 and
  `openai==0.6.3`. `streamlit`, `numpy`, `fpdf`, and `requests` are imported but never declared.
- M2. **Every model call fails.** The code uses the pre-1.0 `openai.Completion.create` and
  the `davinci` engine. The current SDK removed that API, and the engine is retired.
- M3. **The README describes a Flask app that doesn't exist.** `backend_functions.py`
  defines no Flask app, so `flask run` cannot work.
- M4. **Duplicated and unsafe code.** `backend_functions.py` duplicates `prompts.py`.
  `logic1.py` makes a paid API call when it is imported. `patient_answered_question` drops its
  input, and the prompt never includes it.
- M5. **Chat state lives on disk.** `ui.py` keeps the conversation in `state.npy` and
  `storage.txt`. That state is shared by every user, depends on the working directory, and
  hides all errors behind bare `except: pass`. The page also uses `use_column_width`, which
  Streamlit has deprecated.
- M6. **Symptoms from the first message are lost.** Extraction sees only the follow-up
  answer. Its output is raw table text, never parsed.
- M7. **Repo hygiene.** `.DS_Store` and `__pycache__/*.pyc` are committed, and there is no
  `.gitignore`. Nothing protects a `.env` holding a key from being committed.

## 3. Design

```
ui.py            # the one Streamlit page: check-in chat
llm.py           # OpenRouter client + the 4 assistant decisions
prompts.py       # prompt text only
ai-bot.jpg       # unchanged
tests/           # pytest; the model API is always faked
pyproject.toml   # PEP 621, managed by uv; uv.lock
run.sh           # uv run streamlit run ui.py (works from any directory)
.env.example     # OPENROUTER_API_KEY=
```

- D1. **Tooling:** `uv` with Python 3.12 or later. Dependencies are `streamlit`, `openai`
  (used as the OpenRouter client), and `python-dotenv`. For dev: `pytest` and `ruff`.
- D2. **Model API:** OpenRouter at `https://openrouter.ai/api/v1`, free models only. The
  default model is `qwen/qwen3.8-27b:free`, with `apodex/apodex-1.1-mini:free` as an
  OpenRouter fallback (the `models` list). Both were measured as fast and accurate on these
  prompts. The `openrouter/free` router was rejected because it can land on slow models.
  `OPENROUTER_MODEL` can pin any `:free` id; any other model is refused before a request is
  sent. Requests time out after 60 seconds with one retry, so a stalled free model shows an
  error and the page doesn't hang.
- D3. **Key:** read from the sidebar first, then from `OPENROUTER_API_KEY` in the environment
  or `.env`. `.env` is gitignored.
- D4. **Check-in flow:** state lives in `st.session_state`, using `st.chat_message` and
  `st.chat_input`.
  1. `greet`: the assistant asks how the patient is.
  2. `is_unwell`: if no, say goodbye and finish. If yes, `next_question` → `follow_up`.
  3. `answered_question`: if no, repeat the question. If yes, `extract_symptoms` over the
     first message plus the answer, show the table, and finish.
  4. API errors appear in the chat and never crash the page. A "New check-in" button resets
     the conversation.
- D5. **No Flask:** remove the Flask instructions. This project is Streamlit only.
- D6. **Tests:** cover `llm.py` with a fake client. Run the real SDK against a local fake
  server. Use `AppTest` for every path through the page.

## 4. Work breakdown

1. Hygiene: delete `.DS_Store`, `__pycache__/`, `backend_functions.py`, `logic1.py`, and
   `environment_droplet.yml`. Add a `.gitignore` (M3, M4, M7).
2. Packaging: `pyproject.toml`, `uv.lock`, `run.sh`, `.env.example` (M1).
3. `prompts.py` and `llm.py` (M2, M4, M6).
4. `ui.py` (M5, M6).
5. Tests, then the README.

## 5. Acceptance criteria

- `uv sync && uv run pytest` passes with no key and no network.
- `uv run ruff check .` is clean.
- `./run.sh` serves the page from any directory. With no key, it asks for one and does not
  crash.
- With an OpenRouter key, a full check-in on a free model ends in a symptom table that
  includes the first complaint.
