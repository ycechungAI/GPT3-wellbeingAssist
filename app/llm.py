"""The four assistant decisions, each one Chat Completions call (via OpenRouter)."""

import json

import openai
from openai import OpenAI

import prompts
from config import DEFAULT_MODEL, FREE_MODELS, NO_REASONING, is_free


def _create(client: OpenAI, model: str, models: list[str], messages, reasoning_off, **kwargs):
    return client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0,
        # OpenRouter also falls back by itself if a model is unavailable.
        extra_body={"models": models, **(NO_REASONING if reasoning_off else {})},
        **kwargs,
    )


def _ask(client: OpenAI, system: str, user: str, model: str, **kwargs) -> str:
    if not is_free(model):
        raise ValueError(f"{model!r} is not a free model; use 'openrouter/free' or a ':free' id")
    messages = [{"role": "system", "content": system}, {"role": "user", "content": user}]
    order = [model, *(m for m in FREE_MODELS if m != model)]
    for i, current in enumerate(order):
        try:
            try:
                response = _create(client, current, order[i:], messages, True, **kwargs)
            except openai.BadRequestError:
                # Some models can't turn reasoning off; use their default instead.
                response = _create(client, current, order[i:], messages, False, **kwargs)
        except openai.APITimeoutError:
            if current == order[-1]:
                raise
            continue  # too slow: try the next free model
        return (response.choices[0].message.content or "").strip()


def friendly_error(err: Exception) -> str:
    """Short, user-facing text for an API failure (details go to the server log)."""
    if isinstance(err, openai.APITimeoutError):
        return "The free models are slow right now. Please try again."
    if isinstance(err, openai.RateLimitError):
        return "The free model is busy (rate limit). Please wait a minute and try again."
    if isinstance(err, openai.AuthenticationError):
        return "The OpenRouter API key was rejected. Check it in the sidebar or .env."
    if isinstance(err, ValueError):
        return str(err)
    return "Something went wrong talking to the model. Please try again."


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
        {"symptom": str(i["symptom"]).strip(), "when": str(i.get("when") or "Unknown").strip()}
        for i in items
        if isinstance(i, dict) and i.get("symptom")
    ]
