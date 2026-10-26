# ZINC mobile product build

Beta — content pending professional review. This build has had no clinical or legal review.

Work proceeds in plan order. Phase C is blocked until the Phase A/B end-to-end gate passes. The Streamlit app and its tests remain unchanged.

## Task record

- A1: scaffold the API and unchanged core bridge. Backend and unchanged Streamlit suites PASS.

- A2: add hashed accounts bearer tokens and login throttling. Backend and unchanged Streamlit suites PASS.

- A3: record explicit versioned health data consent. Backend and unchanged Streamlit suites PASS.

- A4: mirror profile screening and engine generated weekly plans. Backend and unchanged Streamlit suites PASS.

- A5: persist weekly scheduling activity logs and server safety locks. Backend and unchanged Streamlit suites PASS.

- A6: add bounded coach requests and explicit proposal acceptance. Backend and unchanged Streamlit suites PASS.

- A7: serve progress personal exports and complete account deletion. Backend and unchanged Streamlit suites PASS.

- A8: verify backend safety isolation persistence and all activity flows. Backend and unchanged Streamlit suites PASS.

## Expo runtime
Scaffold: Expo SDK 58 (expo ~58.0.19), React Native 0.88, TypeScript 6, Expo Router. Dependencies installed with expo install. SDK 58 transition: physical Expo Go clients must support SDK 58; otherwise use a development build. See https://docs.expo.dev/router/introduction/ .

- B1: scaffold Expo Router SDK 58 and typed secure API transport. Backend and unchanged Streamlit suites PASS.

- B2: build accessible aquatic design components and typography. Backend and unchanged Streamlit suites PASS.

- B3: connect accounts consent and one question safety onboarding. Backend and unchanged Streamlit suites PASS.

- B4: connect five tabs training coach proposals and progress board. Backend and unchanged Streamlit suites PASS.

## Cut-line gate
Above-cut-line browser gate PASS at 390×844 and 1280×900: UI register, consent and privacy link, seven-question safety screen, chosen days, plan, optional add/remove, twelve strength sets, unfinished Accept disabled, accepted next-week proposal, yoga, brain, relaxation, populated progress, rollover with reload, preferences, JSON download, Stop/423, deletion and Welcome. Offline coach fallback verified with provider credentials explicitly empty. No page errors or horizontal page overflow. Backend tests also verify stale safety messages override version conflicts. Phase C begins only after this gate and B5 commit.

- B5: finish account settings and verify the complete cut line. Backend and unchanged Streamlit suites PASS.

- C1: add contextual device local training reminders. Backend and unchanged Streamlit suites PASS.

- C1: test native reminder trigger mapping and time validation. Backend and unchanged Streamlit suites PASS.

- C2: record home tests and scoreboard without changing prescriptions. Backend and unchanged Streamlit suites PASS.

## Privacy wording clarification
The plan's blanket “no sharing” wording would hide the existing optional Gemini processing. The draft instead states no sale, advertising, analytics or sharing with other users, and explicitly discloses the Gemini request and relevant engine context. No sharing-consent checkbox is added. Contact, processor terms, backups and legal review remain human launch requirements. Policy reference: Washington RCW 19.373.020, read 2026-10-24.

- C3: add clearly marked draft legal pages and health data disclosures. Backend and unchanged Streamlit suites PASS.

## Fictional demo login
Demo email: `maria@demo.zinc`

Demo password: `mariademo12345`

These credentials are for fictional judge/demo use only. Never use this account for personal health information or on an unrestricted public service. The seed reads DEMO_PASSWORD from the environment; the password is documented only here, not embedded in the app or seeder. Existing demo data is never overwritten.

- C4: seed a fictional saved week using the unchanged engine. Backend and unchanged Streamlit suites PASS.

- C5: add reproducible ZINC app icon splash and placeholder identifiers. Backend and unchanged Streamlit suites PASS.

## Final verification
- D1: exact existing Streamlit unittest discovery command PASS: 93 tests in Python 3.11.9. Project .venv is absent, so the isolated /private/tmp/zinc-planner-venv was used. Full app/ diff against pre-product f7b5c9f is empty; engine.py, coach.py and app/tests/ were not edited.

