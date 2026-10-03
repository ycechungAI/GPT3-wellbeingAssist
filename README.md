# GPT3-wellbeingAssist

A check-in assistant for clinical trials. It gathers information about a patient's health
between doctor's visits and puts it into a structured format, so trials run better and
patients are looked after.

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

3. Add an [OpenRouter API key](https://openrouter.ai/keys) to `.env` in the repo root
   (`cp .env.example .env`, then fill in `OPENROUTER_API_KEY=`), or paste it into the app's
   sidebar. `.env` is gitignored.

   The app uses **free models only**, so no credits are spent. The default model is
   `openrouter/free`, which routes to whichever free model is currently available. To pin a
   specific free model, set `OPENROUTER_MODEL` to its `:free` id. Free models have rate limits;
   if one is hit, the chat shows the error.

4. Run the app, then open http://localhost:8501:

   ```bash
   ./run.sh
   ```

## Pages

- **Home:** the patient check-in chat.
- **Experimentation:** try a few-shot dataset against a model, adjust the sampling
  parameters, and save each run to `db/results.db`.
- **Results:** browse saved runs; download them as CSV from the table toolbar.

## Adding datasets

Add a `*.yml` or `*.yaml` file to `datasets/`. It then appears in the Experimentation
dropdown. For the format, see the existing files: `name`, `language`, `nlp_task`, `input`,
`output`, and a `dataset` map of examples.

## Development

```bash
uv run pytest
```

```bash
uv run ruff check .
```

```bash
uv run ruff format .
```

The tests mock the model API, so they need no API key or network connection. For the change log of
the 2026 modernization, see [docs/SPEC.md](docs/SPEC.md).

If you use this project, please follow and star it.

## Screenshot

<img src="https://i.ibb.co/BCgRdbB/experiment1.png" alt="program running on experimental version" />
