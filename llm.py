"""OpenRouter client setup and the four assistant decisions (free models only)."""

import json
import os
from pathlib import Path

import openai
from dotenv import load_dotenv
from openai import OpenAI

import prompts

load_dotenv(Path(__file__).resolve().parent / ".env")

BASE_URL = "https://openrouter.ai/api/v1"
FREE_ROUTER = "openrouter/free"  # routes to a random free model; can land on slow ones
# Measured 2026-10-03: fast and accurate on the check-in prompts. The second is a fallback
# OpenRouter tries automatically if the first is unavailable.
FREE_MODELS = ["qwen/qwen3.8-27b:free", "apodex/apodex-1.1-mini:free"]
MODEL = os.getenv("OPENROUTER_MODEL", FREE_MODELS[0])
# Free models can stall. Give each model this long, then move on to the next free model,
# rather than waiting out the SDK's 10-minute default.
TIMEOUT_SECONDS = 45


def is_free(model: str) -> bool:
    return model == FREE_ROUTER or model.endswith(":free")


def api_key(entered: str | None = None) -> str | None:
    """Key typed in the sidebar, then OPENROUTER_API_KEY (environment or .env)."""
    return entered or os.getenv("OPENROUTER_API_KEY") or None


def client(key: str) -> OpenAI:
    return OpenAI(api_key=key, base_url=BASE_URL, timeout=TIMEOUT_SECONDS, max_retries=0)


def _ask(client: OpenAI, system: str, user: str, model: str, **kwargs) -> str:
    if not is_free(model):
        raise ValueError(f"{model!r} is not a free model; use 'openrouter/free' or a ':free' id")
    order = [model, *(m for m in FREE_MODELS if m != model)]
    for i, current in enumerate(order):
        try:
            response = client.chat.completions.create(
                model=current,
                messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
                temperature=0,
                # OpenRouter also falls back by itself if a model is unavailable.
                extra_body={"models": order[i:]},
                **kwargs,
            )
        except openai.APITimeoutError:
            if current == order[-1]:
                raise
            continue  # too slow: try the next free model
        return (response.choices[0].message.content or "").strip()


def friendly_error(err: Exception) -> str:
    """Short, patient-facing text for an API failure (details go to the server log)."""
    if isinstance(err, openai.APITimeoutError):
        return "The free models are slow right now. Please send your message again."
    if isinstance(err, openai.RateLimitError):
        return "The free model is busy (rate limit). Please wait a minute and try again."
    if isinstance(err, openai.AuthenticationError):
        return "The OpenRouter API key was rejected. Check it in the sidebar or .env."
    if isinstance(err, ValueError):
        return str(err)
    return "Something went wrong talking to the model. Please try again."


def _is_yes(text: str) -> bool:
    return text.strip(" *_`\"'").lower().startswith("yes")


def is_unwell(client: OpenAI, text: str, model: str = MODEL) -> bool:
    """Is the patient feeling unwell?"""
    return _is_yes(_ask(client, prompts.IS_UNWELL, text, model))


def answered_question(client: OpenAI, question: str, answer: str, model: str = MODEL) -> bool:
    """Did the patient's answer respond to the question?"""
    return _is_yes(_ask(client, prompts.ANSWERED_QUESTION, f"Q: {question} A: {answer}", model))


def next_question(client: OpenAI, text: str, model: str = MODEL) -> str:
    """Which follow-up question should we ask about these symptoms?"""
    return _ask(client, prompts.NEXT_QUESTION, text, model)


def extract_symptoms(client: OpenAI, text: str, model: str = MODEL) -> list[dict]:
    """Which symptoms did the patient mention, and when? -> [{"symptom", "when"}]"""
    raw = _ask(
        client, prompts.EXTRACT_SYMPTOMS, text, model, response_format={"type": "json_object"}
    )
    # Free models sometimes wrap the JSON in prose or a ```json fence.
    try:
        items = json.loads(raw[raw.find("{") : raw.rfind("}") + 1]).get("symptoms", [])
    except (json.JSONDecodeError, AttributeError):
        return []
    return [
        {"symptom": str(i["symptom"]).strip(), "when": str(i.get("when") or "Unknown").strip()}
        for i in items
        if isinstance(i, dict) and i.get("symptom")
    ]
