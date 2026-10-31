from telegram import Update
from telegram.ext import ContextTypes

from config import check_access, log


async def add(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not check_access(update):
        return
    raw_args = context.args
    try:
        a, b = float(raw_args[0]), float(raw_args[1])
        result = a + b
        if result == int(result) and '.' not in raw_args[0] and '.' not in raw_args[1]:
            await update.message.reply_text(f"{int(a)} + {int(b)} = {int(result)}")
        else:
            await update.message.reply_text(f"{a} + {b} = {result}")
    except (IndexError, ValueError) as e:
        log.warning(
            "invalid /add arguments",
            extra={
                "command": "add",
                "a": raw_args[0] if len(raw_args) > 0 else None,
                "b": raw_args[1] if len(raw_args) > 1 else None,
                "error": str(e),
            },
        )
        await update.message.reply_text("Usage: /add <number> <number>")
