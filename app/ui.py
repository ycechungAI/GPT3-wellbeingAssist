
import streamlit as st
import requests
import time
from fpdf import FPDF
import base64
import os
import numpy as np
from prompts import patient_feeling_unwell, patient_answered_question, what_to_ask_next, extract_symptoms_from_patient_answer
from dotenv import load_dotenv

def ui() -> None:
    load_dotenv('.env')
    # Formatting the app bg and text color
    st.markdown(
        """
    <style>
    .reportview-container  {
        background-image: linear-gradient(#f5f7fa,#c3cfe2);
    }
    </style>
    """,
        unsafe_allow_html=True,
    )

    # Setting up the Title
    st.title('Synth : Doc Assistant')
    st.title('Clinical Trial Assistance with GPT-3 :wave:')
    st.write('''Check in with me regularly to improve drug research.''')
    st.image('../assets/ai-bot.jpg', use_column_width=True)
    input = st.text_input('Send Robo a message:')

    if st.button('Send'):
        with st.spinner(text='Sending Message...'):
            #Save last Message
            f = open("storage.txt", "a")
            f.write(str(input + '  \n'))
            f.close()

            #Step 2 after Step 1
            try:
                if np.load('state.npy') == 1:
                    output = extract_symptoms_from_patient_answer(input)
                    print(output)
                    f = open("storage.txt", "a")
                    f.write(str("{}".format(output) + '  \n'))
                    f.close()
                    np.save('state', -1) #done state
                    pass
            except:
                pass

            # First Question Save -1 if Ok, 0 otherwise
            try:
                if os.path.isfile('state.npy') == True and np.load('state.npy') == -2:
                    print("THIS IS WHAT WE GET",input)
                    first_question = patient_feeling_unwell(input)
                    if first_question == False or input == 'I am feeling good.':
                        f = open("storage.txt", "a")
                        f.write(str("Bot: I am happy to hear that. Let's check-in again soon!" + '  \n'))
                        f.close()
                        np.save('state', -1) #done state
                        os.remove("state.npy")
                    else:
                        np.save('state', 0) #Nest Question
                        input = what_to_ask_next(input)
                        f = open("storage.txt", "a")
                        f.write('Bot:' + str(input + '  \n'))
                        f.close()
                        np.save('state', 1)
                        print("INHERE")
            except:
                pass

            # First Question Save -1 if Ok, 0 otherwise
            try:
                if os.path.isfile('state.npy') == False:
                        f = open("storage.txt", "a")
                        f.write(str("Bot: Hello! How is your wellbeing today?" + '  \n'))
                        f.close()
                        np.save('state', -2) #done state
            except:
                pass

            # return last 5 logged messages
            r = reversed(list(open("storage.txt", "r").readlines()))
            text = ""
            for idx, line in enumerate(r):
                if idx <5:
                    text += line + '  \n'
            st.info(text)
            print(np.load('state.npy'))