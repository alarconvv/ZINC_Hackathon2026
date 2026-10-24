# Current folder layout

The implemented `backend/`, `mobile/` and `render.yaml` now live together in `mobileApp/`. Historical paths below are relative to `mobileApp/`. The original Streamlit `app/` was subsequently removed outside this move; unchanged rules and required assets are now bundled in `core/`. Run the current commands in README.md and BACKEND_README.md.

# ZINC — Mobile product plan (for Codex)

## Your job

Turn ZINC from a Streamlit demo into a product-shaped app in about **2 days**:

- **`backend/`:** a FastAPI service that wraps the existing, tested rules engine and coach. It adds user accounts and saved data.
- **`mobile/`:** an Expo (React Native, TypeScript) app for iPhone and Android that also exports to the web, so it can be opened from a link.

The Streamlit app in `app/` stays untouched as a fallback demo. **Do not move, rename or edit `app/engine.py`, `app/coach.py` or `app/tests/`.** The backend imports them.

Work in the order given. Each task = one commit (`product(<id>): …`). Everything above the **cut line** must work end to end before anything below it is started. If you run short of time, stop at the cut line, make sure it all works, and write what's left in `PRODUCT_NOTES.md`.

Tasks marked **[Human]** need Viviana (keys, accounts, publishing). Do only the preparation for those, then stop.

## Reference material (read first)

- `app/app.py`: the reference implementation of every user flow (onboarding, safety screen, focus/days, week, train for all four sections, coach, accept/decline, next week, progress, export). Mirror its behaviour and wording.
- `app/engine.py`: all decisions. Functions used by `app.py` include: `new_state`, `MARIA`, `QUESTIONS`, `safety_check`, `assign_tier`, `make_week`, `choose_days`, `AVAILABLE`, `WEEKDAYS`, `change_schedule`, `start_activity`, `active_session`, `log_set`, `log_yoga`, `current_puzzle`, `answer_puzzle`, `finish_activity`, `stop`, `STOP_MESSAGE`, `red_flag`, `progress`, `check_change`, `accept_pending_change`, `decline_pending_change`, `start_next_week`, `prescription`, `eligible`, `event`. Read their real signatures. Don't trust this list blindly.
- `app/coach.py`: `coach_turn(message, state, secrets)` returns an already-filtered string.
- `app/progress_board.py`: Progress screen summaries (`summarize`, `feedback_rows`, `date_range`).
- `app/content/exercises.csv` and `app/content/img/`: exercise content and placeholder illustrations.
- `DESIGN.md` and `app/aquatic.css`: colours, radius, the card/gauge look. Use sea-blue `#126bc5`, deep ocean `#063774`, pale surface `#f4faff`, ink `#12365b`, muted `#526b84`, rule `#d6e7f5`, radius 24, Manrope headings, DM Sans body.
- `ZINC_Product_Description.md` (claims we make and avoid) and `CODEX_POLISH_PLAN*.md` (UI decisions already made).

## Guardrails — must not change

1. **All decisions stay on the server, inside `engine.py`.** These are plans, prescriptions, progression, the 10% cap, the pain ≥ 4 rule, safety results and scheduling limits. The mobile app only displays what the API returns. It never computes or edits a prescription.
2. **Stop.** A Stop control is visible on every screen once a plan exists. It calls `POST /stop`, which runs `engine.stop`. After a stop, every activity and coach endpoint returns 423 Locked, and the app shows `STOP_MESSAGE`. Symptom text goes through `engine.red_flag` on the server, during training and in coach messages.
3. **Coach.** Only `coach.coach_turn` produces coach text. Never call Gemini from the app. Render coach text as plain `<Text>`: no Markdown, HTML, links or images. A proposed change is shown as a card. It is applied only by an explicit `POST /proposal/accept` from the user, and Accept is refused while activities are unfinished, exactly as in `app.py`.
4. **Claims.** Never write "prevents Alzheimer's", dementia-risk numbers, "treats", "detects" or "improves memory" anywhere: UI, store text, notifications or README. The weekly gauge is a completion %, never a health score.
5. **Safety screen and clinician gate.** Use the same `QUESTIONS` and `safety_check`. The "see a clinician first" result and the age 80+ / MCI sign-off rule block plan creation, exactly as in `app.py`.
6. **Privacy.** No third-party analytics, ad SDKs or crash reporters that send health data. Never log health fields or coach text in plain server logs. Passwords are hashed with argon2 or bcrypt. Secrets come only from environment variables.
7. **Honesty about status.** This build has had no clinical or legal review. Keep a visible "Beta" label. Onboarding includes a consent screen and a note that the content is pending professional review. Draft legal pages are marked "Draft — pending legal review."
8. Keep the existing `app/` test suite passing (`cd app && ../.venv/bin/python -m unittest discover -s tests -v`).

