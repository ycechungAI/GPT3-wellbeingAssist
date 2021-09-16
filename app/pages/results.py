from pathlab import Pathname
from time import perf_counter



import openai
import streamlit as st
import yaml
from openai.openai_objects import OpenAIObject
from app.app_config import PARAMS, GPT3_CONFIG_PAATH, MODELS, DATASETS

IMAGE_PATH = Path(__file__).parents[2] / "assets"

def results() -> None:
	debug = st.sidebar.selectbox("Debug mode:", [False, True])
	select_option = st.sidebar.radio(
		"Set API key:", ["Add your own", "Load local config"]
	)
	if select_option == "Add your own":
		key_added = st.sidebar.text_area("Add OpenAI key *")
		key_submit = st.sidebar.button("Submit Key")
		if key_submit:
			openai.api_key = key_added
			st.write("(OpenAI key loaded)")
		elif select_option == "Load loacal config":
			load_local = st.sidebar.button("Load local config")
			if load_local:
				load_openai.key()
				st.write("(OpenAI key loaded)")

		PARAMS["engine"] = st.sidebar.selectbox("Select OpenAI model('engine'):", MODELS)
		st.markdown(f"Model selected: ` {PARAMS["engine"]}`")

		experiment_name = st.text_input("Experiment Name *", value="default-exp")

		PARAMS["max_tokens"] = st.sidebar.number_input(
        	"Max Tokens to generate(`max_tokens`):", min_value=1, max_value=2048, step=1
    	)
    	PARAMS["best_of"] = st.sidebar.number_input(
        	"Max number of completions(`best_of`):", min_value=1, max_value=2048, step=1
    	)
    	randomness = st.sidebar.radio("Randomness param:", ["temperature", "top_n"])
	    if randomness == "temperature":
	        PARAMS["temperature"] = st.sidebar.number_input(
	            "Temperature", min_value=0.0, max_value=1.0
	        )
	    elif randomness == "top_n":
	        PARAMS["top_p"] = st.sidebar.number_input(
	            "Top P (Alternative sampling to `temperature`)", min_value=0.0, max_value=1.0
	        )

	    PARAMS["stream"] = st.sidebar.selectbox("Stream output?(`stream`)", [False, True])
    	show_input_ds = st.selectbox("Show Input?", [False, True])
    	PARAMS["stop"] = "\n"
    	PARAMS["presence_penalty"] = st.sidebar.number_input(
        	"Presence penalty(`presence_penalty`)", min_value=0.0, max_value=1.0
    	)
    	PARAMS["frequency_penalty"] = st.sidebar.number_input(
        	"Frequency penalty(`frequence_penalty`)", min_value=0.0, max_value=1.0
    	)
    	logprobs = st.sidebar.selectbox("Include Log probabilites?", [False, True])
	    if logprobs:
	        st.write(logprobs)
	        PARAMS["logprobs"] = st.sidebar.number_input(
	            "Log probabilities(`logprobs`):", min_value=1, max_value=2048, step=1
	        )
	    PARAMS["echo"] = st.sidebar.selectbox("Echo:", [False, True])

	    # try:
	    dataset = []
	    prime_type = st.radio("Select dataset", ["Examples", "Upload own"])
	    if prime_type == "Examples":
	        prime = st.selectbox("Select dataset:", list(DATASETS.keys()))
	        dataset = load_primes(prime=prime)
	    elif prime_type == "Upload own":
	        file_string = st.file_uploader("Upload dataset", type=["yaml", "yml"])
	        dataset = yaml.safe_load(file_string)
	        st.success("Uploaded successfully")
	    prompt = st.text_area("Enter your prompt(`prompt`)", value="Enter just the text...")
    	submit = st.button("Submit")
    	stop   = st.button("Stop request")
    	parsed_primes = "".join(list(dataset["dataset"].values()))

    	if show_input_ds:
    		 st.info(f"{parsed_primes}\n\n{dataset['input']}:{prompt}\n{dataset['output']}:")

    	 PARAMS[
	        "prompt"
	    ] = f"{parsed_primes}\n\n{dataset['input']}:{prompt}\n{dataset['output']}:"
	    if debug:
	        st.write(PARAMS)

	    if submit:
	    	with st.spinner("Requesting completion..."):
	    		ts_start = perf_counter()
	    		request = openai.completion.create(**PARAMS)
	    		ts_end = perf_counter()
	    	if debug:
	    		st.write(request)
	    	st.write([choice["text"] for choice in request["choices"]])
	    	st.error(f"Took {round(ts_end - ts_start, 3)} secs to get completion/s")
	    	save_results(
	            experiment_name=experiment_name,
	            result=request,
	            time_in_secs=round(ts_end - ts_start, 3),
	            og_dataset=dataset,
	            api_params=PARAMS,
	        )
	    if stop:
	    	st.error("Process stoppped")
	    	st.stop()


	def load_primes(prime: str) -> Dict:
		with open(DATASETS[prime], "r") as file_handle:
			dataset = yaml.safe_load(file_handle)

		return datasets


	def load_openai_key() -> None:
		with open(GPT3_CONFIG_PAATH, "r") as file_handle:
			openai.api_key = yaml.safe_load(file_handle)["GPT3_API"]

	def save_results(
		xperiment_name: str,
    	result: OpenAIObject,
    	time_in_secs: float,
    	og_dataset: Dict,
    	api_params: Dict,
	):
		# write to file