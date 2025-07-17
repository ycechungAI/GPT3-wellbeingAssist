import pytest
from streamlit.testing.v1 import AppTest


def test_app_loads():
    """Test that the app loads without errors."""
    at = AppTest.from_file("ui.py")
    at.run()
    assert not at.exception
