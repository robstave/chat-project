from telegram import Update
from telegram.ext import ContextTypes

from config import check_access, COMMANDS_FILE


async def commands_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send the list of available commands as a Markdown-formatted message."""
    if not check_access(update):
        return
    try:
        with open(COMMANDS_FILE, "r") as f:
            text = f.read().strip()
    except FileNotFoundError:
        text = "No command list available."
    await update.message.reply_text(text, parse_mode="Markdown")
