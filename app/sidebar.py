"""Sidebar widgets shared by every page."""

import streamlit as st
from openai import OpenAI

import config


def openai_client() -> OpenAI | None:
    """Show the API-key box and return a client, or None (with a warning) if no key is set."""
    # Widget values are dropped when switching pages, so keep the key in plain session state.
    st.session_state.api_key = st.sidebar.text_input(
        "OpenAI API key",
        value=st.session_state.get("api_key", ""),
        type="password",
        help="Optional if OPENAI_API_KEY is set in your environment, .env or gpt3_config.yml.",
    )
    key = config.api_key(st.session_state.api_key)
    if not key:
        st.warning("Add an OpenAI API key in the sidebar to continue.")
        return None
    return OpenAI(api_key=key)
