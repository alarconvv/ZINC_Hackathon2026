"""Deterministic prototype policies; no model or UI dependencies."""
from copy import deepcopy
import csv
from datetime import datetime, timezone, date, timedelta
import activities
from pathlib import Path
import re
from uuid import uuid4
from zoneinfo import ZoneInfo

QUESTIONS = {
    'chest': 'Chest pain at rest or during activity?',
    'faint': 'Dizziness, fainting, or unexplained loss of consciousness?',
    'heart': 'A heart condition or instruction to exercise only under supervision?',
    'pressure': 'Uncontrolled blood pressure or a concern about blood pressure?',
    'medication': 'Diabetes medication that needs exercise guidance?',
    'joint': 'A joint or bone condition that could be made worse by exercise?',
    'falls': 'A fall in the past year?',
}
STOP_MESSAGE = ('Stop exercising and sit or lie somewhere safe. Seek urgent medical help for chest pain, '
                'fainting, or severe or persistent symptoms. Do not resume this session. Contact local emergency services if needed.')
AVAILABLE = {'yoga': True, 'brain': True}
MARIA = {'name': 'Maria', 'age': 52, 'level': 'beginner', 'limits': ['knees'],
         'mci': False, 'clinician_clearance': False, 'toggles': {'yoga': False, 'brain': False}}


def new_state(profile=None):
    return {'profile': deepcopy(profile or MARIA), 'safety_result': None, 'stopped': False,
            'plan': None, 'logs': {'version': 0, 'sessions': []}, 'pending_change': None,
            'onboarding_step': 0, 'screening_answers': {}, 'next_plan': None, 'history': [],
            'activity_sessions': {}, 'active_activity': None, 'brain_level': 1, 'brain_streak': [],
            'events': [], 'messages': [], 'cursor': 0, 'set_index': 0, 'session_done': False}


def event(state, kind, **details):
    state['events'].append({'time': datetime.now(timezone.utc).isoformat(), 'event': kind, **details})


def assign_tier(age):
    if type(age) is not int or not 20 <= age <= 110:
        raise ValueError('This prototype supports ages 20–110.')
    return 'Build' if age < 40 else 'Protect' if age < 60 else 'Rebuild' if age < 80 else 'Supported'


def safety_check(answers):
    if set(answers) != set(QUESTIONS) or any(type(v) is not bool for v in answers.values()):
        raise ValueError('Answer every screening question.')
    if any(answers[k] for k in QUESTIONS if k != 'falls'):
        return 'clinician'
    return 'limits' if answers['falls'] else 'cleared'


def red_flag(text):
    return bool(re.search(r'\b(chest\s+(pain|pressure|tightness)|dizz\w*|faint\w*|passed out|shortness of breath|cannot breathe|can.t breathe)\b', str(text), re.I))


def stop(state):
    state['stopped'] = True
    state['pending_change'] = None
    event(state, 'safety_stop')
    return STOP_MESSAGE


def eligible(state):
    return not state['stopped'] and state['safety_result'] in ('cleared', 'limits') and state['plan'] is not None


def catalog():
    with (Path(__file__).parent / 'content/exercises.csv').open(newline='') as f:
        return list(csv.DictReader(f))


