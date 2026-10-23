# V261023 build verification — October 23, 2026

The source is `ZINC_App_3-Day_Build_Plan_V261023.docx`. This record concerns a fictional, session-only prototype; passing software tests is not clinical validation. **The full release is not all green:** live Gemini, public deployment, physical-device checks and submission artifacts require separate evidence.

## Reproducible automated gate

From `app/` run `../.venv/bin/python -m unittest discover -s tests -v`.
The final QA run passed **63 tests in 14.055 seconds**, with no failures or skips (includes acceptance, engine, SDK and adversarial security regressions). Streamlit bare-runtime warnings and an SDK Pydantic deprecation warning did not fail tests. Dependencies are installed in the project `.venv`.

`test_engine.py` and `test_weekly.py` cover unit rules; `test_app.py` and `test_acceptance.py` drive actual Streamlit forms with AppTest; `test_model_adapter.py` exercises SDK response/tool shapes with a fake network. These tests do not contact Gemini or demonstrate a public deployment.

## Twenty specification scenarios

| # | Expected | Actual evidence / remaining work |
|---|---|---|
| 1 | Maria's four-section Protect plan and supported content | PASS local: `EngineTests.test_maria_plan`, `AppTests.test_complete_journey_and_history`; all four players run. |
| 2 | Chest screening blocks plan and AI | PASS local: `EngineTests.test_chest_screen_blocks_generation_and_model`, `AppTests.test_screen_blocks`. |
| 3 | Fall screening selects supported versions | PASS local: `EngineTests.test_falls_supported`. |
| 4 | Dizziness immediately stops, no AI | PASS local: `EngineTests.test_dizzy_stops_without_model`; `AcceptanceTests.test_symptom_form_locks_every_activity_and_coach_without_network` drives symptoms in every player. |
| 5 | Pain 5 blocks harder; easier stages next week | PASS local rules: `test_step_up_pain_five_blocks_harder`, `test_high_pain_rejects_harder_and_ends_exercise`; independent staging covered by `WeeklyTests.test_staging_and_rollover`. No live model claim. |
| 6 | Decline preserves prescriptions | PASS local: `EngineTests.test_decline_leaves_plan`. |
| 7 | Disease question has no disease promise | PASS local: `EngineTests.test_disease_question_no_model`, `test_response_filter`, `test_filtered_reply_discards_proposal`. Keyword rules are not a semantic guarantee. |
| 8 | Missing key / failure labelled fallback; elapsed recorded | PASS local: `test_missing_key_fallback`, `test_failed_turn_discards_staged_proposal`, `AcceptanceTests.test_missing_configuration_is_local_labelled_fallback`; event records elapsed seconds. Real network outage latency remains unmeasured. |
| 9 | Back preserves answers; default four-section plan | PASS AppTest: `AppTests.test_back_preserves_answers`, `AcceptanceTests.test_focus_back_navigation_preserves_all_answers_and_date`. |
| 10 | Independent/both toggles add only intended Sundays | PASS local: `AcceptanceTests.test_focus_combinations_add_only_documented_sunday_sections`. |
| 11 | Supported yoga; feedback; pain ends partial | PASS local: `WeeklyTests.test_yoga_pain_partial`; player exercised by `AppTests.test_complete_journey_and_history`. |
| 12 | Three correct up; two misses down; bounded levels | PASS local: `WeeklyTests.test_reasoning_bank_rules`; no strength-plan mutation from mixed coach context (`AcceptanceTests.test_coach_reads_mixed_activity_history_without_mutating_plan`). |
| 13 | 3/5-minute breathing, accessible/reduced motion, skip=0 | PASS local AppTest: `AcceptanceTests.test_relaxation_lengths_skip_and_accessible_instructions` checks both values, self-report completion and skip; reduced-motion rule, accessible text and 10-second cycle exist. PASS browser: normal-motion keyframe phases, 10-second cycle, reduced-motion alternative and control/alert contrast verified in Chromium at both tested viewport sizes. |
| 14 | Independent resume and rerun duplicate protection | PASS local: `WeeklyTests.test_resume_and_duplicate_completion`, `AcceptanceTests.test_reruns_do_not_repeat_submitted_work`. |
| 15 | Completed/partial/skipped/unstarted board accurate | PASS AppTest: `AcceptanceTests.test_mixed_status_board_across_two_weeks` asserts displayed status counts and completed reasoning/relaxation summaries. |
| 16 | Stage once; reject stale/tampered/duplicate | PASS local: `test_stale_and_tampered_proposals`, `test_accept_once_and_input_immutability`, `test_full_session_acceptance`, `WeeklyTests.test_staging_and_rollover`. |
| 17 | Next week retains history; old feedback cannot progress | PASS local: `WeeklyTests.test_staging_and_rollover`, `AcceptanceTests.test_mixed_status_board_across_two_weeks`. |
| 18 | Coach reads complete history; bounded guidance | PASS injected model: `AcceptanceTests.test_coach_reads_mixed_activity_history_without_mutating_plan`, `EngineTests.test_successful_tool_turn_stages_without_mutation`; SDK fake network in `AdapterTests.test_real_adapter_tool_loop`. Live Gemini read both contexts and created a validated proposal; the actual Streamlit Accept control and week rollover PASS (`live-model.json`, `adapter-followup.md`). |
| 19 | Week-specific metrics/export/reset; refresh limits stated | PASS local for board/reset: `AcceptanceTests.test_mixed_status_board_across_two_weeks`, `test_ui_reset_clears_history_and_requires_new_screen`. Export payload inspected in source: profile, current/staged/history plans, activity sessions, logs, events; PASS real browser download: parsed JSON matches set/activity counts and completed relaxation minutes at both viewport sizes. Refresh-loss warning appears in UI/README. |
| 20 | Phone and second-device complete journey | PASS simulated browser viewports: desktop 1280×900 and phone 390×844, keyboard activation, all players, export/history and no overflow. Physical-device, public link and live-model checks remain OPEN. |

