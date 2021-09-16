## GPT3-wellbeingAssist

# Main Problems: 
Gain information about patients health status in between doctor's visits 
Put it in a structured format

# Outcome: 
Improve clinical trials effectiveness and patients well being

Given the patient’s answer….: 
Did it fulfill our question? [Yes, No]
Do we need to ask a follow-up question? [Yes, No]
What do we need to ask more specifically about? 
What are his symptoms and when did they occur? 
How can we categorize his answer (structure the data)? 

# Open Issues: 
Legal aspect?

## NEW INSTRUCTIONS

# Setup

- pip install pysqlite3

- Add your OpenAI key to `gpt3_config.yml` in this format:

```yaml
GPT3_API: ab-XXXXXXXXXXXXXXXXXXXXXXXX
```
- Or you can add it via the `streamlit` app directly.
- Install `poetry`. Follow the [official site](https://python-poetry.org/docs/#installation) or [this cookbook](https://soumendra.gitbook.io/deeplearning-cookbook/setting-up/setting-up-poetry-for-your-project)
- Once `poetry` is installed, run `poetry install`. This will download all the packages needed (ideally in `.venv`) as well as setup the repository.
- To run migrations: `poetry run migrate`

# Running the app
- To run the `streamlit` app: `poetry run st-server` or bash run.sh
- You will now be able to view the application @ `localhost:8000`

# Adding new primes/dataset
- Create a `*.yml` or `*.yaml` file in `datasets`, this file would be available in the `streamlit` app in the dropdown

# Running
[x] only works on streamlit run home.py when you cd into the app folder
[ ] getting the script to work by just running bash script run.sh

If you use this project, do help out:
Follow and Star the project
```

https://ibb.co/TgH5p6t/experiment1.png

## ======================================
## DEPRECIATED
## ======================================
# Environment - Conda python3
conda env create --name envname --file=environment_droplet.yml
conda activate envname

# Install Openai and Flask 
pip install openai
pip install python-dotenv
pip install Flask
pip install fpdf

# Deactivate Environment
conda deactivate

# To run Flask
$ export FLASK_APP=backend_functions.py 

$ flask run
