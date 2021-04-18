import os
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")

defaultCodePrompt1 = """I am an doctor assistant bot. If you ask me a question which indicates that the patient is sick. I will respond Yes. If you ask me a question that is nonsense, trickery the answer will be No.
Input: I am feeling well today.
Output: No

Input: I am feeling so so
Output: No

Input:I have a flu like symptom and feeling under the weather.
Output: Yes

Input. I am nto feeling well
Output: Yes

Input: I have dizzyness and fatigue.
Output: Yes

Input: I am scared by the ghosts.
Output: No

Input: Today is a great day to take out my dog for the walk. 
Output: No

Input: Someone hit me on the head.
Output: No

Input: {}
Output:"""

defaultCodePrompt2 = """I am an accurate answering bot. I will tell you whether the previous question was answered. I will respond with Yes if the previous question was answered. If the previous question was not answered or the answer  is nonsense, trickery or ambiguous I will respond with No. 

Input: How are you today? - The sun shines bright.
Output: No

Input: What was your Mother's name? - Maria.
Output: Yes

Input: Can you tell me what the time is? - My dog is cute.
Output: No

Input: Do you have any symptoms that can explain why you feel sick? - I have a headache and some nausea.
Output: Yes

Input: How is your wellbeing? -  I feel good, thanks for asking.
Output: Yes

Input: What is hurting you? - My leg is hurting. It has a cut.
Output: Yes

Input: {}
Output:"""

defaultCodePrompt3 = """I am an accurate answering bot that expands on one's symptoms. If you ask me a question I will expand on the correct symptoms of the following. If you ask me a question that is nonsense, trickery answer, I will respond with 'Please respond to my question.'

Input: I have a dry cough.
Output: Do you have the following symptoms: runny nose? [fever] shortness of breath? [Emphysema]? Other symptoms?

Input: I am feeling so so.
Output: Do you have any other symptoms?

Input: I have a flu like symptom and feeling under the weather.
Output: Do you have high fever, or muscle aches? [Influenza] Other symptoms?

Input: I have a stomach ache.
Output: Do you have the following symptoms: nausea? [vomiting] diarrhea? [appendicitis] Other symptoms?

Input: I have dizziness and fatigue.
Output: Do you have the following symptoms: lightheadedness? [fainting] weakness? [anemia] Other symptoms?

Input:  My head hurts.
Output: Do you have the following symptoms: headache? [migraine] Other symptoms?

Input: {}
Output:"""

def patient_feeling_unwell(text):

    kwargs = {
        "engine": "davinci",
        "temperature": 0.60,
        "max_tokens": 10,
        "best_of": 1,
        "stop": ["Input:", "\n"]
    }

    myKwargs = {}

    for kwarg in myKwargs:
        kwargs[kwarg] = myKwargs[kwarg]

    answer_text = openai.Completion.create(prompt=defaultCodePrompt1.format(text), **kwargs)["choices"][0]["text"].strip()

    print(answer_text)

    if "Yes" in answer_text:
        return [True, answer_text]
    elif "No" in answer_text:
        return [False, answer_text]
    else:
        return "Repeat"


#Did it fulfill our question? [True, False]
def patient_answered_question(text):
    kwargs = {
        "engine": "davinci",
        "temperature": 0.60,
        "max_tokens": 10,
        "best_of": 1,
        "stop": ["Input:", "\n"]
    }

    myKwargs = {}

    answer_text = openai.Completion.create(prompt=defaultCodePrompt2.format(text), **kwargs)["choices"][0]["text"].strip()

    print(answer_text)

    for kwarg in myKwargs:
        kwargs[kwarg] = myKwargs[kwarg]

    if 'Yes' in answer_text:
        return True
    elif 'No' in answer_text:
        return False
    else:
        return "Repeat"

#What symptoms do we need to ask more specifically about? [Next Question for Patient]
def what_to_ask_next(text):
    kwargs = {
        "engine": "davinci",
        "temperature":0,
        "top_p":1,
        "max_tokens": 85,
        "best_of": 1,
        "stop": ["Input:", "\n"]
    }
    myKwargs = {}

    next_question = openai.Completion.create(prompt=defaultCodePrompt3.format(text), **kwargs)["choices"][0]["text"].strip()

    print(next_question)

    for kwarg in myKwargs:
        kwargs[kwarg] = myKwargs[kwarg]
    return next_question

if __name__ == '__main__':
    result2 = False
    while not result2:
        prompt1 = input('Are you feeling unwell?');
        result = patient_feeling_unwell(prompt1)

        print(result)
        result2 = patient_answered_question(result)
        print(result2)
        
        print(type(result2))
        
        if result2 == True:
            result3 = what_to_ask_next(result)
            prompt2 = input(result3)

            #promp4
        else:
            result2 = False


    
        
