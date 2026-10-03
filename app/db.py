"""SQLite storage for experiment results."""

import json
import sqlite3
from contextlib import closing
from pathlib import Path

import config

SCHEMA = """
CREATE TABLE IF NOT EXISTS gpt3_results (
    result_id       TEXT PRIMARY KEY,
    experiment_name TEXT NOT NULL,
    api_params      TEXT,
    response_time   REAL,
    output_response TEXT,
    language        TEXT,
    nlp_task        TEXT,
    error_msg       TEXT,
    created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
)
"""


def connect(path: Path | None = None) -> sqlite3.Connection:
    path = path or config.DB_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute(SCHEMA)
    return conn


def save_result(
    *,
    result_id: str,
    experiment_name: str,
    api_params: dict,
    response_time: float,
    outputs: list[str],
    language: str = "",
    nlp_task: str = "",
    error_msg: str = "",
    path: Path | None = None,
) -> None:
    with closing(connect(path)) as conn, conn:
        conn.execute(
            "INSERT INTO gpt3_results (result_id, experiment_name, api_params, response_time,"
            " output_response, language, nlp_task, error_msg) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                result_id,
                experiment_name,
                json.dumps(api_params),
                response_time,
                json.dumps(outputs, ensure_ascii=False),
                language,
                nlp_task,
                error_msg,
            ),
        )


def load_results(path: Path | None = None) -> list[dict]:
    path = path or config.DB_PATH
    if not path.exists():
        return []
    with closing(connect(path)) as conn:
        rows = conn.execute("SELECT * FROM gpt3_results ORDER BY created_at DESC").fetchall()
    return [dict(r) for r in rows]