def make_week(profile, safety_result, available_features=None, start_date=None):
    today = datetime.now(ZoneInfo('America/New_York')).date()
    start = date.fromisoformat(str(start_date)) if start_date is not None else today - timedelta(days=today.weekday())
    if start.weekday() != 0:
        raise ValueError('Choose a Monday for the weekly schedule.')
    tier = assign_tier(profile['age'])
    if safety_result not in ('cleared', 'limits'):
        raise ValueError('Complete screening and obtain clinician review if required before making a plan.')
    if profile['level'] not in ('beginner', 'active', 'trained') or not set(profile['limits']) <= {'knees', 'back', 'balance'}:
        raise ValueError('Invalid fitness level or limitations.')
    if any(type(profile.get(k, False)) is not bool for k in ('mci', 'clinician_clearance')) or any(type(v) is not bool for v in profile.get('toggles', {}).values()):
        raise ValueError('Screening clearance and focus choices must be boolean values.')
    if (tier == 'Supported' or profile.get('mci')) and not profile.get('clinician_clearance'):
        raise ValueError('The Supported tier requires clinician sign-off before this demo can generate a plan.')
    if profile.get('mci'):
        tier = 'Supported'
    supported = tier == 'Supported' or safety_result == 'limits' or 'balance' in profile['limits']
    exercises = []
    for item in catalog():
        limited = supported or (item['id'] in ('sit_to_stand', 'step_up') and 'knees' in profile['limits']) or (item['id'] in ('hip_hinge', 'core', 'carry') and 'back' in profile['limits'])
        reps = 10 if profile['level'] == 'beginner' or limited else 12
        item.update(version=item['easier'] if limited else item['standard'], reps=reps,
                    base_reps=reps, sets=1 if item['id'] in ('core', 'supported_balance') else 2,
                    unit='seconds' if item['id'] == 'core' else 'reps',
                    power=profile['age'] >= 40 and not supported and item['id'] in ('sit_to_stand', 'step_up', 'row'))
        exercises.append(item)
    plan = {'version': 1, 'week': 1, 'tier': tier, 'fall_risk': supported, 'exercises': exercises,
            'days': ['Mon', 'Wed', 'Fri'] if tier in ('Build', 'Rebuild') else ['Mon', 'Thu'],
            'applied_ids': [], 'adjusted_exercises': [], 'start_date': str(start),
            'yoga': activities.yoga_content(profile, supported), 'toggles': deepcopy(profile.get('toggles', {}))}
    schedule(plan)
    return plan


def summary(plan):
    return f"{plan['tier']} · {len(plan['days'])} strength sessions · balance on {len(plan['days'])} days · plan v{plan['version']}"


def prescription(plan, exercise_id):
    for item in plan['exercises']:
        if item['id'] == exercise_id:
            return item
    raise ValueError('Unknown exercise.')


def feedback(logs, exercise_id):
    return [s for s in logs['sessions'] if s['exercise_id'] == exercise_id]


def log_set(state, exercise_id, reps, effort, pain):
    if not eligible(state) or state['session_done']:
        raise ValueError('The session is not available.')
    if state.get('active_activity'):
        session = active_session(state)
        if session['section'] != 'strength' or session['finished']:
            raise ValueError('Choose an unfinished strength activity before logging a set.')
    item = prescription(state['plan'], exercise_id)
    current = state['plan']['exercises'][state['cursor']]
    if item['id'] != current['id']:
        raise ValueError('Log the current exercise first.')
    if any(type(v) is not int for v in (reps, effort, pain)) or not (0 <= reps <= 100 and 1 <= effort <= 10 and 0 <= pain <= 10):
        raise ValueError('Enter valid repetitions, effort (1–10) and pain (0–10).')
    state['logs']['sessions'].append({'id': str(uuid4()), 'exercise_id': exercise_id,
                                    'week': state['plan']['week'], 'activity_id': state.get('active_activity'),
                                    'session_id': state['activity_sessions'][state['active_activity']]['session_id'] if state.get('active_activity') else None,
                                    'reps': reps, 'effort': effort, 'pain': pain,
                                    'plan_version': state['plan']['version'], 'set': state['set_index'] + 1})
    state['logs']['version'] += 1
    state['pending_change'] = None
    event(state, 'set_logged', exercise_id=exercise_id, pain=pain, effort=effort)
    staged = state.get('next_plan')
    if (pain >= 4 and staged and exercise_id in staged['adjusted_exercises']
            and prescription(staged, exercise_id)['reps'] >= item['reps']):
        # Cancel the unsafe decision; a replacement still needs explicit approval.
        prescription(staged, exercise_id)['reps'] = item['reps']
        staged['adjusted_exercises'].remove(exercise_id)
        state['plan']['adjusted_exercises'].remove(exercise_id)
        state.setdefault('pain_reviews', []).append(exercise_id)
        for accepted in state['events']:
            if (accepted['event'] == 'accepted' and accepted.get('week') == state['plan']['week']
                    and accepted.get('exercise_id') == exercise_id):
                accepted['revoked'] = True
        event(state, 'change_revoked', week=state['plan']['week'], exercise_id=exercise_id)
    state['set_index'] += 1
    # Pain steps back immediately by ending this exercise; the next-week plan still needs approval.
    if state['set_index'] >= item['sets'] or pain >= 4:
        state['cursor'] += 1
        state['set_index'] = 0
    state['session_done'] = state['cursor'] >= len(state['plan']['exercises'])
    if state.get('active_activity'):
        session = state['activity_sessions'][state['active_activity']]
        session.update(cursor=state['cursor'], set_index=state['set_index'])
        session['status'] = 'completed' if state['session_done'] and not session.get('pain_limited') and pain < 4 else 'partial'
        session['pain_limited'] = session.get('pain_limited', False) or pain >= 4
        session['finished'] = state['session_done']


