# Live Gemini proposal and UI acceptance — October 23, 2026

Status: PASS. This supersedes the earlier failed live-model reports; full release remains blocked on public deployment and the other external gates.

Adapter changes: sixty-second per-request deadline (no retries, maximum four requests/eight tools); provider function-call IDs preserved in responses; output ceiling 1,600 tokens; sanitized finish categories and fallback error category/status code, never raw provider errors or keys. The earlier twenty-second live attempt returned provider HTTP 504 before tools completed.

Verification:

- `PYTHONPATH=app .venv/bin/python -m unittest discover -s app/tests -q`: 66 tests passed in 14.738 seconds. Includes function-response ID matching and bounded requests, tool restrictions, stale/tampered proposals, stop behavior, filtered replies and provider-error canary exclusion.
- `.venv/bin/python app/verification/verify_live.py`: real Gemini PASS, 15.4-second coach turn. The model executed get_plan, get_last_session and propose_change successfully. The test cloned the real pending state for Decline, then drove the actual Streamlit Accept button with AppTest. Active count stayed 10, next-week count staged at 11, and explicit rollover activated 11 while historical count stayed 10. See live-model.json.
- Availability and latency vary; the sixty-second per-request setting is not an end-to-end guarantee.

Only fictional Maria data was sent. Configuration stayed server-side. This verifies real-provider integration plus the actual UI control using Streamlit AppTest, not an independent physical-device/public deployment walkthrough. No new independent security review was performed for this narrow adapter follow-up. Existing desktop/phone browser captures predate these adapter-only changes.
