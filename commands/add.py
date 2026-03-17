from telegram import Update
from telegram.ext import ContextTypes

from config import check_access


async def add(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not check_access(update):
        return
    try:
        a, b = float(context.args[0]), float(context.args[1])
        result = a + b
        if result == int(result) and '.' not in context.args[0] and '.' not in context.args[1]:
            await update.message.reply_text(f"{int(a)} + {int(b)} = {int(result)}")
        else:
            await update.message.reply_text(f"{a} + {b} = {result}")
    except (IndexError, ValueError):
        await update.message.reply_text("Usage: /add <number> <number>")
