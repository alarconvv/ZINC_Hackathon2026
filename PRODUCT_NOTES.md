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

Demo password: `Foju1NC4JWjXnQcvzz54njQz`

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

Run backend commands from the repository root. Python 3.11 and a Node release supported by Expo SDK 58 are required (verified here with Python 3.11.9 and Node 24.5.0).

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

To seed the fictional account, use the same DATABASE_URL, set DEMO_PASSWORD to the value in the Fictional demo login section above, and run in another terminal from the repository root:

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

The Streamlit fallback is unchanged. With its own root .venv installed from app/requirements.txt, run `cd app && ../.venv/bin/python -m unittest discover -s tests -v` or `../.venv/bin/python -m streamlit run app.py --server.port 8507`.

## Delivered and limits

All Phase A, B and C features in the plan were implemented. Nothing above the cut line was cut. The above-cut-line gate passed before C1 began. Phase D: 93 unchanged Streamlit tests, 20 backend tests, three mobile logic/content tests, TypeScript/lint, static web export and four phone/desktop browser scenarios pass. The fresh web review resolved its three original findings; it does not certify the whole product.

This is a Beta with content pending professional review. No clinical or legal review is complete. Draft contacts, provider arrangements, retention/backup practices, operational controls and legal rights handling must be completed by the operator before public release. SQLite is not encrypted by this code. There is no email verification, password recovery, refresh-token flow, multi-worker login throttle, migration framework or backup/recovery workflow. Do not interpret the completion gauge as a health measure. Home tests only record user-reported results and never change prescriptions.

No usable iOS simulator was available (`simctl` absent), and adb was absent. Actual native UI/keyboard, large OS text, gestures, notification permission/delivery, signed builds and store review remain unverified. Expo SDK 58 needs a compatible Expo Go client; a development build may be needed during SDK transitions. Reminders are local only and resync with changed days when the app opens; no server push exists. The fixed engine scheduling timezone is unchanged. Live Gemini, hosted PostgreSQL, public hosting and deployment were not tested. Five high Expo toolchain dependency advisories remain documented above.

Real exercise videos, server push, device health-platform integrations, human coaches, a clinician portal, payments, the full PAR-Q+, Spanish and store submission remain outside the supplied plan. The referenced ZINC_Product_Description.md was not present under that exact filename; existing app copy and evidence sources were used without adding new health-outcome claims.

Human preparation handoffs are recorded in H1–H4 below as they are completed. No hosting, store submission or live-provider check is performed by those preparation tasks.

- D5: run guides, environment variables, demo instructions, verified results, scope and known limits documented. Mobile design tokens and components recorded in mobile/DESIGN.md and its validated JSON sidecar; root Streamlit design preserved.
