# test-bot1 — Ducky Telegram Bot

A Telegram bot powered by Google Gemini, with the persona of Ducky — a mischievous boy sphynx cat.

---

## Running the Bot

### Option A — Local Dev (run.sh)

`run.sh` handles venv creation, dependency install, and startup automatically.

> **If you copied this project from another directory**, delete the old `.venv` first —
> virtual environments contain hardcoded paths and aren't portable:
> ```bash
> rm -rf .venv
> ```

1. Copy the example env file and fill in your values:
   ```bash
   cp .env.example .env
   # edit .env — set TELEGRAM_BOT_TOKEN, GEMINI_APIKEY, ADMIN_HANDLE
   ```

2. Add yourself to `allowed.md`:
   ```
   @yourhandle
   ```

3. Run:
   ```bash
   ./run.sh
   ```

   The script will:
   - Create `.venv` if it doesn't exist
   - Source `.env`
   - Install / upgrade dependencies from `requirements.txt`
   - Start `bot.py`

   Logs are written to `./logs/bot.log`.

---

### Option B — Docker (recommended for production)

1. Copy and fill in your env file:
   ```bash
   cp .env.example .env
   # edit .env — set TELEGRAM_BOT_TOKEN, GEMINI_APIKEY, ADMIN_HANDLE
   ```

2. Add yourself to `allowed.md`:
   ```
   @yourhandle
   ```

3. Create the host log directory:
   ```bash
   sudo mkdir -p /var/log/ducky-bot
   ```

4. Build and start:
   ```bash
   docker compose build
   docker compose up -d
   ```

5. Tail logs:
   ```bash
   docker compose logs -f
   # or directly from the mounted log file:
   tail -f /var/log/ducky-bot/bot.log
   ```

6. Stop:
   ```bash
   docker compose down
   ```

   The container restarts automatically on reboot (`restart: unless-stopped`).
   Logs are mounted from `/var/log/ducky-bot/` on the host → `/app/logs/` in the container.

---

## Configuration

### Environment variables (`.env`)

| Variable | Description |
|----------|-------------|
| `TELEGRAM_BOT_TOKEN` | Token from [@BotFather](https://t.me/BotFather) |
| `GEMINI_APIKEY` | Google Gemini API key |
| `ADMIN_HANDLE` | Your Telegram `@handle` — has permanent full access |
| `LOG_DIR` | *(optional)* Directory for `bot.log`. Defaults to `./logs`. |

### Access control (`allowed.md`)

Only Telegram users whose `@handle` appears in `allowed.md` (or whose handle matches `ADMIN_HANDLE`) can use the bot. All other messages are silently ignored.

- One `@handle` per line — the `@` prefix is optional
- Lines starting with `#` are comments
- The file is re-read on every access check — **no restart needed** to add or remove users
- The admin handle (from `.env`) always has access regardless of this file

Example `allowed.md`:
```
# Friends
@alice
@bob
```

Every access attempt is logged with `GRANTED [admin]`, `GRANTED [user]`, or `DENIED`.

### Persona (`persona.md`)

Ducky's personality is defined in `persona.md`. It is read fresh on every LLM call and injected as the system prompt. Edit it to change how Ducky behaves — no restart needed.

---

## Commands

| Command | Description |
|---------|-------------|
| `/start` | Greet the bot and get started. |
| `/ping` | Check if the bot is alive. Responds with `pong`. |
| `/add <a> <b>` | Add two numbers together. Example: `/add 3 5` → `3 + 5 = 8` |
| `/timer <seconds>` | Set a countdown timer. When it expires the bot sends a duck photo. Example: `/timer 60` |
| `/fortune` | Ask Ducky for a whimsical daily fortune, delivered with a duck photo. |
| `/calotto` | Generate California SuperLotto Plus numbers. Ducky writes a lucky cat haiku, which is hashed to seed the RNG, producing 5 numbers (1–47) plus a Mega number (1–27). |
| `/f5lottery` | Generate California Fantasy 5 numbers. Same haiku-seeded approach, producing 5 numbers (1–39). |
| `/commands` | Show the list of available commands (sent as a Markdown-formatted message). |

All commands require access — unauthorized users receive no response.

The command list shown by `/commands` is loaded from `commands.md` at the project root — edit it to update what users see.

---

## Logging

Logs are written to `$LOG_DIR/bot.log` using Python's `RotatingFileHandler`:

- **Max size:** 5 MB per file
- **Backups:** 3 (i.e. `bot.log`, `bot.log.1`, `bot.log.2`, `bot.log.3`)
- **Docker mount:** `/var/log/ducky-bot/` on the host → `/app/logs/` in the container

---

## File Overview

| File / Directory | Purpose |
|-----------------|---------|
| `bot.py` | Entry point — creates the Telegram application and starts polling |
| `config.py` | Shared config, logging, access control, and persona loading |
| `commands/` | Package containing one file per bot command |
| `commands.md` | Markdown command list loaded by `/commands` |
| `persona.md` | Ducky's system prompt / persona — loaded on each LLM call |
| `allowed.md` | Allowlist of Telegram handles permitted to use the bot |
| `assets/` | Images used by the bot (`duck_timer.jpg`, `duck_fortune.jpg`) |
| `requirements.txt` | Python dependencies |
| `run.sh` | Convenience script for local dev — sources `.env`, creates venv, runs bot |
| `.env` | Secret environment variables (gitignored — copy from `.env.example`) |
| `.env.example` | Template for `.env` |
| `Dockerfile` | Container image definition |
| `docker-compose.yml` | Compose service definition with volume mount and restart policy |
