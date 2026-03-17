import logging
import os
from logging.handlers import RotatingFileHandler

from telegram import Update

# ── Logging ──────────────────────────────────────────────────────────────────
_log_dir = os.environ.get("LOG_DIR", "./logs")
os.makedirs(_log_dir, exist_ok=True)
_log_path = os.path.join(_log_dir, "bot.log")

_log_formatter = logging.Formatter("%(asctime)s  %(levelname)-8s  %(message)s")
_file_handler = RotatingFileHandler(_log_path, maxBytes=5 * 1024 * 1024, backupCount=3)
_file_handler.setFormatter(_log_formatter)
_console_handler = logging.StreamHandler()
_console_handler.setFormatter(_log_formatter)

logging.basicConfig(level=logging.INFO, handlers=[_file_handler, _console_handler])
log = logging.getLogger("bot")

# ── Config ───────────────────────────────────────────────────────────────────
TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
GEMINI_API_KEY = os.environ["GEMINI_APIKEY"]
ADMIN_HANDLE = os.environ["ADMIN_HANDLE"].lstrip("@").lower()

_base_dir = os.path.dirname(__file__)
ALLOWED_FILE = os.path.join(_base_dir, "allowed.md")
PERSONA_FILE = os.path.join(_base_dir, "persona.md")
COMMANDS_FILE = os.path.join(_base_dir, "commands.md")
ASSETS_DIR = os.path.join(_base_dir, "assets")
DUCK_IMAGE = os.path.join(ASSETS_DIR, "duck_timer.jpg")
DUCK_FORTUNE_IMAGE = os.path.join(ASSETS_DIR, "duck_fortune.jpg")
DUCK_LOTTO_IMAGE = os.path.join(ASSETS_DIR, "ducky_lotto.png")

# ── Access control ───────────────────────────────────────────────────────────

def load_allowed_users() -> set:
    """Read allowed.md and return a set of lowercase handles (no @)."""
    allowed = set()
    try:
        with open(ALLOWED_FILE, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                allowed.add(line.lstrip("@").lower())
    except FileNotFoundError:
        log.warning("allowed.md not found — no regular users will have access")
    return allowed


def check_access(update: Update) -> bool:
    """Return True if the sender is allowed. Log every access attempt."""
    user = update.effective_user
    if user is None or not user.username:
        log.info("DENIED  (no username)  user_id=%s", user.id if user else "unknown")
        return False

    handle = user.username.lower()

    if handle == ADMIN_HANDLE:
        log.info("GRANTED [admin]  @%s", handle)
        return True

    if handle in load_allowed_users():
        log.info("GRANTED [user]   @%s", handle)
        return True

    log.info("DENIED  [unknown] @%s", handle)
    return False


def load_persona() -> str:
    """Read persona.md and return its contents as the system prompt."""
    try:
        with open(PERSONA_FILE, "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return "You are a helpful assistant."
