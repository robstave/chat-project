from telegram.ext import Application

from config import TOKEN
from commands import register_all


def main() -> None:
    app = Application.builder().token(TOKEN).build()
    register_all(app)
    app.run_polling()


if __name__ == "__main__":
    main()
