
import os
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")



#Is the patient feeling unwell? [True, False]
def patient_feeling_unwell(text):
    start_sequence = "\nA:"
    restart_sequence = "\n\nQ: "

    response = openai.Completion.create(
      engine="davinci",
      prompt="I am an accurate answering bot. If you ask me a question whether the patient is sick. \"I will respond \"Yes\". If you ask me a question that is nonsense, trickery answer or ambiguous  I will respond with \"No\".\n\nQ:I am feeling well today.\nA: No\n\nQ: I am feeling so so today.\nA: Yes\n\nQ: I have a flu like symptom and feeling under the weather.\nA: Yes\n\nQ: I have no pain and no symptoms.\nA: No\n\nQ: I am feeling well.  Thanks for asking. \nA: No\n\nQ: I have a headache\nA: Yes\n\nQ: {}".format(text),
      temperature=0,
      max_tokens=10,
      top_p=1,
      frequency_penalty=0,
      presence_penalty=0,
      stop=["\n"]
    )

    answer_text = response['choices'][0]['text']
    print("HERE:", answer_text)
    if "Yes" in answer_text:
        return [True,answer_text]
    elif "No" in answer_text:
        return [False, answer_text]
    else:
        return "Repeat"

#Did it fulfill our question? [True, False]
def patient_answered_question(text):
    #GPT-3 magic
    if True:
        return True
    elif False:
        return False

#What do we need to ask more specifically about? [Next Question For Patient]
def what_to_ask_next(text):
    #GPT-3 magic
    question = "GPT-3's next question"
    return question

#What are his symptoms and when did they occur? [List of Symptoms]
def extract_symptoms_from_patient_answer(text):
    #GPT-3 magic
    list_of_symptoms = ["coughing", "pain in chest"]
    return list_of_symptoms


#Save new entry to database ? [Save to database]
def save_to_database(item):
    pass
    #Databse Magic

patient_feeling_unwell('I have a headache')
