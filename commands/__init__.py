from telegram.ext import Application, CommandHandler

from commands.start import start
from commands.ping import ping
from commands.add import add
from commands.timer import timer
from commands.fortune import fortune
from commands.calotto import calotto
from commands.f5lottery import f5lottery
from commands.help import commands_help
from commands.ask import ask
from commands.random_number import random_number
from commands.stats import stats
from observability import track_command


def register_all(app: Application) -> None:
    """Register every command handler on the application."""
    app.add_handler(CommandHandler("start", track_command("start")(start)))
    app.add_handler(CommandHandler("ping", track_command("ping")(ping)))
    app.add_handler(CommandHandler("add", track_command("add")(add)))
    app.add_handler(CommandHandler("timer", track_command("timer")(timer)))
    app.add_handler(CommandHandler("fortune", track_command("fortune")(fortune)))
    app.add_handler(CommandHandler("calotto", track_command("calotto")(calotto)))
    app.add_handler(CommandHandler("f5lottery", track_command("f5lottery")(f5lottery)))
    app.add_handler(CommandHandler("random", track_command("random")(random_number)))
    app.add_handler(CommandHandler("commands", track_command("commands")(commands_help)))
    app.add_handler(CommandHandler("ask", track_command("ask")(ask)))
    app.add_handler(CommandHandler("stats", track_command("stats")(stats)))
