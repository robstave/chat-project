from telegram import Update
from telegram.ext import ContextTypes

from config import check_access, DUCK_IMAGE


async def _timer_finished(context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id, seconds = context.job.data
    with open(DUCK_IMAGE, "rb") as photo:
        await context.bot.send_photo(
            chat_id=chat_id, photo=photo, caption=f"Timer finished! ({seconds}s)"
        )


async def timer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not check_access(update):
        return
    try:
        seconds = int(context.args[0])
        if seconds <= 0:
            raise ValueError
        chat_id = update.effective_chat.id
        context.job_queue.run_once(_timer_finished, seconds, data=(chat_id, seconds))
        await update.message.reply_text(f"Timer started: {seconds} seconds")
    except (IndexError, ValueError):
        await update.message.reply_text("Usage: /timer <seconds>")
