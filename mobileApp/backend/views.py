"""Server presentation data: prescriptions and completion never come from clients."""
from datetime import date, timedelta
import os
from .zinc_core import engine, progress_board

def screen_data(s):
    plan = s['plan']
    if not plan:
        return {}
    sessions = s['activity_sessions']
    rows = [{**a, 'status': sessions.get(a['id'], {}).get('status', 'not started'), 'finished': sessions.get(a['id'], {}).get('finished', False)} for a in plan['activities']]
    today = date.today().isoformat()
    upcoming = [a for a in rows if not a['finished'] and a['date'] >= today] or [a for a in rows if not a['finished']]
    session = sessions.get(s.get('active_activity'))
    next_activity = next((a for a in rows if session and a['id'] == session['id'] and not session['finished']), upcoming[0] if upcoming else None)
    active = None
    if session:
        active = {**session, 'item': None, 'count': 0, 'pain_warning': bool(session.get('pain_limited') or any(f.get('pain', 0) >= 4 for f in session['feedback']))}
        if session['section'] == 'strength':
            active['count'] = sum(r.get('activity_id') == session['id'] for r in s['logs']['sessions'])
            active['pain_warning'] |= any(r.get('activity_id') == session['id'] and r['pain'] >= 4 for r in s['logs']['sessions'])
            if not session['finished']:
                active['item'] = {**engine.prescription(plan, plan['exercises'][s['cursor']]['id']), 'exercise_number': s['cursor'] + 1, 'exercise_total': len(plan['exercises']), 'set_number': s['set_index'] + 1}
        elif session['section'] == 'yoga':
            active['count'] = len(session['feedback'])
            if not session['finished']:
                active['item'] = plan['yoga'][session['pose_index']]
        elif session['section'] == 'brain':
            active['count'] = len(session['answers'])
            if not session['finished'] and not s['stopped']:
                active['item'] = {k: v for k, v in engine.current_puzzle(s).items() if k not in ('answer', 'explanation')}
        else:
            active['count'] = session.get('completed_minutes', 0)
    board = progress_board.summarize(plan, sessions)
    for section, count in zip(engine.SECTIONS, board['sections']):
        count['id'] = section
        count['next_date'] = next((a['date'] for a in rows if a['section'] == section and not a['finished']), None)
    unfinished = (bool(s['logs']['sessions']) and not s['session_done']) or any(not a['finished'] for a in sessions.values() if a['week'] == plan['week'])
    remaining = [a for a in rows if not a['finished']]
    missed = [a for a in remaining if a['date'] < today]
    due = next((a for a in remaining if a['date'] == today), None)
    if session and not session['finished']:
        action = {'kind': 'resume', 'activity': next(a for a in rows if a['id'] == session['id'])}
    elif due:
        action = {'kind': 'start', 'activity': due}
    else:
        action = {'kind': 'recover' if missed else 'rest' if remaining else 'done' if rows else 'empty', 'activity': None}
    strength = 3 if plan['tier'] in ('Build', 'Rebuild') else 2
    recommendations = [{'section': section, 'recommended': strength if section == 'strength' else 2,
        'scheduled': sum(a['section'] == section for a in rows)} for section in engine.SECTIONS]
    last_coach = next((e['event'] for e in reversed(s['events']) if e['event'] in ('coach_success', 'fallback', 'claims_boundary')), None)
    next_start = date.fromisoformat(plan['start_date']) + timedelta(days=7)
    return {'activities': rows, 'next_activity': next_activity, 'active': active, 'sections': board['sections'], 'percent': board['percent'],
        'today': today, 'today_action': action, 'missed_count': len(missed), 'recommendations': recommendations,
        'next_week': {'week': plan['week'] + 1, 'start_date': str(next_start), 'end_date': str(next_start + timedelta(days=6)),
            'unfinished_count': sum(not a['finished'] for a in sessions.values() if a['week'] == plan['week']),
            'unstarted_count': sum(a['status'] == 'not started' for a in rows)},
        'coach_configured': bool(os.getenv('GEMINI_API_KEY') and os.getenv('MODEL')),
        'coach_source': {'coach_success': 'gemini', 'fallback': 'fallback', 'claims_boundary': 'guidance'}.get(last_coach),
        'can_accept': bool(s['pending_change']) and not unfinished and not s['stopped'], 'stop_message': engine.STOP_MESSAGE}
