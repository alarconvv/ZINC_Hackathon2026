# ZINC API

## Local Gemini coach

Put your key in the private, Git-ignored `backend/.env` file as `GEMINI_API_KEY="your-key"`, with a supported text/tool-calling model in `MODEL` (currently `gemini-3.5-flash-lite`). Keep the generated JWT_SECRET stable. Never add these settings to the mobile frontend. This file uses shell assignment syntax and is loaded only by the local startup script.

From `mobileApp/`, after installing backend dependencies, stop any previous API process and run:

```sh
sh backend/start_local.sh
```

The coach sends the message and tool-requested plan/feedback context to Google. Use fictional demo data for verification. Live verification still requires a valid API key, model access and available quota. This local setup does not deploy the app.

FastAPI account/persistence boundary around the unchanged `core/engine.py`, `core/coach.py` and `core/progress_board.py`. Run commands from `mobileApp/`. Full run instructions, verification results, fictional demo credentials and known limits are in [PRODUCT_NOTES.md](PRODUCT_NOTES.md).

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

Tests use temporary SQLite databases and a stubbed coach; no provider calls. Beta — content pending professional review. See the draft privacy and terms files in this folder before any public use.
