import pytest

import llm
from conftest import FakeClient


def test_is_unwell_parses_yes_and_no():
    assert llm.is_unwell(FakeClient("Yes"), "I have a fever") is True
    assert llm.is_unwell(FakeClient("No."), "I feel great") is False


def test_is_unwell_tolerates_markdown():
    assert llm.is_unwell(FakeClient("**Yes**"), "x") is True


def test_only_free_models_are_called():
    client = FakeClient("Yes")
    llm.is_unwell(client, "x", model="google/gemma-4-31b-it:free")
    with pytest.raises(ValueError, match="not a free model"):
        llm.is_unwell(client, "x", model="openai/gpt-4o-mini")
    assert [c["model"] for c in client.calls] == ["google/gemma-4-31b-it:free"]


def test_requests_carry_free_fallbacks():
    client = FakeClient("Yes")
    llm.is_unwell(client, "x", model=llm.FREE_MODELS[0])
    assert client.calls[0]["extra_body"]["models"] == llm.FREE_MODELS


def test_answered_question_sends_question_and_answer():
    client = FakeClient("Yes")
    assert llm.answered_question(client, "Do you have a fever?", "Yes, 39C") is True
    assert client.calls[0]["messages"][1]["content"] == "Q: Do you have a fever? A: Yes, 39C"


def test_next_question_returns_text():
    assert llm.next_question(FakeClient("  Do you have a fever?\n"), "cough") == (
        "Do you have a fever?"
    )


def test_extract_symptoms_parses_json():
    client = FakeClient(
        '{"symptoms": [{"symptom": "Headache", "when": "Sunday"}, {"symptom": "Cough"}]}'
    )
    assert llm.extract_symptoms(client, "headache sunday, cough") == [
        {"symptom": "Headache", "when": "Sunday"},
        {"symptom": "Cough", "when": "Unknown"},
    ]
    assert client.calls[0]["response_format"] == {"type": "json_object"}


def test_extract_symptoms_strips_code_fence():
    client = FakeClient(
        'Sure!\n```json\n{"symptoms": [{"symptom": "Cough", "when": "Today"}]}\n```'
    )
    assert llm.extract_symptoms(client, "cough") == [{"symptom": "Cough", "when": "Today"}]


def test_extract_symptoms_tolerates_bad_json():
    assert llm.extract_symptoms(FakeClient("not json"), "x") == []
    assert llm.extract_symptoms(FakeClient('{"symptoms": ["bad", {}]}'), "x") == []


def test_extract_symptoms_null_when_is_unknown():
    client = FakeClient('{"symptoms": [{"symptom": "Knee pain", "when": null}]}')
    assert llm.extract_symptoms(client, "knee") == [{"symptom": "Knee pain", "when": "Unknown"}]


def test_timeout_moves_to_next_free_model():
    import httpx2
    import openai

    calls = []

    def create(**kwargs):
        calls.append(kwargs["model"])
        if len(calls) == 1:
            raise openai.APITimeoutError(request=httpx2.Request("POST", "http://x"))
        return FakeClient("Yes")._create(**kwargs)

    client = FakeClient()
    client.chat.completions.create = create
    assert llm.is_unwell(client, "x", model=llm.FREE_MODELS[0]) is True
    assert calls == llm.FREE_MODELS[:2]


def test_friendly_errors_hide_raw_payloads():
    import openai

    assert "slow" in llm.friendly_error(openai.APITimeoutError(request=None))
    assert llm.friendly_error(RuntimeError('{"routing_funnel": ...}')).startswith("Something")


def test_calls_turn_reasoning_off():
    client = FakeClient("Yes")
    llm.is_unwell(client, "x")
    assert client.calls[0]["extra_body"]["reasoning"] == {"enabled": False}


def test_model_that_cannot_disable_reasoning_is_retried_with_default():
    import httpx2
    import openai

    sent = []

    def create(**kwargs):
        sent.append(kwargs["extra_body"])
        if "reasoning" in kwargs["extra_body"]:
            response = httpx2.Response(400, request=httpx2.Request("POST", "http://x"))
            raise openai.BadRequestError("reasoning is mandatory", response=response, body=None)
        return FakeClient("Yes")._create(**kwargs)

    client = FakeClient()
    client.chat.completions.create = create
    assert llm.is_unwell(client, "x") is True
    assert ["reasoning" in body for body in sent] == [True, False]
