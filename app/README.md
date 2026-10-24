# ZINC complete weekly prototype

## Run

From the project folder:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r app/requirements.txt
.venv/bin/python -m streamlit run app/app.py
```

Or create a Python 3.11+ virtual environment first. Configuration and secret templates are in the project-root `.streamlit` folder. Set `GEMINI_API_KEY` and `MODEL` in `.streamlit/secrets.toml` or Streamlit Cloud secrets; never commit the secrets file. The three model tools are `get_plan`, `get_last_session`, and `propose_change`. No model tool can apply a prescription. Missing configuration returns a clearly labelled fallback. Real model interaction and public deployment require separate verification.

## Journey

Load Maria → profile → complete safety screen → focus → dated four-section week → independently start/resume each activity → coach check-in → accept or decline next-week changes → progress and export → Start next week.

All plans include strength/balance, yoga, reasoning games and relaxation. The age-tier schedule is the starting suggestion; users can choose other baseline weekdays during onboarding. Other sections default to Tuesday and Saturday. Extra yoga adds Sunday yoga; Extra brain and relaxation adds Sunday games and breathing. Both focus toggles start off. Restrictions select supported yoga versions. The bank contains 24 reasoning puzzles across four levels, with three consecutive correct answers raising difficulty and two misses lowering it. Each session has five questions. Breathing uses a ten-second cycle, a three- or five-minute selection and reduced-motion instructions. Completed relaxation minutes are self-reported, not measured by a timer. Quick look is explicitly a mockup; home tests remain planned.

Sessions have unique IDs and dated activity IDs, independent resume positions, feedback and completion status. Partial and skipped work is not counted as completed. Stop locks all activity and coach paths. Pain >=4 ends the affected strength exercise or yoga activity and blocks harder/same progression. A weekly cap of 10% applies to repetitions or core-hold seconds with sets and versions fixed; smaller integer baselines hold steady when a single count would exceed 10%. No weights or loads are adjusted.

Accept stages next-week prescriptions and invalidates stale proposals without rewriting current-week counts. Start next week archives the prior plan, activates staged changes, resets per-week baselines and keeps all session history. Complete/end unfinished activities before acceptance or rollover. Previous-week feedback cannot drive new progression.

Progress shows section completion, session status, pain/effort records and charts, reasoning accuracy/level, relaxation minutes and accepted changes. History lives only in `st.session_state`; refreshing, reconnecting or restarting can lose it. Export before leaving. Load Maria resets everything and does not bypass screening. No accounts or durable storage are implemented.

## Verify

```sh
cd app
../.venv/bin/python -m unittest discover -s tests -v
```

October 23 engineering verification: **66 tests passed**, no failures or skips. Independent audit and review fixes are recorded in `verification/audit.md`; all 20 specification scenarios and M0–M8 gates are mapped in `verification/gates.md`. Machine-readable local/external gate status is in `verification/checks.json`.

Runtime pins are Streamlit 1.66.1, Google GenAI 1.47.0 and Pillow 13.0.0. `requirements.lock.txt` records all 49 tested Python 3.11/macOS runtime packages. `pip check` passes; the strict point-in-time advisory scan found no known vulnerabilities. Install `requirements.txt` on other platforms and repeat the scan/tests for that platform.

The isolated browser gate in `tests/browser_gate.cjs` passed at desktop 1280×900 and phone 390×844: real onboarding and all players, keyboard activation, normal/reduced-motion breathing, control/alert colors, export download/parse, second-week/historical progress, no page errors and no horizontal page overflow. These are simulated viewports, not physical-device claims. Test screenshots and results are in `verification/browser/`.

To reproduce browser checks with Node and Playwright installed, start Streamlit locally and run:

```sh
ZINC_TEST_URL=http://127.0.0.1:8505 node tests/browser_gate.cjs
```

If Playwright is supplied by the Codex runtime instead of a normal Node install, set `ZINC_PLAYWRIGHT_PATH` to its package path and use the bundled Node executable; `PLAYWRIGHT_BROWSERS_PATH` can point at the downloaded test browser. These are development tools, not application dependencies.

For a real provider check, configure the ignored project-root `.streamlit/secrets.toml`, then run `../.venv/bin/python verification/verify_live.py` from `app/`. This opt-in test uses fictional Maria data and makes bounded live API calls. It writes only sanitized events/results, never keys or raw provider exceptions. Missing configuration is explicitly BLOCKED (exit 2). Live Gemini, public hosting, physical devices, provider account controls and human deliverables are still separate release gates.

## Sources and limits

The merged build specification is `ZINC_App_3-Day_Build_Plan_V261023.docx` in the parent folder. Exercise and evidence source labels come from the supplied project documents and have not been independently clinically reviewed. All activity prescriptions are fictional prototype policies. The shortened PAR-Q+-style screen is not the full validated questionnaire. Symptom matching and output filtering cannot understand every wording or guarantee safety. General wellness, not medical advice; fictional data only.

The model receives the fictional plan and activity history. Keys and raw provider errors never enter event logs. The adapter bounds turns to four requests/eight tools, uses a sixty-second timeout per request and disables retries. This is not a sixty-second total guarantee. Account-wide spending caps must be configured with the provider. The UI keeps the existing blue visual identity.

## Aquatic Progress board

The redesigned Progress screen uses a dated week selector, seven-day rail, circular scheduled-activity completion gauge, four-section completion summary, and an accessible SVG area curve of completed activities by scheduled day. All values come from recorded demo state; partial/skipped activities are not counted as completed. The curve is participation, not a strength/health outcome or a time-of-day forecast. Earlier-week comparison states actual completion counts and totals.

Reasoning accuracy includes answer count; relaxation minutes remain self-reported. Detailed activity status, contextual pain/effort observations, accepted prescription changes, and diagnostics are available in expandable sections. Unlike movements are no longer joined as a single feedback trend. Export explicitly includes all demo history. The bottom navigation retains native radio semantics, visible focus, and reserved space above the page end and chat composer.

Presentation helpers live in `progress_board.py`; `aquatic.css` supplies the shared aquatic surfaces and responsive dock. `DESIGN.md` records the visual decisions. The earlier aquatic-UI run passed 66 tests; the flexible planner follow-up passes 75 tests. The existing browser regression suite passed at desktop 1280×900 and phone 390×844, including export, historical-week selection, keyboard navigation, reduced motion, no page errors and no horizontal page overflow. Captures are in `verification/browser/`.

## Live Gemini integration follow-up

The adapter now allows sixty seconds per request, still with retries disabled and at most four requests/eight tool calls. This is not a sixty-second end-to-end guarantee. Function responses preserve the provider's function-call IDs, and output is bounded to 1,600 tokens per request. Sanitized model finish categories and fallback status codes help distinguish failures without recording provider error text or credentials.

A real Gemini read/propose/accept test passed on October 23, 2026. The `verification/verify_live.py` additionally checks Decline, clicks the real Streamlit Accept control using AppTest, and verifies next-week activation/history. The enhanced gate passed with a 15.4-second coach turn: active 10, staged next week 11, rollover 11 with prior history retained. See `verification/live-model.json` and `verification/adapter-followup.md`. The local 66-test suite passed after the adapter changes. Provider response time and availability vary; this does not establish public deployment readiness.

## Flexible weekly planner

Onboarding now includes baseline weekday choices for all four sections. Keep the prescribed baseline frequency (two strength sessions for Protect/Supported, three for Build/Rebuild; two baseline activities per other section). The existing quick Sunday choices remain optional shortcuts.

In Your week, expand **Add an optional activity** to choose an activity type and weekday; the form previews the new weekly commitment. Each unfinished activity has a **Reschedule** control. Unstarted extras can be removed; baseline activities cannot be removed, and finished activities retain their recorded dates. Moving an activity preserves its activity/session IDs, feedback and resume position. Chosen dates and extras recur in the next week; historical weeks are retained. Calendar edits clear pending proposals and synchronize the staged schedule without discarding accepted next-week counts.

Prototype scheduling limits: at most one activity of each type per day; no adjacent strength days (including Sunday/Monday); at most three strength days, with supported mode retaining its prescribed frequency. Previous-week strength dates are also checked before editing a current week. These are conservative product policies, not validated clinical scheduling rules.

Progress computes baseline completion separately from optional extras. The daily activity curve includes all completed activities by scheduled date. Overview offers the next activity, prioritizing unfinished work, today's activities, then upcoming work. This change does not add accounts, durable storage, notifications, shortened prescriptions or exercise videos.

## Professional polish

The interface now has a welcome screen, consistent activity and training panels, friendly dates, evidence/status chips, and a five-tab native keyboard-accessible dock. The header offers **Aa** text size and high contrast preferences; **About ZINC** explains the evidence, adaptation rules and limits. Demo controls are in a header popover (sidebar only with `?demo=1`).

Your week can be downloaded as an all-day RFC 5545 calendar. Optional rest and breathing timers run only in the browser, record nothing, and never mark an activity complete. Breathing minutes remain self-reported. Exercise SVGs are schematic placeholders, not final instructional art.

Coach history stays inert plain text to preserve the Markdown/external-request regression protection. Only the already-filtered response is escaped for the typing effect. Proposal acceptance and all engine/coach guardrails are unchanged.

Task commits and verification notes are in `verification/polish-notes.md`; browser captures cover desktop and narrow phones. Presentation polish does not add accounts, durable storage or clinical validation. Live Gemini availability depends on local credentials and is not established by the offline regression suite.

Final polish verification: 82 local automated tests passed, plus browser checks at 1280×900, 390×844 and 360×800. The gate also exercises optional timer controls, calendar download, large text/high contrast and the About dialog. Decision and security modules remain unchanged.

## Audit fixes

Later strength pain of 4 or higher now cancels a conflicting accepted next-week target. The current prescription, recorded work and unrelated accepted changes stay intact. Starting next week is blocked until an easier replacement is explicitly accepted. Revoked decisions stay in exported history but are excluded from the active adjustments table.

Ended partial activities show **Ended early**; resumable activities show **In progress**. Calendar event IDs include the plan's start date, remain stable when rescheduling within that week, and differ between fresh weeks. The live verification setup now passes the welcome step. The root `.gitignore` protects local secrets, virtual environments and generated Python caches.

Audit-fix verification: 88 local tests passed, including an offline run through the provider gate's actual Accept UI using a fake provider. Browser regressions also passed at 1280×900, 390×844 and 360×800. This does not claim a new live Gemini result. Previously imported calendar files use the old identifiers; remove old imported entries before reimporting the corrected export if your calendar creates duplicates.
