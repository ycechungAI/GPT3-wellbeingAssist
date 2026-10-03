"""Sidebar widgets shared by every page."""

import streamlit as st
from openai import OpenAI

import config


def llm_client() -> OpenAI | None:
    """Show the API-key box and return a client, or None (with a warning) if no key is set."""
    # Widget values are dropped when switching pages, so keep the key in plain session state
    # and restore the (keyed, stable) widget from it on every page.
    st.session_state.setdefault("api_key", "")
    st.session_state.api_key_input = st.session_state.api_key
    st.sidebar.text_input(
        "OpenRouter API key",
        key="api_key_input",
        type="password",
        help="Optional if OPENROUTER_API_KEY is set in your environment or .env.",
        on_change=lambda: st.session_state.update(api_key=st.session_state.api_key_input),
    )
    key = config.api_key(st.session_state.api_key)
    if not key:
        st.warning("Add an OpenRouter API key in the sidebar to continue (free models only).")
        return None
    return OpenAI(api_key=key, base_url=config.OPENROUTER_BASE_URL)
