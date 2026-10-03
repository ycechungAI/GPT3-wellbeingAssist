"""The four assistant decisions, each one Chat Completions call (via OpenRouter)."""

import json

from openai import OpenAI

import prompts
from config import DEFAULT_MODEL, is_free


def _ask(client: OpenAI, system: str, user: str, model: str, **kwargs) -> str:
    if not is_free(model):
        raise ValueError(f"{model!r} is not a free model; use 'openrouter/free' or a ':free' id")
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
        temperature=0,
        **kwargs,
    )
    return (response.choices[0].message.content or "").strip()


def _is_yes(text: str) -> bool:
    return text.strip(" *_`\"'").lower().startswith("yes")


def is_unwell(client: OpenAI, text: str, model: str = DEFAULT_MODEL) -> bool:
    """Is the patient feeling unwell?"""
    return _is_yes(_ask(client, prompts.IS_UNWELL, text, model))


def answered_question(
    client: OpenAI, question: str, answer: str, model: str = DEFAULT_MODEL
) -> bool:
    """Did the patient's answer respond to the question?"""
    user = f"Q: {question} A: {answer}"
    return _is_yes(_ask(client, prompts.ANSWERED_QUESTION, user, model))


def next_question(client: OpenAI, text: str, model: str = DEFAULT_MODEL) -> str:
    """Which follow-up question should we ask about these symptoms?"""
    return _ask(client, prompts.NEXT_QUESTION, text, model)


def extract_symptoms(client: OpenAI, text: str, model: str = DEFAULT_MODEL) -> list[dict]:
    """Which symptoms did the patient mention, and when? -> [{"symptom", "when"}]"""
    raw = _ask(
        client,
        prompts.EXTRACT_SYMPTOMS,
        text,
        model,
        response_format={"type": "json_object"},
    )
    # Free models sometimes wrap the JSON in prose or a ```json fence.
    try:
        items = json.loads(raw[raw.find("{") : raw.rfind("}") + 1]).get("symptoms", [])
    except (json.JSONDecodeError, AttributeError):
        return []
    return [
        {"symptom": str(i.get("symptom", "")).strip(), "when": str(i.get("when", "Unknown"))}
        for i in items
        if isinstance(i, dict) and i.get("symptom")
    ]
