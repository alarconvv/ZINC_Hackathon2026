#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
if [ ! -f backend/.env ]; then
  echo 'Create backend/.env with your private Gemini and server settings.' >&2
  exit 1
fi
set -a
. ./backend/.env
set +a
if [ -z "${GEMINI_API_KEY:-}" ] || [ -z "${MODEL:-}" ]; then
  echo 'Set GEMINI_API_KEY and MODEL in backend/.env, save, then restart.' >&2
  exit 1
fi
exec "${PYTHON_BIN:-backend/.venv/bin/python}" -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --no-access-log