## Architecture

```
backend/              FastAPI + SQLModel + SQLite (Postgres-ready via DATABASE_URL)
  main.py             app, routers, CORS
  deps.py             auth dependency, DB session, state load/save
  auth.py             register / login / JWT
  routes/*.py         onboarding, plan, activities, coach, progress, account
  state_store.py      per-user engine state (JSON) with optimistic version
  seed_demo.py        creates the demo user "maria@demo.zinc" (fictional)
  tests/              pytest + FastAPI TestClient
mobile/               Expo + expo-router + TypeScript
  app/(auth)/…        welcome, sign in, register, consent
  app/(onboarding)/…  profile, safety, result, focus & days
  app/(tabs)/…        today, week, train, coach, progress
  app/settings/…      account, privacy, text size, reminders, about
  src/api.ts          typed client; src/theme.ts tokens; src/components/*
```

**State model (fastest safe path):** store each user's whole engine state dict (the same object `app.py` keeps in `st.session_state.zinc`) as JSON in a `user_state` row with a `version` integer. Every mutating endpoint does: load → call the engine function → save with `version + 1`. A version mismatch returns 409, and the app refetches. This reuses the engine unchanged. Also store `events` in their own table for audit.

## Phase A — Backend (about 6 hours)

**A1. Scaffold.**
Python 3.11 project in `backend/` with `requirements.txt`: fastapi, uvicorn, sqlmodel, passlib[argon2] or bcrypt, python-jose or pyjwt, google-genai (same version as `app/requirements.txt`), pytest, httpx. Make `app/` importable (`sys.path` insert in one place, `backend/zinc_core.py`, which re-exports `engine`, `coach`, `progress_board`). Add `GET /health`.

**A2. Accounts.**
`POST /auth/register` (email, password ≥ 10 chars, first name), `POST /auth/login` → access JWT (24 h). Use `Authorization: Bearer`. Rate-limit login attempts in memory (5 per minute per email). Return the same error message for unknown email and wrong password.

**A3. Consent records.**
`POST /consent` stores `{collect_health_data: true, version, timestamp}`. This consent is required before any onboarding endpoint works. There is no data sharing, so there is no sharing consent to collect; record that fact in the privacy page instead.

**A4. Onboarding endpoints.**
- `PUT /profile`: name, age, level, limits, MCI, clinician sign-off.
- `GET /safety/questions`.
- `POST /safety`: returns `cleared` / `cleared_limits` / `clinician`, plus the sign-off block. This uses the same logic and messages as `app.py`.
- `POST /plan`: start Monday, chosen days and toggles. Calls `make_week` and `choose_days`, and returns the plan. Validation errors from the engine come back as 422 with the engine's message.

**A5. Week and activity endpoints.**
`GET /plan`, `POST /schedule` (move, add or remove, via `change_schedule`), `POST /activities/{id}/start`, `GET /activities/active`, `POST /activities/active/set` (reps, effort, pain), `POST /activities/active/pose`, `GET /activities/active/puzzle`, `POST /activities/active/answer`, `POST /activities/active/finish` (skipped or minutes), `POST /symptoms` (`red_flag` → stop), and `POST /stop`. Every response includes the updated summary the screen needs, so the app never recomputes anything.

