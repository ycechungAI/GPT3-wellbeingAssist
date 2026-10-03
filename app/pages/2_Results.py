"""Browse saved experiment runs."""

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
st.caption("Use the table's toolbar to download it as CSV.")
