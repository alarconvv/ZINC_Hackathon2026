"""Explicit real-provider gate using fictional Maria data, never prints secrets."""
from datetime import datetime, timezone
from pathlib import Path
import json
import sys
import tomllib
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import coach
import engine
from copy import deepcopy


def main():
    target = Path(__file__).with_name('live-model.json')
    report = {'time': datetime.now(timezone.utc).isoformat(), 'gate': 'live_gemini', 'status': 'BLOCKED'}
    try:
        path = Path(__file__).resolve().parents[2] / '.streamlit/secrets.toml'
        secrets = tomllib.loads(path.read_text()) if path.exists() else {}
        if not all(isinstance(secrets.get(k), str) and secrets[k].strip() for k in ('GEMINI_API_KEY', 'MODEL')):
            report['reason'] = 'Set GEMINI_API_KEY and MODEL in server-side .streamlit/secrets.toml; no provider request made.'
            return report, 2
        state = engine.new_state()
        state['safety_result'] = 'cleared'
        state['plan'] = engine.make_week(state['profile'], 'cleared')
        strength = next(a for a in state['plan']['activities'] if a['section'] == 'strength')
        engine.start_activity(state, strength['id'])
        while not state['session_done']:
            item = state['plan']['exercises'][state['cursor']]
            engine.log_set(state, item['id'], item['reps'], 6, 1)
        original = state['plan']['exercises'][0]['reps']
        reply = coach.coach_turn('This is a fictional prototype test. Read my plan and last-session feedback using both read tools, then propose a harder sit_to_stand goal for next week. Explain concisely without numbers; the app displays the prescription.', state, secrets)
        tools = [e for e in state['events'] if e['event'] == 'tool']
        report['tools'] = tools
        report['diagnostics'] = [e for e in state['events'] if e['event'] in ('model_response', 'reply_filtered', 'fallback', 'coach_success')]
        report['elapsed_s'] = state['events'][-1].get('elapsed_s')
        names = {e['tool'] for e in tools if e.get('valid')}
        if names != {'get_plan', 'get_last_session', 'propose_change'} or state['pending_change'] is None:
            report.update(status='FAIL', reason='Real provider did not complete the validated read/propose loop. Inspect server configuration and model compatibility.')
            return report, 1
        report['stage'] = 'decline'
        declined = deepcopy(state)
        before_decline = deepcopy(declined['plan'])
        engine.decline_pending_change(declined)
        assert declined['pending_change'] is None and declined['plan'] == before_decline and declined['next_plan'] is None
        assert state['plan']['exercises'][0]['reps'] == original
        report['stage'] = 'ui_accept'
        from streamlit.testing.v1 import AppTest
        at = AppTest.from_file(str(Path(__file__).resolve().parents[1] / 'app.py'), default_timeout=30).run()
        state['messages'].append({'role': 'assistant', 'text': reply})
        state['welcomed'] = True
        at.session_state['zinc'] = state
        at.session_state['page'] = 'Coach'
        at.run()
        assert not at.exception
        next(b for b in at.button if b.label == 'Accept for next week').click().run()
        assert not at.exception
        state = at.session_state['zinc']
        assert state['pending_change'] is None
        assert state['plan']['exercises'][0]['reps'] == original
        staged = state['next_plan']['exercises'][0]['reps']
        assert staged > original
        report['stage'] = 'rollover'
        engine.start_next_week(state)
        assert state['plan']['exercises'][0]['reps'] == staged
        assert state['history'][-1]['exercises'][0]['reps'] == original
        report['prescriptions'] = {'active_before': original, 'active_after_accept': original,
                                   'staged_next_week': staged, 'active_after_rollover': staged}
        report.update(status='PASS', stage='complete', reason='Real provider read both contexts and proposed a validated adjustment. Decline preserved plans; the actual Streamlit Accept button staged the adjustment without rewriting the current week. Rollover activated it and retained history.')
        return report, 0
    except Exception:
        # Provider/parsing errors may include credentials. Never serialize their message.
        report.update(status='FAIL', reason='Live gate could not finish; raw errors withheld to protect server configuration.')
        return report, 1
    finally:
        target.write_text(json.dumps(report, indent=2) + '\n')


if __name__ == '__main__':
    result, code = main()
    print(json.dumps(result, indent=2))
    raise SystemExit(code)