**A6. Coach and proposals.**
`POST /coach` with `{message}` calls `coach.coach_turn` using `GEMINI_API_KEY` and `MODEL` from the environment. It returns `{reply, pending_change}`. Add `POST /proposal/preview` (the rules-only path from `app.py`), `POST /proposal/accept`, `POST /proposal/decline` and `POST /week/next`. Add a 30-second server timeout. If the coach fails, return the app's friendly fallback text.

**A7. Progress and account.**
`GET /progress?week=n` returns the `progress_board.summarize` output plus reasoning accuracy, relaxation minutes, feedback rows and accepted changes. `GET /account/export` returns all of the user's data as JSON. `DELETE /account` hard-deletes the user, their state, events and consents, and returns 204.

**A8. Backend tests.**
pytest with TestClient and a temporary SQLite database. Cover:
- register → consent → screen → plan → start strength → log set → finish.
- `/stop` locks every activity and coach endpoint (423).
- Symptom text with "chest pain" stops the session.
- A `clinician` result blocks `/plan`.
- Accept is refused while activities are unfinished.
- Another user's token can't read or change state (no cross-user access).
- Export contains the user's data; delete removes everything.
- A version conflict returns 409.

Use a stub coach runner, with no network in tests.

## Phase B — Mobile app (about 8 hours)

**B1. Scaffold.**
`npx create-expo-app@latest mobile --template` (TypeScript, expo-router). Record the Expo SDK version in `PRODUCT_NOTES.md`. Add `@expo-google-fonts/manrope`, `@expo-google-fonts/dm-sans`, `react-native-svg`, `expo-secure-store` (token storage; `localStorage` fallback on web), `expo-notifications`, and `@expo/vector-icons`. Put the API base URL in `app.config` / `EXPO_PUBLIC_API_URL`.

**B2. Design system (`src/theme.ts`, `src/components/`).**
Build from the tokens above: `Screen` (deep-blue gradient background), `Card` (pale surface, radius 24), `Button` (primary / secondary / danger, minimum 48pt), `Chip` (status), `EvidenceBadge` (Strong / Moderate / Emerging evidence, always with the word), `Ring` (SVG completion ring), `StopButton`, `SectionHeader` (small caps label), and `Meta` (muted line). Respect the OS text size (`allowFontScaling`) and reduced motion. Give every interactive element an `accessibilityLabel` and `accessibilityRole`.

**B3. Auth and onboarding.**
- **Welcome:** "Strength for the years ahead", three benefit lines, "Create account", "Sign in".
- **Register, then Consent:** a plain explanation of what is stored and why, a link to the privacy page, a required checkbox and the "Beta — content pending professional review" note.
- **Onboarding:** Profile → Safety, one question per screen with large Yes/No buttons and a progress bar → Result card → Focus & days → "Create my week".

**B4. Tabs.**
Use a bottom tab bar with icons: Today, Week, Train, Coach, Progress. A `StopButton` sits in the header on every tab. While a training session is active, it becomes a full-width bar under the header.

- **Today:** greeting, four section cards with rings and each section's next day, a "Next activity" card with a Start or Resume button, and a "How ZINC works" card on the first visit only.
- **Week:** agenda rows with a date block, name, status chip, evidence badge and minutes, plus a Start button. Long-press or ⋯ opens Reschedule. There is also an "Add activity" sheet.
- **Train:**
  - Strength: illustration, name, prescription, cue, power tag, easier/harder chips (display only), and a "Why this exercise?" sheet with the source. Logging uses steppers for reps, effort 1–10 and pain 0–10, then a 60-second rest timer.
  - Yoga: pose cards with effort and pain.
  - Brain: a puzzle with a number pad.
  - Relaxation: an animated breathing circle on a 10-second cycle, with 3 or 5 minutes and a self-reported "Done".
  - The symptom field is always shown during a session.
  - The completion screen shows a check icon, "Nice work, {name}", the counts, what's next, and the pain ≥ 4 warning when it applies.
