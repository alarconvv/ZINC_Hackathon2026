# ZINC

ZINC is a general-wellness app that helps people build a manageable weekly routine of strength and balance exercises, yoga, reasoning games, and relaxation. It combines a flexible activity calendar, recorded feedback, a progress board, and a Gemini-powered coach.

The rules engine creates exercise prescriptions and checks scheduling and progression limits. The AI coach can explain the plan and propose a bounded adjustment; the person must explicitly accept a proposal before it is staged for the next week.

**Status:** working local web application with an Expo mobile codebase. Native-device behavior, public hosting, clinical content, and legal documents still require review or verification. ZINC does not provide a diagnosis or a clinical assessment. Use fictional information for team testing.

## Features

- Account creation, sign-in, consent, profile setup, and safety screening.
- Suggested weekly schedules with editable days and strength rest-day checks.
- Optional extra activities, rescheduling, and skipping missed activities.
- Removal of unstarted activities after a recommendation warning. Started and finished activities retain their records; recommended weekly counts remain visible.
- A Today screen with a clear next action and a dated confirmation before starting another week.
- Strength, yoga, reasoning, and relaxation activity flows with saved feedback.
- A progress board with completion counts, recorded feedback, reasoning accuracy, and self-reported relaxation minutes.
- Optional chair-stand and balance records for comparison over time.
- Gemini coaching with distinct live-reply, fallback, and pending-proposal states, plus an adjustment preview that works without AI.
- Data export, account deletion, larger-text and high-contrast options, and a prominent Stop control.

## Architecture

```text
Expo / React Native interface
            │
            ▼
       FastAPI backend ───── Gemini API
            │                 (server-side key)
            ├── Deterministic rules engine
            └── SQLite database for local use
```

| Component | Technology |
| --- | --- |
| Interface | Expo SDK 58, React Native 0.88, React 19, TypeScript, Expo Router |
| Backend | Python 3.11, FastAPI, SQLModel |
| Local persistence | SQLite |
| Authentication | Argon2 password hashes and JWT bearer tokens |
| AI coach | Google Gen AI SDK and a configurable Gemini model |
| Verification | pytest, Node tests, TypeScript, ESLint, Playwright |

## Repository structure

```text
mobileApp/
├── mobile/              Expo interface, assets, and browser tests
├── backend/             API, account handling, and backend tests
│   ├── .env.example     Configuration template without credentials
│   ├── start_local.sh   Local API startup script
│   └── seed_demo.py     Fictional Maria demo seeder
├── core/                Rules engine, coach adapter, and exercise assets
├── render.yaml          Prepared backend deployment configuration
├── README.md            Mobile application guide
├── BACKEND_README.md    API guide
├── PRODUCT_NOTES.md     Build record, demo instructions, and known limits
├── DESIGN.md            Design system
├── DEPLOY_WEB.md        Web deployment handoff
├── privacy.md           Draft privacy policy
└── terms.md             Draft terms

app-protoype-presentation/  Earlier presentation prototype
DescriptionProject/        Project description documents
designColor/               Visual references
```

The current application is in **`mobileApp/`**. The earlier presentation prototype is separate.

## Run locally

### Requirements

- Git
- Python **3.11**
- Node.js **24** and npm
- A Gemini API key with access to the configured model, if testing the live coach

The commands below use a POSIX shell: macOS, Linux, or Windows through WSL. Native Windows PowerShell uses different environment-variable and virtual-environment commands; `start_local.sh` requires a POSIX shell.

### 1. Clone and install the backend

```sh
git clone https://github.com/alarconvv/ZINC_Hackathon2026.git
cd ZINC_Hackathon2026/mobileApp

python3.11 -m venv backend/.venv
backend/.venv/bin/python -m pip install -r backend/requirements.txt
cp backend/.env.example backend/.env
```

Copy the template only on first setup. Keep your existing `.env` when updating the code.

### 2. Configure the backend

Generate a private JWT secret:

```sh
backend/.venv/bin/python -c "import secrets; print(secrets.token_hex(32))"
```

Edit `mobileApp/backend/.env`. Paste the generated value into `JWT_SECRET`, and add your Gemini key:

```env
DATABASE_URL="sqlite:///backend/zinc.db"
JWT_SECRET="PASTE_YOUR_GENERATED_SECRET_HERE"
GEMINI_API_KEY="PASTE_YOUR_GEMINI_API_KEY_HERE"
MODEL="gemini-3.5-flash-lite"
CORS_ORIGINS="http://localhost:8081,http://127.0.0.1:8081"
```

The model is configurable and must be available to your Google account. Live coaching also requires available API quota. Keep the JWT secret stable across restarts to preserve existing logins.

**Never commit `.env`, API keys, JWT secrets, or a local database.** The repository ignores these files. Gemini credentials belong only on the backend; `EXPO_PUBLIC_API_URL` is public interface configuration and must never contain a secret.

### 3. Start the backend — terminal 1

From `ZINC_Hackathon2026/mobileApp/`:

```sh
sh backend/start_local.sh
```

The startup script loads `backend/.env`. The API creates its database tables automatically.

- Health check: <http://127.0.0.1:8000/health>
- API documentation: <http://127.0.0.1:8000/docs>

Port **8000** is the backend, not the application interface.

#### Run without Gemini

The local startup script requires a key and model. To test the saved-plan and rules-only features without Gemini, leave `GEMINI_API_KEY` and `MODEL` empty in `.env`, then run this instead from `mobileApp/`:

```sh
set -a
. ./backend/.env
set +a
backend/.venv/bin/python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --no-access-log
```

You still need a valid `JWT_SECRET`. AI messages use the labelled fallback response when Gemini is unavailable; the rules-only preview remains available after recording the required feedback.

