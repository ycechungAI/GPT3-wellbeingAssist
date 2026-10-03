"""Prompt experiment lab: run a few-shot dataset against free models side by side."""

import logging
from time import perf_counter

import streamlit as st
import yaml

import config
import db
import llm
from sidebar import llm_client

log = logging.getLogger(__name__)
TIMEOUT_SECONDS = 300  # long generations are expected here, unlike the chat

st.set_page_config(page_title="Experiment Lab", page_icon=":test_tube:", layout="wide")
st.title("Prompt Experiment Lab :test_tube:")
st.caption(
    "Run a few-shot dataset against free models side by side. Every run is saved for Results."
)
client = llm_client()

models = st.sidebar.multiselect(
    "Free models to compare", config.MODELS, default=[config.DEFAULT_MODEL]
)
params = {
    "max_tokens": st.sidebar.number_input("Max tokens", 1, 32768, 1024),
    "temperature": st.sidebar.slider("Temperature", 0.0, 2.0, 0.7, 0.05),
}
reasoning = st.sidebar.toggle(
    "Let models reason",
    help="Slower. Reasoning models may use the whole token budget thinking and return nothing.",
)
extra_body = {} if reasoning else config.NO_REASONING

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

examples = "\n\n".join(str(v).strip() for v in dataset["dataset"].values())
prompt = st.text_area(f"{dataset.get('input', 'Input')}:", placeholder="Enter just the text...")
messages = [
    {"role": "system", "content": f"Follow the pattern of these examples.\n\n{examples}"},
    {
        "role": "user",
        "content": f"{dataset.get('input', 'Input')}: {prompt}\n{dataset.get('output', 'Output')}:",
    },
]

with st.expander("Show full request"):
    st.json({"models": models, **params, "messages": messages})

if blocked := [m for m in models if not config.is_free(m)]:
    st.error(f"Not free models: {', '.join(blocked)}. Use `:free` model ids only.")
    st.stop()

ready = client and prompt.strip() and models
if not st.button("Run", type="primary", disabled=not ready):
    st.stop()

# Models run one after another: free models are rate-limited, and each column fills as it ends.
saved = 0
for column, model in zip(st.columns(len(models)), models, strict=True):
    with column:
        st.markdown(f"**{model}**")
        with st.spinner("Running..."):
            start = perf_counter()
            try:
                response = client.with_options(timeout=TIMEOUT_SECONDS).chat.completions.create(
                    model=model, messages=messages, extra_body=extra_body, **params
                )
            except Exception as err:
                log.exception("experiment request failed for %s", model)
                st.error(f"{llm.friendly_error(err)} ({type(err).__name__}: see server log)")
                continue
            elapsed = round(perf_counter() - start, 3)

        choice = response.choices[0]
        output = (choice.message.content or "").strip()
        if not output:
            why = "it hit the token limit" if choice.finish_reason == "length" else "no text"
            st.warning(f"Empty answer ({why}). Not saved. Try more max tokens or reasoning off.")
            continue
        st.success(output)
        st.caption(f"{elapsed} s")
        db.save_result(
            result_id=response.id,
            experiment_name=experiment_name,
            api_params={"model": model, **params, "reasoning": reasoning, "prompt": prompt},
            response_time=elapsed,
            outputs=[output],
            language=str(dataset.get("language", "")),
            nlp_task=str(dataset.get("nlp_task", "")),
        )
        saved += 1
if saved:
    st.toast(f"Saved {saved} run(s) to the results database")
