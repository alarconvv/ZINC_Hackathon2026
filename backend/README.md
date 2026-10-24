# ZINC API

FastAPI account/persistence boundary around the unchanged `app/engine.py`, `app/coach.py` and `app/progress_board.py`. Run commands from the repository root. Full run instructions, verification results, fictional demo credentials and known limits are in [PRODUCT_NOTES.md](../PRODUCT_NOTES.md).

```sh
python3.11 -m venv backend/.venv
backend/.venv/bin/python -m pip install -r backend/requirements.txt
export JWT_SECRET="$(python3.11 -c 'import secrets; print(secrets.token_urlsafe(48))')"
export DATABASE_URL='sqlite:///backend/zinc.db'
export CORS_ORIGINS='http://localhost:8081,http://127.0.0.1:8081'
backend/.venv/bin/python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --no-access-log
```

Keep a stable JWT_SECRET in your hosting environment across restarts; the example creates a temporary local secret. It must be at least 32 characters. GEMINI_API_KEY and MODEL are optional for the rules-only path and are server environment variables only. No `.env` loader runs automatically. Never put keys in Expo public variables.

Authenticated state mutations require `If-Match: <version>` from the latest `/me` or `/plan` response. Stale writes return 409; the client refetches. Stop overrides stale client versions. Safety symptoms also override stale versions. After Stop, activity and coach routes return 423. The API never accepts an engine-state object or client-written prescription.

SQLite is the local default. PostgreSQL URLs are normalized to the installed psycopg driver. Live PostgreSQL, backups, migrations and hosting have not been verified. SQL parameters are hidden in database exceptions; do not enable SQL echo or request-body logging.

```sh
cd backend
.venv/bin/python -m pytest -q
```

Tests use temporary SQLite databases and a stubbed coach; no provider calls. Beta — content pending professional review. See the draft privacy and terms files in `mobile/content/` before any public use.
