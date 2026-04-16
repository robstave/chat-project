from langchain_core.tools import tool

from config import FIDDLE_FILE


@tool
def fiddle_songs() -> str:
    """Returns the full list of fiddle songs available.
    Use this when the user asks anything about fiddle songs —
    picking one, listing them, sorting them, recommending one, etc.
    """
    with open(FIDDLE_FILE, "r") as f:
        return f.read().strip()
