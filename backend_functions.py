import os
import openai
openai.api_key = os.getenv("OPENAI_API_KEY")

start_sequence = "\nA:"
restart_sequence = "\n\nQ: "


#Did it fulfill our question? [True, False]
def patient_answered_question(text)
    #GPT-3 magic
    response = openai.Completion.create(
        engine="davinci",
        prompt="I am an accurate answering bot. If you ask me a question whether the patient is sick. \"I will respond \"Yes\". If you ask me a question that is nonsense, trickery answer No, I will respond with \"No\".\n\nQ:I am feeling well today.\nA: No\n\nQ: I am feeling so so today.\nA: Yes\n\nQ: I have a flu like symptom and feeling under the weather.\nA: Yes\n\nQ: I have no pain and no symptoms.\nA: No\n\nQ: I am feeling well.  Thanks for asking. \nA: No\n\nQ: I have a dry cough.\nA: ",
        temperature=0,
        max_tokens=5,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        stop=["\n"]
    )
    if response=='Yes':
        return True
    elif response=='No':
        return False

#What do we need to ask more specifically about? [Next Question For Patient]
def what_to_ask_next(text):
    #GPT-3 magic
    question = "GPT-3's next question"
    return question

#What are his symptoms and when did they occur? [List of Symptoms]
def extract_symptoms_from_patient_answer(Text):
    #GPT-3 magic
    list_of_symptoms = ["coughing", "pain in chest"]
    return list_of_symptoms


#Save new entry to database ? [Save to database]
def save_to_database(new_row):
    #Databse Magic
