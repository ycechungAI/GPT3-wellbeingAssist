"""Patient check-in: ask how they feel, follow up on symptoms, structure the answer."""

import logging

import streamlit as st

import config
import llm
from sidebar import llm_client

log = logging.getLogger(__name__)
GREETING = "Hello! How is your wellbeing today?"
FAREWELL = "I am happy to hear that. Let's check in again soon!"
THANKS = "Thank you. Here is a summary of what you told me:"


def reset() -> None:
    st.session_state.stage = "greet"
    st.session_state.messages = [{"role": "assistant", "content": GREETING}]
    st.session_state.question = GREETING
    st.session_state.complaint = ""
    st.session_state.symptoms = []


def say(text: str) -> None:
    st.session_state.messages.append({"role": "assistant", "content": text})


def handle(client, text: str) -> None:
    """Advance the check-in: greet -> follow_up -> done."""
    state = st.session_state
    if state.stage == "greet":
        if llm.is_unwell(client, text):
            state.complaint = text
            state.question = llm.next_question(client, text)
            say(state.question)
            state.stage = "follow_up"
        else:
            say(FAREWELL)
            state.stage = "done"
    elif state.stage == "follow_up":
        if not llm.answered_question(client, state.question, text):
            say(f"Sorry, I didn't quite get that. {state.question}")
            return
        state.symptoms = llm.extract_symptoms(client, f"{state.complaint}\n{text}")
        say(THANKS if state.symptoms else "Thank you, I have noted that down.")
        state.stage = "done"


st.set_page_config(page_title="Synth: Doc Assistant", page_icon=":wave:")
st.title("Synth: Doc Assistant :wave:")
st.caption("Clinical trial check-in. Check in with me regularly to improve drug research.")
st.image(str(config.ASSETS_DIR / "ai-bot.jpg"), width=160)

if "stage" not in st.session_state:
    reset()
st.sidebar.button("New check-in", on_click=reset)
client = llm_client()

for message in st.session_state.messages:
    st.chat_message(message["role"]).write(message["content"])

if st.session_state.symptoms:
    st.table(st.session_state.symptoms)

if st.session_state.stage == "done":
    st.info("Check-in complete. Use **New check-in** in the sidebar to start again.")
elif client and (text := st.chat_input("Send Robo a message")):
    st.session_state.messages.append({"role": "user", "content": text})
    try:
        with st.spinner("Thinking..."):
            handle(client, text)
    except Exception as err:  # surface API/network errors in the chat, don't crash
        log.exception("model call failed")
        say(f"Sorry: {llm.friendly_error(err)}")
    st.rerun()