- D2: verify relational integrity PostgreSQL readiness and private database errors. Backend and unchanged Streamlit suites PASS.

## Dependency audit (2026-10-24)
Npm audit reports 5 high advisories in the Expo CLI/development dependency chain (node-forge and Zod, including transitive Expo packages). node-forge 1.4.0 has no published patch; Expo CLI uses Zod 3, whose currently available release is still affected by the advisory. The suggested automated Expo 44 downgrade is not a valid SDK 58 fix. No forced override or downgrade was applied. These are toolchain findings; the FastAPI backend does not use either package. Do not expose the development server to untrusted networks or enable unreviewed OTA/code-signing flows. Recheck upstream fixes before public builds. Sources: https://github.com/advisories/GHSA-86w9-cpqp-85rv and https://github.com/advisories/GHSA-mrhx-c7xc-m3w5 .
- D3 web export: PASS, Expo SDK 58 static export to mobile/dist. TypeScript and lint PASS. New product source formatted; unused template assets and the template reset command removed. The export does not contain a live provider key. Toolchain audit findings are recorded separately above and are not represented as a clean security audit.

- D3: verify typed mobile source and production web export. Backend and unchanged Streamlit suites PASS.
- D4 final browser gate: 4 PASS at 390×844 and 1280×900. Both disposable-account flows cover register, consent/privacy, seven safety answers, chosen days, optional scheduling, all four activities, offline coach, unfinished Accept disabled, explicit accepted proposal, home-test saving, rollover/reload, persisted guide dismissal, export, Stop/423, deletion/Welcome. Both demo flows sign in and verify populated progress. Screenshots: mobile/e2e/screenshots/. Live provider access was explicitly disabled. Stop is also available above open sheets. Native notification delivery, native simulators/hardware and live Gemini were not tested.

- D4: verify saved product flows demo progress and modal safety access. Backend and unchanged Streamlit suites PASS.
- D4 visual-review fixes: compact two-column phone Today summaries, adjacent weekday/completion values for the chart, and selected-tab/heading assertions before screenshots. Initial Coach/Progress and large-text/high-contrast keyboard-focus captures added. Four browser scenarios PASS again after the fix batch. Web review verdict is recorded below when returned; native verification is still not established.

- D4: confirm the reviewed phone grid chart context and truthful captures. Backend and unchanged Streamlit suites PASS.
- Fresh Impeccable web verdict pass: all three original findings RESOLVED (Today grid/next action, chart day/count context, truthful Week captures). Initial Coach/Progress and large-text/high-contrast focus evidence inspected. This closes those screenshot/source findings at 390 and 1280 widths only; it is not a native, clinical, legal or comprehensive accessibility certification.

## Run locally

Run backend commands from `mobileApp/`. Python 3.11 and a Node release supported by Expo SDK 58 are required (verified here with Python 3.11.9 and Node 24.5.0).

### API

```sh
python3.11 -m venv backend/.venv
backend/.venv/bin/python -m pip install -r backend/requirements.txt
export JWT_SECRET="$(python3.11 -c 'import secrets; print(secrets.token_urlsafe(48))')"
export DATABASE_URL='sqlite:///backend/zinc.db'
export CORS_ORIGINS='http://localhost:8081,http://127.0.0.1:8081'
backend/.venv/bin/python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --no-access-log
```

Use a stable private JWT_SECRET in the server environment for saved logins across restarts. The example generates an ephemeral local secret; changing it invalidates tokens, while the account data remains in the database. SQLite is persisted at backend/zinc.db and ignored by Git.

To seed the fictional account, use the same DATABASE_URL, set DEMO_PASSWORD to the value in the Fictional demo login section above, and run in another terminal from `mobileApp/`:

```sh
backend/.venv/bin/python -m backend.seed_demo
```

The seeder requires DEMO_PASSWORD in the environment and preserves any existing demo account. It does not print the password. The demo is not auto-created when the API starts.

### App and web

