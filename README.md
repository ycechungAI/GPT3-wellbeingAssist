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

3. Provide an OpenAI API key, using one of these options:
   - Put `OPENAI_API_KEY=sk-...` in a `.env` file in the repo root.
   - Set the `OPENAI_API_KEY` environment variable.
   - Put `GPT3_API: sk-...` in `gpt3_config.yml`.
   - Paste the key into the sidebar of the running app.

   The default model is `gpt-4o-mini`. To use a different one, set `OPENAI_MODEL`.

4. Run the app, then open http://localhost:8501:

   ```bash
   ./run.sh
   ```

## Pages

- **Home:** the patient check-in chat.
- **Experimentation:** try a few-shot dataset against a model, adjust the sampling
  parameters, and save each run to `db/results.db`.
- **Results:** browse saved runs and download them as CSV.

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

The tests mock OpenAI, so they need no API key or network connection. For the change log of
the 2026 modernization, see [docs/SPEC.md](docs/SPEC.md).

If you use this project, please follow and star it.

## Screenshot

<img src="https://i.ibb.co/BCgRdbB/experiment1.png" alt="program running on experimental version" />
