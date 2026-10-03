# GPT3-wellbeingAssist: prototype

The original single-page prototype of a check-in assistant for clinical trials. It gathers
information about a patient's health between doctor's visits and puts it into a structured
format, so trials run better and patients are looked after.

Given the patient's answer, the assistant decides:

- Is the patient unwell?
- Did they answer the question?
- What should we ask more specifically about?
- Which symptoms do they have, and when did those symptoms occur? (structured as a table)

Open issue: the legal aspects of handling patient data.

## Quick start

1. Install [uv](https://docs.astral.sh/uv/getting-started/installation/):

   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. Install dependencies (uv fetches Python 3.12+ if needed):

   ```bash
   uv sync
   ```

3. Add an [OpenRouter API key](https://openrouter.ai/keys). Run `cp .env.example .env`,
   then fill in `OPENROUTER_API_KEY=`, or paste the key into the app's sidebar. `.env` is
   gitignored.

   The app uses **free models only**, so no credits are spent. The default model is
   `qwen/qwen3.8-27b:free`, and `apodex/apodex-1.1-mini:free` is an automatic fallback. Both
   were picked for speed. To use another free model, set `OPENROUTER_MODEL` to its `:free`
   id. Free models have rate limits. A model that takes over 45 seconds is skipped for the
   fallback. Either way, the chat shows a short error message.

   Some free models only work if you allow them in your
   [OpenRouter privacy settings](https://openrouter.ai/settings/privacy). The defaults don't
   need that.

4. Run the app, then open http://localhost:8501:

   ```bash
   ./run.sh
   ```

## Development

```bash
uv run pytest
```

```bash
uv run ruff check .
```

The tests fake the model API, so they need no API key or network connection. The changes
behind this version are described in [docs/SPEC.md](docs/SPEC.md).
