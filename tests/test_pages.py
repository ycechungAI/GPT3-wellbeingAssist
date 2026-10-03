from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

import config
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
    monkeypatch.delenv("OPENROUTER_API_KEY")
    at = checkin()
    assert at.warning and not at.chat_input


def test_checkin_patient_is_well(checkin):
    at = checkin(is_unwell=lambda c, t: False)
    at.chat_input[0].set_value("I feel great").run()
    assert chat(at)[-1].startswith("I am happy to hear that")
    assert not at.chat_input


def test_checkin_follow_up_and_symptoms(checkin):
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


def test_checkin_shows_api_errors(checkin):
    def boom(c, t):
        raise RuntimeError("rate limited")

    at = checkin(is_unwell=boom)
    at.chat_input[0].set_value("hi").run()
    assert not at.exception
    assert chat(at)[-1] == "Sorry: Something went wrong talking to the model. Please try again."


def test_experimentation_submits_and_saves(monkeypatch):
    monkeypatch.setattr(sidebar, "OpenAI", lambda **kwargs: FakeClient("Hello"))
    at = AppTest.from_file(str(APP / "pages" / "1_Experimentation.py"), default_timeout=30).run()
    assert not at.exception
    at.text_area[0].set_value("नमस्ते").run()
    at.button[0].click().run()
    assert not at.exception
    assert at.success[0].value == "Hello"
    [row] = db.load_results()
    assert row["experiment_name"] == "default-exp"


def test_api_key_survives_page_switch(monkeypatch):
    monkeypatch.delenv("OPENROUTER_API_KEY")
    at = AppTest.from_file(str(APP / "Home.py"), default_timeout=30).run()
    at.sidebar.text_input[0].input("sk-typed").run()
    assert at.session_state.api_key == "sk-typed" and at.chat_input
    at.switch_page("pages/1_Experimentation.py").run()
    assert not at.exception
    assert at.sidebar.text_input[0].value == "sk-typed" and not at.warning


@pytest.mark.parametrize("content", [b"- a\n- list\n", b"dataset: [1, 2]\n", b"key: [unclosed\n"])
def test_experimentation_rejects_bad_upload(content):
    at = AppTest.from_file(str(APP / "pages" / "1_Experimentation.py"), default_timeout=30).run()
    at.radio[0].set_value("Upload own").run()
    at.file_uploader[0].set_value(("bad.yml", content, "application/x-yaml")).run()
    assert not at.exception
    assert at.error


def test_results_page_lists_runs():
    at = AppTest.from_file(str(APP / "pages" / "2_Results.py"), default_timeout=30).run()
    assert not at.exception and at.info
    assert not config.DB_PATH.exists()

    db.save_result(
        result_id="r1", experiment_name="exp", api_params={}, response_time=1, outputs=["x"]
    )
    at = AppTest.from_file(str(APP / "pages" / "2_Results.py"), default_timeout=30).run()
    assert not at.exception
    assert at.dataframe[0].value["result_id"].tolist() == ["r1"]
