#!/bin/sh
# Start the Streamlit app from any working directory.
cd "$(dirname "$0")" || exit 1
exec uv run streamlit run ui.py "$@"
