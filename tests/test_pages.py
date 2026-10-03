from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

import db
import llm
import sidebar
from conftest import FakeClient

APP = Path(__file__).resolve().parents[1] / "app"


def chat(at: AppTest) -> list[str]:
    return [m.markdown[0].value for m in at.chat_message]


@pytest.fixture
def checkin(monkeypatch):
    def start(**fakes):
        for name, fake in fakes.items():
            monkeypatch.setattr(llm, name, fake)
        return AppTest.from_file(str(APP / "Home.py"), default_timeout=30).run()

    return start


def test_checkin_greets(checkin):
    at = checkin()
    assert not at.exception
    assert chat(at) == ["Hello! How is your wellbeing today?"]


def test_checkin_needs_api_key(checkin, monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY")
    at = checkin()
    assert at.warning and not at.chat_input


def test_checkin_patient_is_well(checkin):
    at = checkin(is_unwell=lambda c, t: False)
    at.chat_input[0].set_value("I feel great").run()
    assert chat(at)[-1].startswith("I am happy to hear that")
    assert not at.chat_input


def test_checkin_follow_up_and_symptoms(checkin):
    answers = iter([False, True])
    at = checkin(
        is_unwell=lambda c, t: True,
        next_question=lambda c, t: "Do you have a fever?",
        answered_question=lambda c, q, a: next(answers),
        extract_symptoms=lambda c, t: [{"symptom": "Fever", "when": "Today"}],
    )
    at.chat_input[0].set_value("I have a cough").run()
    assert chat(at)[-1] == "Do you have a fever?"

    at.chat_input[0].set_value("my dog is cute").run()
    assert chat(at)[-1].startswith("Sorry, I didn't quite get that.")

    at.chat_input[0].set_value("Yes, since this morning").run()
    assert at.table[0].value.iloc[0].tolist() == ["Fever", "Today"]
    assert not at.chat_input


def test_checkin_shows_api_errors(checkin):
    def boom(c, t):
        raise RuntimeError("rate limited")

    at = checkin(is_unwell=boom)
    at.chat_input[0].set_value("hi").run()
    assert not at.exception
    assert "rate limited" in chat(at)[-1]


def test_experimentation_submits_and_saves(monkeypatch):
    monkeypatch.setattr(sidebar, "OpenAI", lambda api_key: FakeClient("Hello"))
    at = AppTest.from_file(str(APP / "pages" / "1_Experimentation.py"), default_timeout=30).run()
    assert not at.exception
    at.text_area[0].set_value("नमस्ते").run()
    at.button[0].click().run()
    assert not at.exception
    assert at.success[0].value == "Hello"
    [row] = db.load_results()
    assert row["experiment_name"] == "default-exp"


def test_results_page_lists_runs():
    at = AppTest.from_file(str(APP / "pages" / "2_Results.py"), default_timeout=30).run()
    assert not at.exception and at.info

    db.save_result(
        result_id="r1", experiment_name="exp", api_params={}, response_time=1, outputs=["x"]
    )
    at = AppTest.from_file(str(APP / "pages" / "2_Results.py"), default_timeout=30).run()
    assert not at.exception
    assert at.dataframe[0].value["result_id"].tolist() == ["r1"]
