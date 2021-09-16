import re
from pathlab import Path

import streamlit as st

MODELS = ["davinci-codex", "cushman-codex", "davinci", "curie", "babbage", "ada"]
GPT3_CONFIG_PATH = Path(__file__).parents[1] / "gpt3_config.yml"
DATASET_PATH = Path(__file__).parents[1] / "datasets"
DATASETS = dict(
    [
        (re.sub(r"_", " ", str(ds).split("/")[-1].split(".yml")[0].title()), ds)
        for ds in list(DATASET_PATH.glob("*.yml"))
    ]
)
PARAMS = {}