# GPT3-wellbeingAssist: experiment lab

A prompt experiment lab, from the experimentation branch of GPT3-wellbeingAssist. Pick a
few-shot dataset (for example Chinese → English summarization or Hindi → English
translation), write a prompt, and run it against one or more **free** models side by side.
Every run is saved, and the Results page compares models by output and latency.

The patient check-in assistant from the main project is included as a demo page.

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
   `qwen/qwen3.8-27b:free`, and `apodex/apodex-1.1-mini:free` is also offered. To change the
   default, set `OPENROUTER_MODEL` in `.env` to any `:free` id. Some free models only work if
   you allow them in your [OpenRouter privacy settings](https://openrouter.ai/settings/privacy).

4. Run the app, then open http://localhost:8501:

   ```bash
   ./run.sh
   ```

## Pages

- **Home (lab):** choose a dataset and the free models to compare, then run. Each model gets
  its own column with its output and latency, and each successful run is saved to
  `db/results.db`.
- **Results:** a summary per model (number of runs, median latency) and every saved run.
  Download either table as CSV from its toolbar.
- **Check-in:** the patient check-in chat.

## Adding datasets

Add a `*.yml` or `*.yaml` file to `datasets/`. It then appears in the lab's dropdown. For the
format, see the existing files: `name`, `language`, `nlp_task`, `input`, `output`, and a
`dataset` map of examples.

## Development

```bash
uv run pytest
```

```bash
uv run ruff check .
```

The tests fake the model API, so they need no API key or network connection. The changes
behind this version are described in [docs/SPEC.md](docs/SPEC.md).
