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
st.title('AI Stock Researcher')

st.header("Stock Research Assistance with GPT-3 :wave:")

st.write('''The **AI Stock Researcher** leverages the worlds most advanced language model GPT-3 to generate stock fundamental analysis. It uses a FastAPI service as the backend.
         Visit this URL at `localhost:8000/docs` for FastAPI documentation.''')

st.image('./ai-bot.jpg', use_column_width=True)

input = st.text_input('Compnany Name:')

if st.button('Generate Report'):
    st.subheader('Stock Fundamentals')
    with st.spinner(text='Fundamental Analysis In progress'):
        report_text = process_prompt(input, backend)
        st.code(report_text)


def create_download_link(val, filename):
    b64 = base64.b64encode(val)  # val looks like b'...'
    return f'<a href="data:application/octet-stream;base64,{b64.decode()}" download="{filename}.pdf">Download file</a>'

export_as_pdf = st.button("Export as PDF")

if export_as_pdf:
    report_text = process_prompt(input, backend)
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial', '', 12)
    html = create_download_link(pdf.output(dest="S").encode("latin-1"), "test")
    st.markdown(html, unsafe_allow_html=True)