## Milestones and release gates

| Gate | Actual status |
|---|---|
| Local unit / functional / integration | Automated results below; passing tests cover deterministic and injected-model behavior only. |
| Security pass | PASS local reviewed scope: all concrete findings resolved; 7 adversarial tests, `pip check`, and strict dependency scan (49 packages, zero advisory records) pass. See `audit.md`. Local tests enforce model tool allowlist, read-before-propose, proposal validation, stopped-state denial, deep-copy read isolation and failure-detail exclusion. This is not a penetration test or provider-account audit. |
| M0 setup | Local requirements/secrets template and fixtures exist. Public phone link is OPEN; complete live acceptance now PASS; team access/roster/work blocks not verified. |
| M1 deterministic journey | Local automated coverage PASS. |
| M2 agent loop | Injected-model/SDK adapter coverage PASS. Live Gemini reads PASS with saved secrets and Gemini 3.1 Flash Lite. Complete validated pending-change/UI acceptance/rollover loop now PASS; see `live-model.json` and `adapter-followup.md`. |
| M3 deployed core | Local four-player journey/history PASS. Public deployment and independent two-device checks OPEN. Report/deck/poster drafts not verified. |
| M4 evidence/content | This mapping covers 20 scenarios with explicit limitations; final six-section report, screenshots and links OPEN. |
| M5 release candidate | Dependency pins exist. Local fresh-session AppTest PASS; final artifact package, dependency audit PASS; final artifacts and backup recording remain OPEN. |
| M6 rehearsal | OPEN: timed 7-minute talk, 2-minute poster pitch, real team review and backup recording need human evidence. |
| M7 submission package | OPEN: six-section report, manually authored deck, one horizontal poster, identities/photo, reviewer access and public app links not delivered/verified by these tests. |
| M8 submit/verify | OPEN: submission and confirmation require external action/evidence. |

Do not convert OPEN gates to PASS on the strength of mocks or localhost tests. The plan requires slides/poster to be designed by hand with AI mode off; those assets and real team identity/rehearsal evidence cannot be invented by the software team.

## Final local engineering gate record

All local gates PASS after fixes and re-review. `checks.json` records exact source hashes, runtime versions and evidence. `audit.md` lists every material finding and resolution. The prior missing browser/export evidence is now supplied by `browser/results.json` and captures. Re-run after any implementation or dependency change.

Live gate command: `../.venv/bin/python verification/verify_live.py` from `app/`. It deliberately returns exit 2 and writes BLOCKED when server configuration is missing; it never turns a mock into a live pass. Once configured it sends only the fictional fixture and records actual tool events.

## Live gate follow-up

Server-side secrets are now configured. The originally configured model returned 404. Gemini 2.5 Flash was unavailable to new users; 3.5 Flash returned temporary high-demand errors; 3.8 Flash did not complete the bounded gate. Configuration now selects the listed Gemini 3.1 Flash Lite model. Its real calls successfully executed `get_plan` and `get_last_session`, but the full proposal/acceptance gate failed after 34.186 seconds. No adjustment was accepted. The live gate is FAIL, not missing-configuration BLOCKED and not PASS. No credentials or raw provider messages appear in these reports.

Two live adapter defects were fixed: the request deadline is now twenty seconds, and function responses use Gemini's `user` role. All 63 local tests pass again. Browser evidence remains from the prior run; UI code did not change. The narrow adapter fix has regression coverage but has not received another independent review.

## Latest live gate — supersedes earlier follow-up failures

Status: PASS. This supersedes the earlier failed live-model reports; full release remains blocked on public deployment and the other external gates.

Adapter changes: sixty-second per-request deadline (no retries, maximum four requests/eight tools); provider function-call IDs preserved in responses; output ceiling 1,600 tokens; sanitized finish categories and fallback error category/status code, never raw provider errors or keys. The earlier twenty-second live attempt returned provider HTTP 504 before tools completed.

Verification:

- `PYTHONPATH=app .venv/bin/python -m unittest discover -s app/tests -q`: 66 tests passed in 14.738 seconds. Includes function-response ID matching and bounded requests, tool restrictions, stale/tampered proposals, stop behavior, filtered replies and provider-error canary exclusion.
- `.venv/bin/python app/verification/verify_live.py`: real Gemini PASS, 15.4-second coach turn. The model executed get_plan, get_last_session and propose_change successfully. The test cloned the real pending state for Decline, then drove the actual Streamlit Accept button with AppTest. Active count stayed 10, next-week count staged at 11, and explicit rollover activated 11 while historical count stayed 10. See live-model.json.
- Availability and latency vary; the sixty-second per-request setting is not an end-to-end guarantee.

Only fictional Maria data was sent. Configuration stayed server-side. This verifies real-provider integration plus the actual UI control using Streamlit AppTest, not an independent physical-device/public deployment walkthrough. No new independent security review was performed for this narrow adapter follow-up. Existing desktop/phone browser captures predate these adapter-only changes.
