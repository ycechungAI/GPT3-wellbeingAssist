"""Browse saved experiment runs."""

import csv
import io

import streamlit as st

import db

st.set_page_config(page_title="Results")
st.title("Results")

rows = db.load_results()
if not rows:
    st.info("No saved runs yet. Submit one from the Experimentation page.")
    st.stop()

names = sorted({r["experiment_name"] for r in rows})
selected = st.multiselect("Experiments", names, default=names)
rows = [r for r in rows if r["experiment_name"] in selected]

st.dataframe(rows, hide_index=True)

buffer = io.StringIO()
writer = csv.DictWriter(buffer, fieldnames=list(rows[0]) if rows else [])
writer.writeheader()
writer.writerows(rows)
st.download_button("Download CSV", buffer.getvalue(), "results.csv", "text/csv")
