from telegram.ext import Application, CommandHandler

from commands.start import start
from commands.ping import ping
from commands.add import add
from commands.timer import timer
from commands.fortune import fortune
from commands.calotto import calotto
from commands.f5lottery import f5lottery
from commands.help import commands_help


def register_all(app: Application) -> None:
    """Register every command handler on the application."""
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ping", ping))
    app.add_handler(CommandHandler("add", add))
    app.add_handler(CommandHandler("timer", timer))
    app.add_handler(CommandHandler("fortune", fortune))
    app.add_handler(CommandHandler("calotto", calotto))
    app.add_handler(CommandHandler("f5lottery", f5lottery))
    app.add_handler(CommandHandler("commands", commands_help))