In a separate terminal:

```sh
cd mobile
npm ci
EXPO_PUBLIC_API_URL=http://127.0.0.1:8000 npx expo start --web
```

For a static build:

```sh
cd mobile
EXPO_PUBLIC_API_URL=http://127.0.0.1:8000 npm run build:web
cd ..
python3 mobile/scripts/serve_web.py
```

Open http://127.0.0.1:8081 . The API must be running. Stop any other process on 8081 before starting Metro or the local static server. Only one is needed.

### Environment variables

- DATABASE_URL: server database; SQLite locally, PostgreSQL with psycopg supported by URL normalization. Live PostgreSQL was not exercised.
- JWT_SECRET: server-only signing secret, at least 32 characters, stable/private in hosting.
- GEMINI_API_KEY and MODEL: server-only optional Gemini configuration. Leave empty for the offline acceptance gate. No keys were added during this build.
- CORS_ORIGINS: comma-separated exact browser origins; update to the actual HTTPS web host before release.
- EXPO_PUBLIC_API_URL: public API base URL compiled into Expo. It contains no credentials.
- DEMO_PASSWORD: seeder/live-check input only; use the fictional demo value above for local judge use. No password is embedded in the mobile app.

### Checks

```sh
cd backend
.venv/bin/python -m pytest -q
cd ../mobile
npm run typecheck
npm run lint
npm test
npm run build:web
npx playwright install chromium
npm run test:e2e
```

Run the API with GEMINI_API_KEY and MODEL unset/empty for the browser test, since it verifies the offline fallback. Seed the fictional demo first. Install the matching Chromium version via Playwright. The implementation used isolated Python environments under /private/tmp; these are not repository dependencies.

Historical Streamlit commands (the original app/ folder is no longer present): With its own root .venv installed from app/requirements.txt, run `cd app && ../.venv/bin/python -m unittest discover -s tests -v` or `../.venv/bin/python -m streamlit run app.py --server.port 8507`.

## Delivered and limits

All Phase A, B and C features in the plan were implemented. Nothing above the cut line was cut. The above-cut-line gate passed before C1 began. Phase D: 93 unchanged Streamlit tests, 20 backend tests, three mobile logic/content tests, TypeScript/lint, static web export and four phone/desktop browser scenarios pass. The fresh web review resolved its three original findings; it does not certify the whole product.

This is a Beta with content pending professional review. No clinical or legal review is complete. Draft contacts, provider arrangements, retention/backup practices, operational controls and legal rights handling must be completed by the operator before public release. SQLite is not encrypted by this code. There is no email verification, password recovery, refresh-token flow, multi-worker login throttle, migration framework or backup/recovery workflow. Do not interpret the completion gauge as a health measure. Home tests only record user-reported results and never change prescriptions.

No usable iOS simulator was available (`simctl` absent), and adb was absent. Actual native UI/keyboard, large OS text, gestures, notification permission/delivery, signed builds and store review remain unverified. Expo SDK 58 needs a compatible Expo Go client; a development build may be needed during SDK transitions. Reminders are local only and resync with changed days when the app opens; no server push exists. The fixed engine scheduling timezone is unchanged. Live Gemini, hosted PostgreSQL, public hosting and deployment were not tested. Five high Expo toolchain dependency advisories remain documented above.

Real exercise videos, server push, device health-platform integrations, human coaches, a clinician portal, payments, the full PAR-Q+, Spanish and store submission remain outside the supplied plan. The referenced ZINC_Product_Description.md was not present under that exact filename; existing app copy and evidence sources were used without adding new health-outcome claims.

Human preparation handoffs are recorded in H1–H4 below as they are completed. No hosting, store submission or live-provider check is performed by those preparation tasks.

- D5: run guides, environment variables, demo instructions, verified results, scope and known limits documented. Mobile design tokens and components recorded in mobileApp/DESIGN.md and its validated JSON sidecar; root Streamlit design preserved.

## H1 — Backend hosting preparation

