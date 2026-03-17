from telegram import Update
from telegram.ext import ContextTypes

from config import check_access


async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not check_access(update):
        return
    await update.message.reply_text("pong")
