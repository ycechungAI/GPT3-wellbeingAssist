"""Try a few-shot dataset against a model and save the run."""

import logging
from time import perf_counter

import streamlit as st
import yaml

import config
import db
import llm
from sidebar import llm_client

log = logging.getLogger(__name__)
EXPERIMENT_TIMEOUT_SECONDS = 300  # long generations are expected here, unlike the chat

st.set_page_config(page_title="Experimentation")
st.title("Experimentation")
client = llm_client()

model = st.sidebar.selectbox("Model", config.MODELS)
st.sidebar.caption("Free OpenRouter models only. Unsupported parameters are ignored.")
params = {
    "max_tokens": st.sidebar.number_input("Max tokens", 1, 32768, 1024),
    "temperature": st.sidebar.slider("Temperature", 0.0, 2.0, 0.7, 0.05),
    "top_p": st.sidebar.slider("Top P", 0.0, 1.0, 1.0, 0.05),
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

if not config.is_free(model):
    st.error(f"`{model}` is not a free model. Set OPENROUTER_MODEL to a `:free` model id.")
    st.stop()

if st.button("Submit", type="primary", disabled=not (client and prompt.strip())):
    with st.spinner("Requesting completion..."):
        start = perf_counter()
        try:
            response = client.with_options(
                timeout=EXPERIMENT_TIMEOUT_SECONDS
            ).chat.completions.create(model=model, messages=messages, **params)
        except Exception as err:
            log.exception("experiment request failed")
            st.error(
                f"Request failed: {llm.friendly_error(err)} ({type(err).__name__}: see server log)"
            )
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
