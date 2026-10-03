"""Try a few-shot dataset against a model and save the run."""

from time import perf_counter

import streamlit as st
import yaml

import config
import db
from sidebar import openai_client

st.set_page_config(page_title="Experimentation")
st.title("Experimentation")
client = openai_client()

model = st.sidebar.selectbox("Model", config.MODELS)
params = {
    "max_completion_tokens": st.sidebar.number_input("Max tokens", 1, 32768, 1024),
    "n": st.sidebar.number_input("Completions (n)", 1, 10, 1),
}
if config.is_reasoning(model):
    st.sidebar.caption("Reasoning models don't accept sampling parameters.")
else:
    params |= {
        "temperature": st.sidebar.slider("Temperature", 0.0, 2.0, 0.7, 0.05),
        "top_p": st.sidebar.slider("Top P", 0.0, 1.0, 1.0, 0.05),
        "presence_penalty": st.sidebar.slider("Presence penalty", -2.0, 2.0, 0.0, 0.1),
        "frequency_penalty": st.sidebar.slider("Frequency penalty", -2.0, 2.0, 0.0, 0.1),
    }

experiment_name = st.text_input("Experiment name", value="default-exp")

datasets = config.dataset_files()
source = st.radio("Dataset", ["Examples", "Upload own"], horizontal=True)
dataset = None
if source == "Examples" and datasets:
    dataset = config.load_dataset(datasets[st.selectbox("Example dataset", list(datasets))])
elif source == "Upload own":
    if uploaded := st.file_uploader("Upload dataset", type=["yaml", "yml"]):
        try:
            dataset = yaml.safe_load(uploaded)
        except yaml.YAMLError as err:
            st.error(f"Could not parse that YAML file: {err}")
            st.stop()
        if not isinstance(dataset, dict) or not isinstance(dataset.get("dataset"), dict):
            st.error("The file needs a top-level mapping with a `dataset:` map of examples.")
            st.stop()

if not dataset:
    st.info("Pick an example dataset or upload a YAML file (see datasets/ for the format).")
    st.stop()

examples = "\n\n".join(str(v).strip() for v in dataset.get("dataset", {}).values())
prompt = st.text_area(f"{dataset.get('input', 'Input')}:", placeholder="Enter just the text...")
messages = [
    {"role": "system", "content": f"Follow the pattern of these examples.\n\n{examples}"},
    {
        "role": "user",
        "content": f"{dataset.get('input', 'Input')}: {prompt}\n{dataset.get('output', 'Output')}:",
    },
]

with st.expander("Show full request"):
    st.json({"model": model, **params, "messages": messages})

if st.button("Submit", type="primary", disabled=not (client and prompt.strip())):
    with st.spinner("Requesting completion..."):
        start = perf_counter()
        try:
            response = client.chat.completions.create(model=model, messages=messages, **params)
        except Exception as err:
            st.error(f"Request failed: {err}")
            st.stop()
        elapsed = round(perf_counter() - start, 3)

    outputs = [choice.message.content or "" for choice in response.choices]
    for output in outputs:
        st.success(output)
    st.caption(f"Took {elapsed} s")

    db.save_result(
        result_id=response.id,
        experiment_name=experiment_name,
        api_params={"model": model, **params, "prompt": prompt},
        response_time=elapsed,
        outputs=outputs,
        language=str(dataset.get("language", "")),
        nlp_task=str(dataset.get("nlp_task", "")),
    )
    st.toast("Saved to the results database")