def progress(plan, logs, exercise_id, direction):
    if direction not in ('harder', 'same', 'easier'):
        raise ValueError('Direction must be harder, same, or easier.')
    item = prescription(plan, exercise_id)
    records = [r for r in feedback(logs, exercise_id) if r.get('week', plan['week']) == plan['week']]
    if not records:
        raise ValueError('Log a set for this exercise before requesting an adjustment.')
    if exercise_id in plan['adjusted_exercises']:
        raise ValueError('A next-week decision for this exercise has already been accepted.')
    painful = any(s['pain'] >= 4 for s in records)
    if painful and direction != 'easier':
        raise ValueError('Pain of 4 or more requires an easier proposal.')
    if direction == 'harder' and (records[-1]['effort'] > 7 or records[-1]['reps'] < item['reps']):
        raise ValueError('Keep or ease the prescription until the current repetitions feel manageable.')
    # shortcut: progression uses repetitions only; add loads only with explicit units and validation.
    new_reps = item['reps'] + (item['base_reps'] // 10) if direction == 'harder' else max(1, item['reps'] - max(1, (item['reps'] + 9) // 10)) if direction == 'easier' else item['reps']
    proposal = {'id': str(uuid4()), 'plan_version': plan['version'], 'log_version': logs['version'],
                'exercise_id': exercise_id, 'direction': direction, 'current': item['reps'], 'proposed': new_reps,
                'reason': 'Pain reached 4 or more; reduce repetitions for next week.' if painful else
                {'harder': 'Completed repetitions with manageable effort and low pain; add at most 10% next week.',
                 'same': 'Keep repetitions steady for next week.', 'easier': 'Reduce repetitions for a more manageable next week.'}[direction]}
    return proposal


def check_change(plan, logs, proposal):
    try:
        if not isinstance(proposal, dict) or not isinstance(proposal.get('id'), str) or not proposal['id']:
            raise ValueError('Invalid proposal ID.')
        if any(type(proposal.get(k)) is not int for k in ('plan_version', 'log_version')):
            raise ValueError('Invalid proposal versions.')
        if proposal['id'] in plan['applied_ids']:
            raise ValueError('This proposal was already applied.')
        if proposal['plan_version'] != plan['version'] or proposal['log_version'] != logs['version']:
            raise ValueError('Feedback or plan changed; request a fresh proposal.')
        expected = progress(plan, logs, proposal['exercise_id'], proposal['direction'])
        for k in ('current', 'proposed', 'reason'):
            if proposal[k] != expected[k] or (k != 'reason' and type(proposal[k]) is not int):
                raise ValueError('The proposal does not match the rules engine.')
        item = prescription(plan, proposal['exercise_id'])
        if proposal['proposed'] * 10 > item['base_reps'] * 11:
            raise ValueError('The weekly repetition increase exceeds 10%.')
        return True, 'Validated by the rules engine.'
    except (KeyError, TypeError, ValueError) as exc:
        return False, str(exc)


def apply_change(plan, logs, proposal):
    ok, reason = check_change(plan, logs, proposal)
    if not ok:
        raise ValueError(reason)
    updated = deepcopy(plan)
    prescription(updated, proposal['exercise_id'])['reps'] = proposal['proposed']
    updated['version'] += 1
    updated['week'] = plan['week'] + 1
    updated['start_date'] = str(date.fromisoformat(plan['start_date']) + timedelta(days=7))
    schedule(updated)
    updated['applied_ids'].append(proposal['id'])
    updated['adjusted_exercises'].append(proposal['exercise_id'])
    return updated


def accept_pending_change(state):
    proposal = state['pending_change']
    state['pending_change'] = None
    if not eligible(state):
        raise ValueError('Training is blocked or stopped.')
    if proposal is None:
        raise ValueError('No pending change.')
    # Do not rewrite a prescription while its training session is in progress.
    if (state['logs']['sessions'] and not state['session_done']) or any(not a['finished'] for a in state['activity_sessions'].values() if a['week'] == state['plan']['week']):
        raise ValueError('Finish the current session before accepting next-week changes.')
    ok, reason = check_change(state['plan'], state['logs'], proposal)
    if not ok:
        event(state, 'accept_rejected')
        raise ValueError(reason)
    if state['next_plan'] is None:
        state['next_plan'] = deepcopy(state['plan'])
        state['next_plan']['week'] += 1
        state['next_plan']['start_date'] = str(date.fromisoformat(state['plan']['start_date']) + timedelta(days=7))
        state['next_plan']['applied_ids'] = []
        state['next_plan']['adjusted_exercises'] = []
        schedule(state['next_plan'])
    if proposal['exercise_id'] in state['next_plan']['adjusted_exercises']:
        raise ValueError('A next-week decision for this exercise was already accepted.')
    prescription(state['next_plan'], proposal['exercise_id'])['reps'] = proposal['proposed']
    state['next_plan']['adjusted_exercises'].append(proposal['exercise_id'])
    state['plan']['version'] += 1
    state['plan']['applied_ids'].append(proposal['id'])
    state['plan']['adjusted_exercises'].append(proposal['exercise_id'])
    if proposal['exercise_id'] in state.get('pain_reviews', []):
        state['pain_reviews'].remove(proposal['exercise_id'])
    event(state, 'accepted', proposal_id=proposal['id'], week=state['plan']['week'], exercise_id=proposal['exercise_id'], proposed=proposal['proposed'])


def decline_pending_change(state):
    state['pending_change'] = None
    event(state, 'declined')


WEEKDAYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
SECTIONS = ('strength', 'yoga', 'brain', 'relaxation')


def schedule(plan):
    start = date.fromisoformat(plan['start_date'])
    template = plan.get('schedule_template')
    if template is None:
        sections = {'strength': [WEEKDAYS.index(d) for d in plan['days']], 'yoga': [1, 5], 'brain': [1, 5], 'relaxation': [1, 5]}
        if plan['toggles'].get('yoga'):
            sections['yoga'].append(6)
        if plan['toggles'].get('brain'):
            sections['brain'].append(6)
            sections['relaxation'].append(6)
        template = [{'slot': f'{section}-{day}', 'section': section, 'day': day,
                     'optional': day == 6 and section != 'strength'} for section, days in sections.items() for day in days]
    plan['activities'] = sorted([{'id': f"w{plan['week']}-{r['slot']}", 'section': r['section'],
        'date': str(start + timedelta(days=r['day'])), 'week': plan['week'], 'optional': r['optional'],
        'minutes': {'strength': 25, 'yoga': 5, 'brain': 5, 'relaxation': 3}[r['section']]} for r in template],
        key=lambda a: (a['date'], a['section']))


def schedule_template(plan):
    start = date.fromisoformat(plan['start_date'])
    return [{'slot': a['id'].split('-', 1)[1], 'section': a['section'],
             'day': (date.fromisoformat(a['date']) - start).days, 'optional': a.get('optional', False)}
            for a in plan['activities']]


def validate_schedule(plan, template, *, allow_reduced=False):
    if not isinstance(template, list) or any(not isinstance(r, dict) for r in template):
        raise ValueError('Choose a valid weekly schedule.')
    for r in template:
        if (r.get('section') not in SECTIONS or type(r.get('day')) is not int or not 0 <= r['day'] <= 6
                or type(r.get('optional')) is not bool or not isinstance(r.get('slot'), str) or not r['slot']):
            raise ValueError('Choose an activity and a day within this week.')
    if len({r['slot'] for r in template}) != len(template) or len({(r['section'], r['day']) for r in template}) != len(template):
        raise ValueError('Each activity type can appear only once per day.')
    required_strength = 3 if plan['tier'] in ('Build', 'Rebuild') else 2
    for section in SECTIONS:
        baseline = [r for r in template if r['section'] == section and not r['optional']]
        required = required_strength if section == 'strength' else 2
        if len(baseline) > required or (not allow_reduced and len(baseline) != required):
            raise ValueError('Keep all prescribed baseline activities in your week.')
    strength = sorted(r['day'] for r in template if r['section'] == 'strength')
    if len(strength) > (required_strength if plan['fall_risk'] else 3):
        raise ValueError('Keep your prescribed strength frequency in supported mode; otherwise at most three strength days are available.')
    if any((day + 1) % 7 in strength for day in strength):
        raise ValueError('Leave at least one rest day between strength sessions, including Sunday and Monday.')


def choose_days(plan, choices):
    """Select baseline weekdays before any activity is started."""
    if not isinstance(choices, dict) or set(choices) != set(SECTIONS):
        raise ValueError('Choose days for all four activity types.')
    template = schedule_template(plan)
    for section in SECTIONS:
        rows = [r for r in template if r['section'] == section and not r['optional']]
        days = choices[section]
        if not isinstance(days, list) or len(days) != len(rows):
            raise ValueError(f'Choose {len(rows)} baseline days for {section}. Add optional activities after creating your week.')
        for row, day in zip(rows, sorted(days) if all(type(d) is int for d in days) else days):
            row['day'] = day
    validate_schedule(plan, template)
    updated = deepcopy(plan)
    updated['schedule_template'] = template
    updated['days'] = [WEEKDAYS[r['day']] for r in template if r['section'] == 'strength']
    schedule(updated)
    return updated


def change_schedule(state, *, activity_id=None, day=None, section=None, remove=False):
    """Transactional calendar edit; prescriptions and recorded work remain intact."""
    if not eligible(state):
        raise ValueError('Complete screening first; stopped sessions cannot change the schedule.')
    if type(remove) is not bool or (not remove and (type(day) is not int or not 0 <= day <= 6)):
        raise ValueError('Choose a day within the selected week.')
    template = schedule_template(state['plan'])
    if activity_id is None:
        if section not in SECTIONS or remove:
            raise ValueError('Choose a valid activity type.')
        template.append({'slot': f'{section}-extra-{uuid4().hex[:8]}', 'section': section, 'day': day, 'optional': True})
    else:
        activity = next((a for a in state['plan']['activities'] if a['id'] == activity_id), None)
        if activity is None:
            raise ValueError('Choose an activity from the current week.')
        session = state['activity_sessions'].get(activity_id)
        if session and session['finished']:
            raise ValueError('Finished activities stay on their recorded day.')
        row = next(r for r in template if r['slot'] == activity_id.split('-', 1)[1])
        if remove:
            if session is not None:
                raise ValueError('Started activities keep their records. Skip the activity instead.')
            template.remove(row)
        else:
            row['day'] = day
    validate_schedule(state['plan'], template, allow_reduced=True)
    start = date.fromisoformat(state['plan']['start_date'])
    earlier_strength = [date.fromisoformat(a['date']) for past in state['history'] for a in past['activities'] if a['section'] == 'strength']
    if any(0 <= (start + timedelta(days=r['day']) - prior).days <= 1 for r in template if r['section'] == 'strength' for prior in earlier_strength):
        raise ValueError('Leave a rest day after the previous week’s strength session.')
    updated = deepcopy(state['plan'])
    updated.update(schedule_template=template, version=updated['version'] + 1,
                   days=[WEEKDAYS[r['day']] for r in template if r['section'] == 'strength'])
    schedule(updated)
    staged = deepcopy(state['next_plan'])
    if staged is not None:
        staged.update(schedule_template=deepcopy(template), days=updated['days'][:])
        schedule(staged)
    state['plan'], state['next_plan'] = updated, staged
    for activity in updated['activities']:
        if activity['id'] in state['activity_sessions']:
            state['activity_sessions'][activity['id']]['date'] = activity['date']
    feedback_changed(state)
    event(state, 'schedule_changed', week=updated['week'])
    if remove:
        event(state, 'activity_removed', activity_id=activity_id, section=activity['section'], recommended=not activity['optional'])


def start_activity(state, activity_id):
    if not eligible(state):
        raise ValueError('Training is blocked or stopped.')
    activity = next((a for a in state['plan']['activities'] if a['id'] == activity_id), None)
    if activity is None:
        raise ValueError('Unknown scheduled activity.')
    session = state['activity_sessions'].setdefault(activity_id, {
        **deepcopy(activity), 'session_id': str(uuid4()), 'activity_id': activity_id, 'status': 'partial', 'finished': False,
        'cursor': 0, 'set_index': 0, 'feedback': [], 'answers': [], 'pose_index': 0})
    state['active_activity'] = activity_id
    state['cursor'], state['set_index'], state['session_done'] = session['cursor'], session['set_index'], session['finished']
    return session


def active_session(state):
    if not eligible(state) or not state.get('active_activity'):
        raise ValueError('Choose an activity first.')
    return state['activity_sessions'][state['active_activity']]


def finish_activity(state, skipped=False, minutes=None):
    session = active_session(state)
    if session['finished']:
        raise ValueError('This activity has already ended.')
    if session['section'] == 'strength' and not skipped:
        raise ValueError('Complete the strength sets first.')
    if session['section'] == 'yoga' and not skipped and session['pose_index'] < 5:
        raise ValueError('Complete the yoga cards first.')
    if session['section'] == 'brain' and not skipped and len(session['answers']) < 5:
        raise ValueError('Complete five puzzles first.')
    if type(skipped) is not bool:
        raise ValueError('Skip must be a boolean.')
    if session['section'] == 'relaxation' and not skipped and (type(minutes) is not int or minutes not in (3, 5)):
        raise ValueError('Choose three or five minutes.')
    performed = bool(session['feedback'] or session['answers'] or any(r.get('activity_id') == state['active_activity'] for r in state['logs']['sessions']))
    session.update(status=('partial' if performed else 'skipped') if skipped else 'completed', finished=True)
    if session['section'] == 'relaxation':
        session['completed_minutes'] = 0 if skipped else minutes
    state['session_done'] = True
    feedback_changed(state)
    event(state, 'activity_finished', activity_id=session['id'], status=session['status'])


def feedback_changed(state):
    state['logs']['version'] += 1
    state['pending_change'] = None


def log_yoga(state, effort, pain):
    session = active_session(state)
    if session['section'] != 'yoga' or session['finished']:
        raise ValueError('No yoga card is available.')
    if type(effort) is not int or type(pain) is not int or not 1 <= effort <= 10 or not 0 <= pain <= 10:
        raise ValueError('Enter valid pain and effort.')
    session['feedback'].append({'pose': session['pose_index'], 'effort': effort, 'pain': pain})
    session['pose_index'] += 1
    if pain >= 4:
        session.update(status='partial', finished=True)
    elif session['pose_index'] == 5:
        session.update(status='completed', finished=True)
    state['session_done'] = session['finished']
    feedback_changed(state)


def current_puzzle(state):
    session = active_session(state)
    if session['section'] != 'brain' or session['finished']:
        raise ValueError('No puzzle is available.')
    level = state['brain_level']
    used = sum(len(s['answers']) for s in state['activity_sessions'].values() if s['section'] == 'brain')
    return [p for p in activities.PUZZLES if p['level'] == level][used % 6]


def answer_puzzle(state, answer):
    puzzle = current_puzzle(state)
    if type(answer) is not int:
        raise ValueError('Enter a whole number.')
    correct = answer == puzzle['answer']
    session = active_session(state)
    session['answers'].append({'puzzle_id': puzzle['id'], 'level': puzzle['level'], 'answer': answer, 'correct': correct})
    streak = state['brain_streak']
    streak.append(correct)
    new_level = activities.next_level(state['brain_level'], streak)
    if len(streak) >= 3 and all(streak[-3:]) or len(streak) >= 2 and not any(streak[-2:]):
        state['brain_streak'] = []
    state['brain_level'] = new_level
    session['answers'][-1]['level_after'] = new_level
    feedback_changed(state)
    if len(session['answers']) == 5:
        session.update(status='completed', finished=True)
        state['session_done'] = True
    return correct, puzzle['explanation']


def start_next_week(state):
    if not eligible(state):
        raise ValueError('Training is blocked or stopped.')
    if state.get('pain_reviews'):
        raise ValueError('Later pain cancelled a next-week decision. Approve an easier goal with your coach before starting next week.')
    legacy_unfinished = any(r.get('week') == state['plan']['week'] and r.get('activity_id') is None for r in state['logs']['sessions']) and not state['session_done']
    if legacy_unfinished or any(not s['finished'] for s in state['activity_sessions'].values() if s['week'] == state['plan']['week']):
        raise ValueError('Finish or skip unfinished activities before moving to the next week.')
    state['history'].append(deepcopy(state['plan']))
    plan = deepcopy(state['next_plan'] or state['plan'])
    plan['week'] = state['plan']['week'] + 1
    plan['version'] = state['plan']['version'] + 1
    plan['start_date'] = str(date.fromisoformat(state['plan']['start_date']) + timedelta(days=7))
    for item in plan['exercises']:
        item['base_reps'] = item['reps']
    plan['adjusted_exercises'], plan['applied_ids'] = [], []
    schedule(plan)
    state.update(plan=plan, next_plan=None, pending_change=None, active_activity=None, cursor=0, set_index=0, session_done=False)
    feedback_changed(state)
    event(state, 'week_started', week=plan['week'])
