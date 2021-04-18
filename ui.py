import streamlit as st
import requests
import time
from fpdf import FPDF
import base64

r = ""

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



def process_prompt(input, server_url: str):
    r += '\n\n'+str(input.text)

    return r


# Setting up the Title
st.title('Clinical Trial Assistance with GPT-3 :wave:')

#st.header("Clinical Trial Assistance with GPT-3 :wave:")

st.write('''Check in with me regularly to improve drug research.''')

st.image('./ai-bot.jpg', use_column_width=True)

st.write(r)
input = st.text_input('Send Robo a message:')

if st.button('Send'):
    with st.spinner(text='Sending Message...'):
        f = open("storage.txt", "a")
        f.write(str(input + '  \n'))
        f.close()

        #f = open("storage.txt", "r")
        #r = f.readlines()
        r = reversed(list(open("storage.txt", "r").readlines()))
        text = ""
        for idx, line in enumerate(r):
            if idx <5:
                text += line + '  \n'
        st.info(text)



        #r = process_prompt(input)
        #st.write(r)
        #st.code(report_text)
