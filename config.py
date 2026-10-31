import json
import logging
import os
from logging.handlers import RotatingFileHandler

from observability import record_llm_usage
from telegram import Update

# ── Logging ──────────────────────────────────────────────────────────────────
_log_dir = os.environ.get("LOG_DIR", "./logs")
os.makedirs(_log_dir, exist_ok=True)
_log_path = os.path.join(_log_dir, "bot.log")

# Attributes that exist on every stdlib LogRecord — anything else on a record
# was passed in via `extra={...}` and should be surfaced as structured fields.
_STANDARD_RECORD_KEYS = set(logging.LogRecord("", 0, "", 0, "", (), None).__dict__) | {"message", "asctime"}


class JsonFormatter(logging.Formatter):
    """Emit one JSON object per log line, including any `extra` fields."""

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "time": self.formatTime(record, "%Y-%m-%dT%H:%M:%S%z"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        for key, value in record.__dict__.items():
            if key not in _STANDARD_RECORD_KEYS:
                payload[key] = value
        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)
        return json.dumps(payload, default=str)


_log_formatter = JsonFormatter()
_file_handler = RotatingFileHandler(_log_path, maxBytes=5 * 1024 * 1024, backupCount=3)
_file_handler.setFormatter(_log_formatter)
_file_handler._ducky_file_handler = True
_console_handler = logging.StreamHandler()
_console_handler.setFormatter(_log_formatter)
_console_handler._ducky_console_handler = True
# observability.py installs an OTEL handler on the root logger before config is imported.
# Configure root logger explicitly so INFO-level command/access logs are not suppressed.
_root_logger = logging.getLogger()
_root_logger.setLevel(logging.INFO)
if not any(getattr(handler, "_ducky_file_handler", False) for handler in _root_logger.handlers):
    _root_logger.addHandler(_file_handler)
if not any(getattr(handler, "_ducky_console_handler", False) for handler in _root_logger.handlers):
    _root_logger.addHandler(_console_handler)
log = logging.getLogger("bot")

# ── Config ───────────────────────────────────────────────────────────────────
TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
GEMINI_API_KEY = os.environ["GEMINI_APIKEY"]
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
ADMIN_HANDLE = os.environ["ADMIN_HANDLE"].lstrip("@").lower()

_base_dir = os.path.dirname(__file__)
ALLOWED_FILE = os.path.join(_base_dir, "allowed.md")
PERSONA_FILE = os.path.join(_base_dir, "persona.md")
COMMANDS_FILE = os.path.join(_base_dir, "commands.md")
ASSETS_DIR = os.path.join(_base_dir, "assets")
DUCK_IMAGE = os.path.join(ASSETS_DIR, "duck_timer.jpg")
DUCK_FORTUNE_IMAGE = os.path.join(ASSETS_DIR, "duck_fortune.jpg")
DUCK_LOTTO_IMAGE = os.path.join(ASSETS_DIR, "ducky_lotto.png")
FIDDLE_FILE = os.path.join(ASSETS_DIR, "fiddle.md")

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


def log_token_usage(response, label: str = "LLM", model: str = "unknown") -> None:
    """Log token usage from a LangChain AI message response."""
    try:
        meta = getattr(response, "usage_metadata", None) or {}
        if not meta:
            # Gemini sometimes puts it in response_metadata
            meta = getattr(response, "response_metadata", {}).get("usage_metadata", {})
        input_tokens = meta.get("input_tokens", meta.get("prompt_token_count", 0))
        output_tokens = meta.get("output_tokens", meta.get("candidates_token_count", 0))
        total_tokens = meta.get("total_tokens", meta.get("total_token_count", 0))
        input_tokens = int(input_tokens or 0)
        output_tokens = int(output_tokens or 0)
        total_tokens = int(total_tokens or 0)
        command = label.lstrip("/") if isinstance(label, str) and label.startswith("/") else label

        record_llm_usage(command, model, input_tokens, output_tokens, total_tokens)
        log.info(
            "%s tokens — input: %s  output: %s  total: %s",
            label, input_tokens, output_tokens, total_tokens,
            extra={"command": command, "model": model, "input_tokens": input_tokens, "output_tokens": output_tokens, "total_tokens": total_tokens},
        )
    except Exception as e:
        log.warning("Could not log token usage: %s", e)
