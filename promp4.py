import os
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")

defaultCodePrompt = """"Given the input from the user create a table summarizing the symptoms from the given text and if possible the date when the person experienced the symptom.
Input: I had a headache on sunday and felt a little sick on monday. That went away quickly. Sometimes I have pain in the kidney and today in the morning i felt a bit sleepy.  On wednesday I hurt my leg. I also hurt my ear when I went diving. This morning I hurt my toe.

Output:
| Symptom | Date |
| Headache | Sunday |
| Sickness | Monday |
| Kidney Pain |  Unknown |
| Sleepy |  Today |
| Leg Pain | Wednesday |
| Ear Pain |  Unknown |
| Toe Pain |  Today |

Input: {}
Output:"""

def extract_symptoms_from_patient_answer(text):

    """
    kwargs = {
        "engine": "davinci",
        "temperature":0,
        "top_p":1,
        "max_tokens": 85,
        "best_of": 1,
        "stop": ["Input:", "\n"]
    }
    myKwargs = {}
    """

    answer = openai.Completion.create(prompt=defaultCodePrompt.format(text)
            ,engine="davinci",max_tokens="85", temperature=0
            ,frequency_penalty=0,
            presence_penalty=0,stop=["Input", "\n"])
    print(answer["choices"])[0]["text"]


    #answer = answer.split('|')
    #answer.remove('\n')
    #answer.remove('')

    #symptoms = answer[0::3]
    #dates = answer[1::3]

    return answer# symptoms, dates

print(extract_symptoms_from_patient_answer("I am not feeling well I have a fever"))
