import click
from loguru import logger

import os
import subprocess
from pathlib import Path

THIS_DIRECTORY = Path(__file__).parent.resolve()


@click.command()
def st_server():
    """Starts the streamlit server."""
    logger.info("Starting server...")
    subprocess.run(
        [
            "poetry",
            "run",
            "streamlit",
            "run",
            str(THIS_DIRECTORY / "app" / "ui.py"),
        ],
        check=True,
        universal_newlines=True,
    )


@click.command()
def migrations():
	logger.info("Running migrations...")
    os.chdir(THIS_DIRECTORY / "db")
    subprocess.run(
        ["poetry", "run", "alembic", "upgrade", "head"],
        check=True,
        universal_newlines=True,
    )
    logger.info("Completed succeessfully")
