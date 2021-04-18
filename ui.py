import streamlit as st
import requests
import time
from fpdf import FPDF
import base64


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

# interact with FastAPI endpoint
backend = 'http://fastapi:8000/code'

def process_prompt(input, server_url: str):
    r = requests.post(server_url,
                      json={"input": input},
                      timeout=8000)

    return r.text


# Setting up the Title
st.title('Clinical Trial Assistance with GPT-3 :wave:')

#st.header("Clinical Trial Assistance with GPT-3 :wave:")

st.write('''Check in with me regularly to improve drug research.''')

st.image('./ai-bot.jpg', use_column_width=True)

input = st.text_input('Send Robo a message:')

if st.button('Send'):
    st.subheader('Send')
    with st.spinner(text='Sending Message...'):
        report_text = process_prompt(input, backend)
        st.code(report_text)
