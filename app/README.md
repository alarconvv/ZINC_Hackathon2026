# ZINC complete weekly prototype

## Run

From the project folder:

```sh
.venv/bin/python -m pip install -r app/requirements.txt
.venv/bin/python -m streamlit run app/app.py
```

Or create a Python 3.11+ virtual environment first. Configuration and secret templates are in the project-root `.streamlit` folder. Set `GEMINI_API_KEY` and `MODEL` in `.streamlit/secrets.toml` or Streamlit Cloud secrets; never commit the secrets file. The three model tools are `get_plan`, `get_last_session`, and `propose_change`. No model tool can apply a prescription. Missing configuration returns a clearly labelled fallback. Real model interaction and public deployment require separate verification.

## Journey

Load Maria → profile → complete safety screen → focus → dated four-section week → independently start/resume each activity → coach check-in → accept or decline next-week changes → progress and export → Start next week.

All plans include strength/balance, yoga, reasoning games and relaxation. Strength days retain the age-tier schedule. Other sections run Tuesday and Saturday. Extra yoga adds Sunday yoga; Extra brain and relaxation adds Sunday games and breathing. Both focus toggles start off. Restrictions select supported yoga versions. The bank contains 24 reasoning puzzles across four levels, with three consecutive correct answers raising difficulty and two misses lowering it. Each session has five questions. Breathing uses a ten-second cycle, a three- or five-minute selection and reduced-motion instructions. Completed relaxation minutes are self-reported, not measured by a timer. Quick look is explicitly a mockup; home tests remain planned.

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

Presentation helpers live in `progress_board.py`; `aquatic.css` supplies the shared aquatic surfaces and responsive dock. `DESIGN.md` records the visual decisions. The 66-test Python suite passed after these changes. The existing browser regression suite passed at desktop 1280×900 and phone 390×844, including export, historical-week selection, keyboard navigation, reduced motion, no page errors and no horizontal page overflow. Captures are in `verification/browser/`.

## Live Gemini integration follow-up

The adapter now allows sixty seconds per request, still with retries disabled and at most four requests/eight tool calls. This is not a sixty-second end-to-end guarantee. Function responses preserve the provider's function-call IDs, and output is bounded to 1,600 tokens per request. Sanitized model finish categories and fallback status codes help distinguish failures without recording provider error text or credentials.

A real Gemini read/propose/accept test passed on October 23, 2026. The `verification/verify_live.py` additionally checks Decline, clicks the real Streamlit Accept control using AppTest, and verifies next-week activation/history. The enhanced gate passed with a 15.4-second coach turn: active 10, staged next week 11, rollover 11 with prior history retained. See `verification/live-model.json` and `verification/adapter-followup.md`. The local 66-test suite passed after the adapter changes. Provider response time and availability vary; this does not establish public deployment readiness.
