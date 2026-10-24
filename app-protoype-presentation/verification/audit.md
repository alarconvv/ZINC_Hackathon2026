# Ponytail engineering audit and review — V261023

What this repo does: ZINC creates fictional four-section weekly wellness plans, runs independently resumable activities, records feedback, and stages deterministic exercise adjustments for human approval. The expected load is one fictional user per browser session; accounts, shared databases and durable storage are outside this prototype.

The engineering team reviewed the runtime, all callers, test fixtures, configuration, dependencies and the V261023 specification. Backend implementation, independent QA, security review and browser review ran in parallel. Findings were reproduced, fixed, checked with regressions and reviewed again. The Word specification was not edited during this pass.

## Must-fix findings — resolved

1. **Strength feedback could corrupt a different activity.**
   - What this is: set logging updates both feedback and the active session.
   - Problem: starting yoga and calling the strength logger wrote strength sets under the yoga activity and changed its completion state.
   - Fix: reject wrong-section and finished-session calls before mutation; regression tests compare the complete unchanged state.
   - If skipped: stale callbacks or future callers could falsify completion and progression. Status: resolved.

2. **Model Markdown could cause off-app requests.**
   - What this is: coach and user messages were passed to Markdown-capable `st.write`.
   - Problem: a provider reply containing an image URL could request an external endpoint carrying fictional profile fields in the URL.
   - Fix: render both sides of chat with plain `st.text`; the malicious-Markdown regression proves the payload is inert and absent from Markdown output.
   - If skipped: untrusted prose could trigger browser requests or present misleading links. Status: resolved.

3. **Known dependency advisories prevented a clean security gate.**
   - What this is: Streamlit 1.50.0 and Pillow 11.3.0 were pinned/resolved.
   - Problem: official Streamlit advisories affected the old pin; the full dependency scan also flagged Pillow. Streamlit 1.54 through 1.66.0 capped Pillow below the required patch version.
   - Fix: compatible released pins Streamlit 1.66.1 and Pillow 13.0.0, exact tested runtime lock, package compatibility check and a fresh strict advisory scan. No advisory IDs were suppressed.
   - If skipped: the dependency security gate would remain red, even where current image-upload paths do not expose the vulnerable parsers. Status: resolved; 49 runtime packages, zero known advisory records.

4. **Week dates and input types were not consistently validated.**
   - What this is: the engine accepts profile, scheduling, completion and proposal inputs independently of widgets.
   - Problem: host-local dates could differ from Eastern time; non-Monday starts, truthy non-boolean clearance/focus/skip values and boolean numeric fields could slip through shared boundaries. Direct change application also needed next-week dates to match its week number.
   - Fix: explicit Eastern dates, Monday validation, strict relevant types and aligned next-week dates/schedule. Boundary and multiweek tests cover the cases.
   - If skipped: UI and direct tool callers could disagree about eligibility, dates or prescription validity. Status: resolved.

5. **Session identity and history could be misleading.**
   - What this is: activity IDs identify scheduled slots; session IDs identify a user's activity execution.
   - Problem: the scheduled activity record overwrote the generated session ID. Historical Progress also displayed the current global reasoning level instead of the selected week's final level.
   - Fix: distinct `session_id` and `activity_id`, strength log linkage, saved `level_after` results and selected-week rendering. Old session records fall back to their recorded puzzle level.
   - If skipped: exports and historical progress could attribute work or difficulty to the wrong session/week. Status: resolved.

6. **Brain activity feedback leaked between sessions.**
   - What this is: the displayed correct/incorrect explanation was stored globally.
   - Problem: an untouched second brain activity could show the first activity's feedback.
   - Fix: store feedback on its activity session; the real Streamlit A→B→A test verifies isolation and restoration.
   - If skipped: independent sessions would show misleading feedback. Status: resolved.