Prepared backend/Dockerfile, mobileApp/render.yaml and a secret-safe .dockerignore. The image runs as a non-root user and imports the unchanged app core. It has no live keys. When DEMO_PASSWORD is set, it creates the fictional demo account at startup without overwriting an existing one. Use a persistent managed PostgreSQL DATABASE_URL for hosting; an ephemeral container SQLite file is not durable hosting. Set the exact HTTPS web origin in CORS_ORIGINS. Render can generate JWT_SECRET when the human applies the blueprint. GEMINI_API_KEY and MODEL remain human-entered server secrets.

Local container preparation, if Docker is available:

```sh
# From the repository root (one level above mobileApp):
docker build -f mobileApp/backend/Dockerfile -t zinc-api .
```

Do not apply the Render blueprint or expose personal health data until the operator completes the known launch requirements. No backend service was deployed. The .env.example is documentation only and has empty secret placeholders; the application reads environment variables directly.

H1 checks: Docker command shell syntax, required hosting variables and ignore rules PASS. Docker image build was not run: the local Docker daemon is unavailable. No daemon was started and no deployment was attempted.

## H2 — Phones and Expo Go preparation

Use a trusted local network. The phone and computer must be able to reach each other. Start the API from `mobileApp/` with the same environment as above, changing its bind address for this local phone check:

```sh
backend/.venv/bin/python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --no-access-log
```

Find your computer's LAN IP address. In a separate terminal, replace COMPUTER_LAN_IP below, then run:

```sh
cd mobile
EXPO_PUBLIC_API_URL=http://COMPUTER_LAN_IP:8000 npx expo start
```

