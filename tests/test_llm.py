import llm
from conftest import FakeClient


def test_is_unwell_parses_yes_and_no():
    assert llm.is_unwell(FakeClient("Yes"), "I have a fever") is True
    assert llm.is_unwell(FakeClient("No."), "I feel great") is False


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


def test_extract_symptoms_tolerates_bad_json():
    assert llm.extract_symptoms(FakeClient("not json"), "x") == []
    assert llm.extract_symptoms(FakeClient('{"symptoms": ["bad", {}]}'), "x") == []
