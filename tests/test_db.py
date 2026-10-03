import json

import db


def test_save_and_load_roundtrip():
    assert db.load_results() == []
    db.save_result(
        result_id="r1",
        experiment_name="exp",
        api_params={"model": "m"},
        response_time=0.5,
        outputs=["नमस्ते", "hi"],
        language="hindi",
    )
    [row] = db.load_results()
    assert row["result_id"] == "r1"
    assert json.loads(row["api_params"]) == {"model": "m"}
    assert json.loads(row["output_response"]) == ["नमस्ते", "hi"]
    assert row["created_at"]


def test_api_params_keep_non_ascii():
    db.save_result(
        result_id="u",
        experiment_name="e",
        api_params={"prompt": "नमस्ते"},
        response_time=1,
        outputs=["x"],
    )
    assert "नमस्ते" in db.load_results()[0]["api_params"]