### 4. Build and open the app — terminal 2

Start a second terminal from the cloned repository root:

```sh
cd mobileApp/mobile
npm ci
EXPO_PUBLIC_API_URL=http://127.0.0.1:8000 npm run build:web
cd ..
python3 mobile/scripts/serve_web.py
```

Open **<http://127.0.0.1:8081/>** and create an account. Both terminals must stay running. Press `Ctrl+C` in each terminal to stop the services.

For interface development with automatic reload, run the following from `mobileApp/mobile/` instead of building and serving the static export:

```sh
EXPO_PUBLIC_API_URL=http://127.0.0.1:8000 npm run web
```

Use only one interface server on port 8081 at a time.

### 5. Optional: create the populated Maria demo

From `mobileApp/`, set `DEMO_PASSWORD` to a password of at least ten characters and run:

```sh
DEMO_PASSWORD='replace-with-your-local-demo-password' backend/.venv/bin/python -m backend.seed_demo
```

Sign in as **`maria@demo.zinc`** using the password you chose. The seeder creates fictional activity records and preserves an existing demo account; running it again does not reset data or change the password. If you use a custom `DATABASE_URL`, export that same value before seeding.

See [Product notes](mobileApp/PRODUCT_NOTES.md) for the agreed demo credentials used by the browser test fixture. For a first-time setup demonstration, create a fresh account through the interface. Accounts created on another computer do not automatically exist on yours.

## Run with Docker (alternative)

With Docker Desktop running, teammates can run the API and web app without installing Python or Node. From the repository root:

```sh
docker compose up --build
```

Open **<http://127.0.0.1:8081/>** and create a fictional account, or sign in as `maria@demo.zinc` with the demo password in the [product notes](mobileApp/PRODUCT_NOTES.md). The API runs on port 8000.

- The first build downloads about 3 GB and takes several minutes. Keep at least 5 GB of disk free.
- Gemini is optional. For the live coach, create a `.env` file next to `docker-compose.yml` containing `GEMINI_API_KEY=...` and `MODEL=gemini-3.5-flash-lite`. The repository ignores `.env`. Without a key, the coach uses its labelled fallback.
- Both ports listen only on this computer. Stop other servers using ports 8000 or 8081 first.
- Press `Ctrl+C` to stop. `docker compose down` deletes the containers and their saved accounts and activity. Restarting the API signs everyone out unless `JWT_SECRET` is set in `.env`.

## Data and privacy during local testing

- Account and activity data persist in `mobileApp/backend/zinc.db` by default.
- Each computer has its own database. Pulling GitHub updates does not synchronize accounts or progress.
- Passwords are hashed. The local SQLite database itself is not encrypted by the app.
- The web interface stores its login token in browser local storage; native builds use SecureStore.
- Live coach requests send messages and tool-requested plan/feedback context to Google.
- Export and deletion controls are available in Settings. Keep testing data fictional.

## Run checks

Backend tests use temporary databases and stub the model; they do not call Gemini. From `mobileApp/`:

```sh
backend/.venv/bin/python -m pytest backend/tests -q
```

Interface checks, from `mobileApp/mobile/`:

```sh
npm run typecheck
npm run lint
npm test
```

Browser tests require the API and interface servers, a populated Maria fixture, and Gemini disabled for the offline expectations. Use an isolated test database and the fixture credentials in the product notes. From `mobileApp/mobile/`:

```sh
npx playwright install chromium
npm run test:e2e
```

These scenarios create and delete fictional test accounts. The latest recorded verification includes 30 backend tests, three interface logic/content tests, and six phone/desktop browser scenarios. Native-device checks remain outstanding.

## Working as a team

1. Clone the repository and create your own private `.env`.
2. Create a branch for each change and submit a pull request.
3. Review and merge changes, then run `git pull` to update local copies.
4. Rerun `npm ci` or the backend dependency installation when the corresponding dependency files change.
5. Rebuild the static interface after changing its code or API URL, or use development mode for automatic reload.

For shared testing through one link, deploy the backend and interface and use a shared hosted database. `mobileApp/render.yaml` and the [web deployment guide](mobileApp/DEPLOY_WEB.md) are preparation; a clone or GitHub push does not deploy the app. Codespaces configuration is not yet included.

## Troubleshooting

| Problem | Check |
| --- | --- |
| `ERR_CONNECTION_REFUSED` | Keep both servers running; open port **8081** for the app and `/health` on port **8000** for the API. |
| Port already in use | Stop the existing server before starting another instance. |
| Sign-in fails after cloning | The database starts empty. Create an account or seed the local demo. |
| Authentication is not configured | Set `JWT_SECRET` to a private value of at least 32 characters and restart the backend. |
| Coach shows a fallback | Check the backend key, model access, quota, and connection. A fallback does not apply a plan change. |
| Browser cannot reach the API | Check `EXPO_PUBLIC_API_URL` and the exact interface origin in `CORS_ORIGINS`; rebuild the static interface after changing its API URL. |
| A phone cannot reach `127.0.0.1` | On a phone, localhost refers to the phone. Follow the trusted-network and native-build guidance in the product notes. |

## Further documentation

- [Mobile application guide](mobileApp/README.md)
- [Backend and Gemini guide](mobileApp/BACKEND_README.md)
- [Product notes and known limits](mobileApp/PRODUCT_NOTES.md)
- [Design system](mobileApp/DESIGN.md)
- [Mobile build plan](mobileApp/CODEX_MOBILE_PRODUCT_PLAN.md)
- [Web deployment guide](mobileApp/DEPLOY_WEB.md)
- [Draft privacy policy](mobileApp/privacy.md) and [draft terms](mobileApp/terms.md)
