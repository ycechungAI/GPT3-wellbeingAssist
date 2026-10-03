from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

import llm

UI = str(Path(__file__).resolve().parents[1] / "ui.py")


def chat(at: AppTest) -> list[str]:
    return [m.markdown[0].value for m in at.chat_message]


@pytest.fixture
def checkin(monkeypatch):
    def start(**fakes):
        for name, fake in fakes.items():
            monkeypatch.setattr(llm, name, fake)
        return AppTest.from_file(UI, default_timeout=30).run()

    return start


def test_greets(checkin):
    at = checkin()
    assert not at.exception
    assert chat(at) == ["Hello! How is your wellbeing today?"]


def test_needs_api_key(checkin, monkeypatch):
    monkeypatch.delenv("OPENROUTER_API_KEY")
    at = checkin()
    assert at.warning and not at.chat_input
    at.sidebar.text_input[0].input("sk-or-typed").run()
    assert not at.warning and at.chat_input


def test_patient_is_well(checkin):
    at = checkin(is_unwell=lambda c, t: False)
    at.chat_input[0].set_value("I feel great").run()
    assert chat(at)[-1].startswith("I am happy to hear that")
    assert not at.chat_input


def test_follow_up_and_symptoms(checkin):
    answers = iter([False, True])
    extracted = []
    at = checkin(
        is_unwell=lambda c, t: True,
        next_question=lambda c, t: "Do you have a fever?",
        answered_question=lambda c, q, a: next(answers),
        extract_symptoms=lambda c, t: (
            extracted.append(t) or [{"symptom": "Fever", "when": "Today"}]
        ),
    )
    at.chat_input[0].set_value("I have a cough").run()
    assert chat(at)[-1] == "Do you have a fever?"

    at.chat_input[0].set_value("my dog is cute").run()
    assert chat(at)[-1].startswith("Sorry, I didn't quite get that.")

    at.chat_input[0].set_value("Yes, since this morning").run()
    assert at.table[0].value.iloc[0].tolist() == ["Fever", "Today"]
    assert extracted == ["I have a cough\nYes, since this morning"]
    assert not at.chat_input


def test_new_checkin_resets(checkin):
    at = checkin(is_unwell=lambda c, t: False)
    at.chat_input[0].set_value("fine").run()
    at.sidebar.button[0].click().run()
    assert chat(at) == ["Hello! How is your wellbeing today?"] and at.chat_input


def test_shows_api_errors(checkin):
    def boom(c, t):
        raise RuntimeError("rate limited")

    at = checkin(is_unwell=boom)
    at.chat_input[0].set_value("hi").run()
    assert not at.exception
    assert chat(at)[-1] == "Sorry: Something went wrong talking to the model. Please try again."
