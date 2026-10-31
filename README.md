# test-bot1 — Ducky Telegram Bot

This is a Telegram bot built with Google Gemini and styled around Ducky, a mischievous boy sphynx cat.

> This is a personal project. The `/stats` command is wired to private AWS Lambda and DynamoDB resources, so it will not work for you out of the box. The bot structure, persona system, and command layout are still usable as a starting point if you want to build something similar.  Remove the `/stats` command or implement your own backend if you want it to work.

---

## Running the bot

### Option A: local dev with run.sh

`run.sh` creates the virtual environment, installs dependencies, loads the environment file, and starts the bot.

> If you copied this repo to a new directory, delete the old `.venv` first. Virtual environments keep hardcoded paths and are not portable.
>
> ```bash
> rm -rf .venv
> ```

1. Copy the example environment file and fill in your values:

   ```bash
   cp .env.example .env
   # edit .env and set TELEGRAM_BOT_TOKEN, GEMINI_APIKEY, and ADMIN_HANDLE
   ```

2. Add yourself to `allowed.md`:

   ```
   @yourhandle
   ```

3. Start it:

   ```bash
   ./run.sh
   ```

   The script does this:
   - creates `.venv` if it does not exist
   - loads variables from `.env`
   - installs or upgrades dependencies from `requirements.txt`
   - runs `bot.py`

   Logs go to `./logs/bot.log`.

---

### Option B: Docker

1. Copy the env file and add your values:

   ```bash
   cp .env.example .env
   # edit .env and set TELEGRAM_BOT_TOKEN, GEMINI_APIKEY, and ADMIN_HANDLE
   ```

2. Add yourself to `allowed.md`:

   ```
   @yourhandle
   ```

3. Create the host log directory:

   ```bash
   sudo mkdir -p /var/log/ducky-bot
   ```

4. Build and start the container:

   ```bash
   docker compose build
   docker compose up -d
   ```

5. Watch the logs:

   ```bash
   docker compose logs -f
   # or directly from the mounted file:
   tail -f /var/log/ducky-bot/bot.log
   ```

6. Stop it:

   ```bash
   docker compose down
   ```

   Docker restarts the service automatically with `restart: unless-stopped`.
   Logs are mounted from `/var/log/ducky-bot/` on the host to `/app/logs/` in the container.

---

## Configuration

### Environment variables in `.env`

| Variable | Description |
|----------|-------------|
| `TELEGRAM_BOT_TOKEN` | Token from [@BotFather](https://t.me/BotFather) |
| `GEMINI_APIKEY` | Google Gemini API key |
| `ADMIN_HANDLE` | Telegram handle with permanent full access |
| `LOG_DIR` | Optional path for `bot.log`; defaults to `./logs` |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | Optional OTLP HTTP base endpoint for telemetry export. Example: `http://127.0.0.1:4318` for local use or `http://host.docker.internal:4318` in Docker |

### Access control with `allowed.md`

Only Telegram users whose handle appears in `allowed.md` or whose handle matches `ADMIN_HANDLE` can use the bot. Everyone else is ignored silently.

- one handle per line; the `@` is optional
- lines starting with `#` are comments
- the file is re-read on every access check, so no restart is needed to add or remove users
- the admin handle from `.env` always has access

Example:

```text
# Friends
@alice
@bob
```

Every access attempt is logged as `GRANTED [admin]`, `GRANTED [user]`, or `DENIED`.

### Persona in `persona.md`

Ducky's personality is defined in `persona.md`. The file is loaded fresh on every LLM call and used as the system prompt. Edit it if you want to change the bot's behavior without restarting it.

---

## Commands

| Command | Description |
|---------|-------------|
| `/start` | Start the bot and greet the user. |
| `/ping` | Check whether the bot is alive. Replies with `pong`. |
| `/add <a> <b>` | Add two numbers. Example: `/add 3 5` → `3 + 5 = 8` |
| `/timer <seconds>` | Start a countdown timer. When it expires, the bot sends a duck photo. Example: `/timer 60` |
| `/fortune` | Ask Ducky for a whimsical daily fortune with a duck photo. |
| `/calotto` | Generate California SuperLotto Plus numbers. Ducky writes a lucky cat haiku, seeds the RNG with a hash of it, and produces 5 numbers from 1–47 plus a Mega number from 1–27. |
| `/f5lottery` | Generate California Fantasy 5 numbers using the same haiku-seeded approach, producing 5 numbers from 1–39. |
| `/random [max]` | Return a random number from 0 to 99, or from 0 to `max - 1` when a positive integer is provided. |
| `/commands` | Show the available commands in a Markdown-formatted message. |
| `/ask <question>` | Ask Ducky anything in natural language. The LLM can call tools automatically, including looking up your stats. Example: `/ask what are my latest weights?` |
| `/stats list` | List all available metric IDs for the current user. |
| `/stats <metric>` | Show the last 10 events for a metric. Example: `/stats weight-scale` |
| `/stats set <metric> <value> [MM/DD]` | Record a new metric value, optionally with a specific date. |

### Stats aliases

| Alias | Resolves to |
|-------|-------------|
| `steps` | `steps-iphone` |
| `weight` | `weight-scale` |

The `/stats` command talks to an external AWS API Gateway → Lambda → DynamoDB backend. The relevant environment variables are:

| Variable | Description |
|----------|-------------|
| `AWS_API_URL` | Base URL of the API Gateway endpoint |
| `AWS_API_KEY` | API key sent as the `x-api-key` header |
| `AWS_USER` | Username to query. If unset, it defaults to the Telegram sender's handle |

All commands require access. Unauthorized users get no response.

The list shown by `/commands` is loaded from `commands.md` at the project root. Edit that file if you want to change what users see.

---

## Logging

Logs are written to `$LOG_DIR/bot.log` using Python's `RotatingFileHandler`:

- max size: 5 MB per file
- backups: 3 files (`bot.log`, `bot.log.1`, `bot.log.2`, `bot.log.3`)
- Docker mount: `/var/log/ducky-bot/` on the host to `/app/logs/` in the container

---

## File overview

| File / Directory | Purpose |
|-----------------|---------|
| `bot.py` | Entry point; builds the Telegram app and starts polling |
| `config.py` | Shared config, logging, access checks, and persona loading |
| `commands/` | Package with one file per bot command |
| `commands.md` | Markdown command list loaded by `/commands` |
| `persona.md` | Ducky's system prompt and persona definition |
| `allowed.md` | Allowlist of Telegram handles allowed to use the bot |
| `assets/` | Images used by the bot |
| `requirements.txt` | Python dependencies |
| `run.sh` | Convenience script for local dev; loads `.env`, creates a venv, and runs the bot |
| `.env` | Secret environment variables; gitignored and copied from `.env.example` |
| `.env.example` | Template for `.env` |
| `Dockerfile` | Container image definition |
| `docker-compose.yml` | Compose service definition with mounted logs and restart policy |
