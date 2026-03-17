#!/usr/bin/env bash
set -e

# Create virtualenv if it doesn't exist
if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi

# Load environment variables from .env
if [ -f ".env" ]; then
  set -a
  source .env
  set +a
else
  echo "ERROR: .env file not found. Copy .env.example to .env and fill in your values."
  exit 1
fi

# Activate venv
source .venv/bin/activate

# Install deps
pip install --upgrade pip
pip install -r requirements.txt

# Make sure token is set
if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
  echo "ERROR: TELEGRAM_BOT_TOKEN not set"
  echo "Run: export TELEGRAM_BOT_TOKEN=\"your token\""
  exit 1
fi

# Run bot
python bot.py