- **Coach:** chat bubbles (coach text as plain `Text`), prompt chips, a typing indicator while waiting, a typing effect over the returned text, a proposal card with Accept / Decline, and "Adjust without AI".
- **Progress:** a week picker, a date rail, the completion gauge (SVG), section counts, the activity curve (SVG), reasoning accuracy with its answer count, self-reported relaxation minutes, and expandable feedback.

**B5. Settings.**
- Account: name, email, sign out.
- **Download my data:** saves or shares the export JSON.
- **Delete my account:** a confirmation sheet, then `DELETE /account`, then back to Welcome.
- Text size override, high contrast, About & evidence, Privacy policy, Terms.

## — Cut line: everything above must work end to end —

## Phase C — Product finish (about 4 hours)

**C1. Reminders.**
Use local notifications (`expo-notifications`) on the user's training days at a chosen time: "Your strength session is today." Permission is asked in context, not at launch. On web, hide the setting.

**C2. Home strength test (record and trend only).**
Add a 30-second chair-stand counter (big tap target, countdown, reduced-motion safe) and a single-leg balance timer. Results are saved through a new `POST /tests` endpoint that **stores them only**. They don't change the plan; that rule doesn't exist yet in the engine. Show the history on Progress as "Your scoreboard," with a "Retest due" card after 8 weeks.

**C3. Draft legal pages.**
Write `mobileApp/privacy.md` and `mobileApp/terms.md` in plain language, marked "Draft — pending legal review". Cover what is collected, why, retention, no sale and no sharing, how to export and delete, and a contact address placeholder. Add a separate "Consumer Health Data Privacy Policy" section, since Washington's My Health My Data Act requires one. Don't claim compliance with any law.

**C4. Demo account and seed.**
`backend/seed_demo.py` creates a fictional Maria (52, beginner, knee limitation, Protect tier) with one week of realistic logged activity, so judges can sign in and see a populated app. Put the credentials only in `PRODUCT_NOTES.md`.

**C5. App identity.**
Create a 1024×1024 icon (white ✳ on `#126bc5`, generated with vector shapes, no fonts), a splash screen in deep ocean, app name "ZINC", and a bundle id placeholder `com.zinc.coach`.

## Phase D — Verify and hand off (about 2 hours)

1. `cd app && ../.venv/bin/python -m unittest discover -s tests -v` passes (Streamlit app untouched).
2. `cd backend && pytest -q` passes.
3. `cd mobile && npx tsc --noEmit` passes, and `npx expo export --platform web` builds.
4. Run the backend locally, serve the web export, and run a Playwright smoke test (`mobile/e2e/smoke.spec.ts`) at 390×844 and 1280×900. Cover: register → consent → screen → plan → strength set → Stop locks the app; sign in as the demo user and check that Progress shows data; export downloads; delete returns to Welcome. Save screenshots to `mobile/e2e/screenshots/`.
5. Write `PRODUCT_NOTES.md`: how to run the backend and app, environment variables, the demo login, the Expo SDK version, what was cut, and known limits (no clinical or legal review, SQLite, local notifications only).

## [Human] steps to prepare, not perform

- **Backend hosting:** add a `backend/Dockerfile` and a `render.yaml` (or a Fly.io `fly.toml`) using `DATABASE_URL`, `JWT_SECRET`, `GEMINI_API_KEY` and `MODEL`. Don't deploy.
- **Phones:** document `npx expo start` and the Expo Go QR flow. Optionally add `eas.json` for later builds. Don't submit to any store.
- **Web link:** document deploying `mobile/dist` to a static host.
- **Live coach:** document a one-command check against the deployed backend using the demo user.

## Out of scope

Real exercise videos, server push notifications, Apple Health / Google Health Connect, human coaches, clinician portal, payments, the full PAR-Q+ (licensing and wording need review; keep the existing shortened questions and the caveat), Spanish, store submission, HIPAA-grade hosting, and any new engine rule.