Open a compatible Expo Go release on iPhone or Android. Scan the terminal QR code (iPhone Camera or Expo Go's scanner). Allow local-network access if the OS requests it. The API address must be the computer's address; 127.0.0.1 on the phone points back to the phone. Do not expose the development server or an unaudited beta on an untrusted network.

This app uses SDK 58. Check the current Expo Go SDK support before trying the QR flow. During a transition, a compatible development build may be needed; that requires human native-build setup and, for cloud builds, an Expo account and signing choices. No EAS build profile, signing credentials, remote build or store submission was created. Before a distributable build, replace com.zinc.coach with identifiers you control and configure an HTTPS API URL in the build environment. Reference: https://docs.expo.dev/router/introduction/ .

On actual iPhone and Android, verify safe areas, keyboard movement, system text scaling, Back/edge gestures, Stop while scrolling and inside sheets, and local notification permission/delivery. Notification permission should appear only after Enable reminders. Web hides reminders. These device checks remain a human handoff, not a reported pass.

## H3 — Web link preparation

mobileApp/DEPLOY_WEB.md documents building mobile/dist with the actual HTTPS API origin, uploading it to a static host, preserving route and asset files, configuring extensionless links and exact backend CORS, and rerunning the acceptance checks. The local static helper is not a public server. No host account, public URL, upload or deployment was created. Build output and API keys are not committed.

## H4 — Live coach preparation

backend/verify_live.py is a human-run check against the chosen backend. It signs in to the fictional demo, requests an explanation, requires a new coach_success event (not fallback), and verifies that current/staged prescriptions are unchanged. It never accepts or declines a proposal and never rolls the week. The request is saved to the demo's coach history. Do not use a personal account. It does not send provider keys from the client; the human must configure GEMINI_API_KEY and MODEL on the backend first.

After the human seeds the fictional account on the chosen backend, one command from `mobileApp/` is:

```sh
ZINC_API_URL='https://YOUR_API_HOST' DEMO_EMAIL='<demo email above>' DEMO_PASSWORD='<demo password above>' backend/.venv/bin/python -m backend.verify_live
```

Replace the host and the two credential placeholders with the Fictional demo login values above. Keep the credentials in your local environment; do not copy them into the mobile bundle or public logs. A normal successful result is JSON with status PASS, stage live_coach, plan_unchanged true and proposal_pending false. If the model creates a validated pending proposal, proposal_pending is true; no change is accepted. Missing configuration returns BLOCKED/exit 2. A failed request, provider fallback or changed prescription returns FAIL/exit 1. PASS exits 0. Remote HTTP origins are refused; localhost HTTP is allowed for local checks.

Only the checker tests with a fake client were run. No real provider request, deployed service check, key entry, push, publication or store submission was performed. Existing demo state is not reset to make this check pass; a stopped account remains stopped.

- H4: prepare a human live coach check with no automatic acceptance. Backend and unchanged Streamlit suites PASS.

## Final local preview
All 27 task/preparation commits are present in plan order, one per task. Final totals after the handoff tests: 93 unchanged Streamlit tests, 22 backend tests and three mobile tests PASS; TypeScript/lint, static web export and four browser scenarios PASS. The three original web review findings are resolved.

The local web preview is http://127.0.0.1:8081 and the API is http://127.0.0.1:8000 . The running API uses ignored backend/zinc.db (local permissions 0600), freshly seeded fictional Maria and an ephemeral server-only JWT secret. No provider key is configured. The Streamlit fallback remains at http://127.0.0.1:8507 if its prior process is still running. No app/ file was changed.

Native devices, the Docker image build, hosted PostgreSQL, live Gemini and actual deployment remain unverified. Docker daemon, simctl and adb availability limits are recorded above. Five Expo toolchain advisories remain. Human steps were prepared only.


## Folder consolidation

The mobile UI, API, local database and render.yaml now live in mobileApp/. Run current backend commands from mobileApp/ and UI commands from mobileApp/mobile/. The original app/ folder was no longer present during consolidation; core/ contains exact copies of its last committed engine.py, activities.py, coach.py, progress_board.py and required exercise assets. The backend and Docker image import this bundled core. Earlier task records describe the historical layout.

Consolidation checks: 22 backend tests, 3 mobile tests, TypeScript, lint and static export PASS. Both disposable-account browser flows PASS. The two populated-demo checks fail their fixed 75% expectation because the saved demo has advanced beyond its seeded week; its database was preserved rather than reset. Docker was not built. Local preview processes were restarted; the temporary JWT secret changed, so existing users may need to sign in again.


## First-time setup demo

Demo email: `first@demo.zinc`

Demo password: `1time12345`

Fictional local account for testing initial setup. Sign out of Maria, sign in with this account, then complete consent, profile, safety screening and day selection to create its first week. No consent, screening answers, plan or activity records were pre-filled. Setup is saved after completion; signing out does not reset it. Do not use real health information.


## Live Gemini connection — 2026-10-24

The local backend now loads the private Git-ignored backend/.env via backend/start_local.sh. GEMINI_API_KEY remains server-only; a stable JWT_SECRET is stored privately in the same file. The active model is gemini-3.5-flash-lite. The first model encountered a provider 503 and timeouts; a subsequent isolated tool-call succeeded, and the full backend.verify_live check returned PASS with Maria’s fictional account, plan_unchanged true and proposal_pending false. No proposal was accepted and no cloud service was deployed. Provider latency or quota failures can still trigger the existing fallback. Restart with sh backend/start_local.sh from mobileApp/ (or set PYTHON_BIN to the installed backend Python). Never print or commit backend/.env.


## Weekly usability improvements — 2026-10-24

Implemented suggested schedules before editing, next-week date previews and confirmation, optional-feature explanations, a single next action at the top of Today, missed-day reschedule/skip recovery, coach source and fallback status, and plain-language progress counts. Week also allows removing unstarted baseline or extra activities after a recommendation warning. Removal carries into future weeks; Add activity can add a session back. Started and finished activities keep their records; skipping retains partial results. Recommended counts remain visible separately from the chosen schedule. Initial plan generation and strength rest-day limits remain enforced. The Week reload loading gate now preserves the current tab while session data loads.

Verification: 30 backend tests, 3 mobile logic/content tests, TypeScript, lint and web export PASS. Six browser scenarios PASS at 390px and 1280px against an isolated temporary database with Gemini disabled. Confirmed screenshots cover Today, recommendation/removal warnings and next-week confirmation. The local app is published at port 8081 and retains its private Gemini configuration and existing account data. Native devices were not tested.
