import random

from telegram import Update
from telegram.ext import ContextTypes

from config import check_access, log
from observability import record_random_result


def parse_random_upper_bound(raw_args: list[str]) -> int:
    """Return the exclusive upper bound for /random."""
    if not raw_args:
        return 100

    upper_bound = int(raw_args[0])
    if upper_bound <= 0:
        raise ValueError("upper bound must be positive")
    return upper_bound


async def random_number(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not check_access(update):
        return

    raw_args = context.args
    try:
        upper_bound = parse_random_upper_bound(raw_args)
    except (IndexError, ValueError) as error:
        log.warning(
            "invalid /random arguments",
            extra={
                "command": "random",
                "arg": raw_args[0] if raw_args else None,
                "error": str(error),
            },
        )
        await update.message.reply_text("Usage: /random [positive integer]")
        return

    result = random.randrange(upper_bound)
    record_random_result(result)
    log.info(
        "random result generated result=%s upper_bound=%s",
        result,
        upper_bound,
        extra={"command": "random", "upper_bound": upper_bound, "result": result},
    )
    await update.message.reply_text(str(result))