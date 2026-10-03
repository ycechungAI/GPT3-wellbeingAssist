from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

import config
import db
import llm
import sidebar
from conftest import FakeClient

APP = Path(__file__).resolve().parents[1] / "app"
LAB = str(APP / "Home.py")
RESULTS = str(APP / "pages" / "1_Results.py")
CHECKIN = str(APP / "pages" / "2_Check-in.py")


def app(path: str) -> AppTest:
    return AppTest.from_file(path, default_timeout=30).run()


def chat(at: AppTest) -> list[str]:
    return [m.markdown[0].value for m in at.chat_message]


# --- Lab ------------------------------------------------------------------


def test_lab_compares_models_and_saves_each(monkeypatch):
    fake = FakeClient("Hello")
    monkeypatch.setattr(sidebar, "OpenAI", lambda **kwargs: fake)
    at = app(LAB)
    assert not at.exception
    at.sidebar.multiselect[0].set_value(config.FREE_MODELS).run()
    at.text_area[0].set_value("नमस्ते").run()
    at.button[0].click().run()
    assert not at.exception
    assert [s.value for s in at.success] == ["Hello", "Hello"]
    assert [c["model"] for c in fake.calls] == config.FREE_MODELS
    rows = db.load_results()
    assert len(rows) == 2 and {r["experiment_name"] for r in rows} == {"default-exp"}


def test_lab_one_model_failing_does_not_block_others(monkeypatch):
    fake = FakeClient("Hello")
    real_create = fake.chat.completions.create

    def create(**kwargs):
        if kwargs["model"] == config.FREE_MODELS[0]:
            raise RuntimeError('{"routing_funnel": "raw"}')
        return real_create(**kwargs)

    fake.chat.completions.create = create
    monkeypatch.setattr(sidebar, "OpenAI", lambda **kwargs: fake)
    at = app(LAB)
    at.sidebar.multiselect[0].set_value(config.FREE_MODELS).run()
    at.text_area[0].set_value("hi").run()
    at.button[0].click().run()
    assert not at.exception
    assert "Something went wrong" in at.error[0].value and "routing_funnel" not in at.error[0].value
    assert [s.value for s in at.success] == ["Hello"]
    assert len(db.load_results()) == 1


def test_lab_refuses_non_free_model(monkeypatch):
    monkeypatch.setattr(config, "MODELS", [*config.MODELS, "openai/gpt-4o"])
    at = app(LAB)
    at.sidebar.multiselect[0].set_value(["openai/gpt-4o"]).run()
    assert "Not free models" in at.error[0].value
    assert not at.button


@pytest.mark.parametrize("content", [b"- a\n- list\n", b"dataset: [1, 2]\n", b"key: [unclosed\n"])
def test_lab_rejects_bad_upload(content):
    at = app(LAB)
    at.radio[0].set_value("Upload own").run()
    at.file_uploader[0].set_value(("bad.yml", content, "application/x-yaml")).run()
    assert not at.exception and at.error


# --- Results --------------------------------------------------------------


def test_results_summarizes_per_model():
    at = app(RESULTS)
    assert not at.exception and at.info
    assert not config.DB_PATH.exists()

    for i, (model, secs) in enumerate([("a:free", 1.0), ("a:free", 3.0), ("b:free", 2.0)]):
        db.save_result(
            result_id=f"r{i}",
            experiment_name="exp",
            api_params={"model": model},
            response_time=secs,
            outputs=["x"],
        )
    at = app(RESULTS)
    assert not at.exception
    summary = at.dataframe[0].value
    assert summary["model"].tolist() == ["a:free", "b:free"]
    assert summary["runs"].tolist() == [2, 1]
    assert summary["median latency (s)"].tolist() == [2.0, 2.0]
    assert sorted(at.dataframe[1].value["model"].tolist()) == ["a:free", "a:free", "b:free"]


# --- Check-in -------------------------------------------------------------


@pytest.fixture
def checkin(monkeypatch):
    def start(**fakes):
        for name, fake in fakes.items():
            monkeypatch.setattr(llm, name, fake)
        return app(CHECKIN)

    return start


def test_checkin_greets_and_needs_key(checkin, monkeypatch):
    at = checkin()
    assert not at.exception and chat(at) == ["Hello! How is your wellbeing today?"]
    monkeypatch.delenv("OPENROUTER_API_KEY")
    at = checkin()
    assert at.warning and not at.chat_input


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


def test_checkin_well_and_errors(checkin):
    at = checkin(is_unwell=lambda c, t: False)
    at.chat_input[0].set_value("I feel great").run()
    assert chat(at)[-1].startswith("I am happy to hear that")

    def boom(c, t):
        raise RuntimeError("raw")

    at = checkin(is_unwell=boom)
    at.chat_input[0].set_value("hi").run()
    assert not at.exception
    assert chat(at)[-1] == "Sorry: Something went wrong talking to the model. Please try again."


def test_lab_turns_reasoning_off_by_default(monkeypatch):
    fake = FakeClient("Hello")
    monkeypatch.setattr(sidebar, "OpenAI", lambda **kwargs: fake)
    at = app(LAB)
    at.text_area[0].set_value("hi").run()
    at.button[0].click().run()
    assert fake.calls[-1]["extra_body"] == {"reasoning": {"enabled": False}}

    at.sidebar.toggle[0].set_value(True).run()
    at.button[0].click().run()
    assert fake.calls[-1]["extra_body"] == {}


def test_lab_empty_answer_is_not_saved(monkeypatch):
    fake = FakeClient("")
    monkeypatch.setattr(sidebar, "OpenAI", lambda **kwargs: fake)
    at = app(LAB)
    at.text_area[0].set_value("hi").run()
    at.button[0].click().run()
    assert not at.exception
    assert "Empty answer" in at.warning[0].value
    assert not at.success and db.load_results() == []