7. **Labels and feedback had insufficient contrast.**
   - What this is: some themed widgets and alerts retained dark text directly over the blue app surface.
   - Problem: Week, relaxation choices and brain feedback were difficult to read in desktop and phone captures.
   - Fix: surface-aware label colors, opaque light alerts and preserved dark text inside light forms/navigation. Browser assertions verify computed colors and reviewers checked refreshed captures.
   - If skipped: users could miss controls or activity feedback. Status: resolved.

## Should-fix findings — resolved

8. **Rejected tool calls were missing from the audit trail.**
   - What this is: the activity export records model actions and validation decisions.
   - Problem: unknown tools and malformed arguments raised before an event was recorded.
   - Fix: log rejected calls using an allowlisted tool name or `unknown`, never raw arguments or provider errors. Canary tests prove secrets/untrusted names do not enter events.
   - If skipped: failed model turns could not be explained by their exported tool events. Status: resolved.

## Verification and review verdict

- Unit, Streamlit functional/acceptance, SDK integration and security suite: **63 tests passed**, no failures or skips. See `test-results.txt`.
- Browser: Chromium at 1280×900 and 390×844; onboarding, all sections/players, keyboard activation, normal/reduced-motion breathing, contrast, real JSON download, week rollover and historical Progress pass. No page errors or horizontal page overflow. See `browser/results.json` and captures.
- Security regressions: allowlist/read-before-proposal, eight-tool/four-request budgets, immutable tool context, stop denial, staged approval, provider canary exclusion and inert Markdown pass.
- Package compatibility: `pip check` passes.
- Dependency scan: `dependency-audit.json` contains zero known vulnerabilities for all 49 exact runtime dependencies in `requirements.lock.txt`. The strict scan used PyPI advisories; it is a point-in-time known-advisory check, not proof that no unknown vulnerabilities exist.
- Independent security verdict: ship the reviewed local prototype; no unresolved actionable local code findings.
- Independent browser verdict: all three listed feedback/contrast/session-isolation findings resolved at the tested simulated viewports.

Official advisory sources: [Streamlit Windows SSRF](https://github.com/streamlit/streamlit/security/advisories/GHSA-7p48-42j8-8846), [Streamlit cache hashing](https://github.com/advisories/GHSA-vqwp-45wm-r9r5), [Streamlit 1.66.1 dependency metadata](https://raw.githubusercontent.com/streamlit/streamlit/1.66.1/lib/pyproject.toml), [Pillow 13.0.0](https://pypi.org/project/pillow/13.0.0/).

**Verdict: ship locally. Full release is blocked, not all green.** See `gates.md` and `checks.json` for the complete specification mapping and outstanding gates.

**Not checked:** complete live Gemini proposal/acceptance (read tools reached the provider successfully; see follow-up), provider spending controls, public hosting/TLS/reviewer access, physical devices, assistive-technology sessions, clinical content validation, or human-authored submission artifacts/rehearsal. Keyword claim filtering remains supplementary and cannot guarantee arbitrary provider prose is semantically safe. No accounts/persistence, wearables or other roadmap features were added.

## Live configuration follow-up

Saved credentials were used only from server-side secrets. The initial model returned 404; the provider model listing was queried without exposing the key. Live testing also exposed two adapter defects missed by the fake network: an eight-second request deadline below the provider minimum, and the unsupported `tool` role for function responses. The adapter now uses a bounded twenty-second deadline with retries disabled and the Gemini `user` response role. The adapter regression asserts permitted roles and function-response roles; the security regression checks the bounded deadline. The complete 63-test suite passes again (14.055 seconds). Prior independent reviews cover the earlier local build; this narrow follow-up is verified by regressions and the live gate record.

Final live outcome: FAIL with valid `get_plan` and `get_last_session` events; no completed validated proposal/acceptance loop. See `live-model.json`. Active model: Gemini 3.1 Flash Lite. External deployment and human gates remain open.

## Latest adapter follow-up

The earlier live FAIL is superseded by a real provider + Streamlit Accept PASS. See `adapter-followup.md` and `live-model.json`. All 66 local tests passed. The existing independent security review predates this narrow adapter change; no renewed independent review is claimed. Public deployment and human release gates remain open.
