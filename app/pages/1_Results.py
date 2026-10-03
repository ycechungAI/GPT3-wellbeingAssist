"""Compare saved experiment runs, per run and per model."""

import json
from statistics import median

import streamlit as st

import db

st.set_page_config(page_title="Results", layout="wide")
st.title("Results")

rows = db.load_results()
if not rows:
    st.info("No saved runs yet. Run an experiment from the lab first.")
    st.stop()

for row in rows:
    params = json.loads(row["api_params"] or "{}")
    row["model"] = params.get("model") or params.get("engine") or "(unknown)"

names = sorted({r["experiment_name"] for r in rows})
selected = st.multiselect("Experiments", names, default=names)
rows = [r for r in rows if r["experiment_name"] in selected]

st.subheader("Per model")
by_model: dict[str, list[float]] = {}
for r in rows:
    by_model.setdefault(r["model"], []).append(r["response_time"])
st.dataframe(
    [
        {"model": m, "runs": len(times), "median latency (s)": round(median(times), 2)}
        for m, times in sorted(by_model.items())
    ],
    hide_index=True,
)

st.subheader("Runs")
columns = ["created_at", "experiment_name", "model", "response_time", "output_response"]
st.dataframe([{c: r[c] for c in columns} for r in rows], hide_index=True)
st.caption("Use a table's toolbar to download it as CSV.")
