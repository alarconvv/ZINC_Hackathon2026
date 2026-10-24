"""Create the fictional demo once; never reset an existing account."""
import json, os
from datetime import date, timedelta
from sqlmodel import Session, SQLModel, select
from . import deps
from .auth import hasher
from .deps import User, UserState, Consent, AuditEvent
from .zinc_core import engine

def demo_state():
    s = engine.new_state(engine.MARIA)
    s['screening_answers'] = {k: False for k in engine.QUESTIONS}
    s['safety_result'] = engine.safety_check(s['screening_answers'])
    monday = date.today() - timedelta(days=date.today().weekday())
    s['plan'] = engine.make_week(s['profile'], s['safety_result'], engine.AVAILABLE, monday)
    occurrences = {section: 0 for section in engine.SECTIONS}
    for activity in s['plan']['activities']:
        section = activity['section']
        occurrences[section] += 1
        engine.start_activity(s, activity['id'])
        if section == 'strength':
            while not engine.active_session(s)['finished']:
                item = s['plan']['exercises'][s['cursor']]
                engine.log_set(s, item['id'], item['reps'], 5, 0)
                if occurrences[section] == 2 and s['cursor'] == 1:
                    engine.finish_activity(s, skipped=True)
        elif section == 'yoga':
            if occurrences[section] == 2:
                engine.finish_activity(s, skipped=True)
            else:
                for _ in range(5):
                    engine.log_yoga(s, 4, 0)
        elif section == 'brain':
            for index in range(5):
                puzzle = engine.current_puzzle(s)
                engine.answer_puzzle(s, puzzle['answer'] if index != 2 else -1)
        else:
            engine.finish_activity(s, minutes=3 if occurrences[section] == 1 else 5)
    s['pending_change'] = engine.progress(s['plan'], s['logs'], 'sit_to_stand', 'harder')
    engine.accept_pending_change(s)
    s['home_tests'] = [{'kind': 'chair_stand', 'value': 11, 'unit': 'stands', 'timestamp': str(monday) + 'T12:00:00+00:00'}]
    engine.event(s, 'fictional_demo_seeded')
    return s

def seed(db, password):
    if len(password) < 10:
        raise ValueError('Set DEMO_PASSWORD to at least ten characters.')
    if db.exec(select(User).where(User.email == 'maria@demo.zinc')).first():
        return False
    s = demo_state()
    user = User(email='maria@demo.zinc', name='Maria', password_hash=hasher.hash(password))
    db.add(user)
    db.add(UserState(user_id=user.id, data=json.dumps(s)))
    db.add(Consent(user_id=user.id, collect_health_data=True, version='2026-10-beta'))
    for event in s['events']:
        db.add(AuditEvent(user_id=user.id, data=json.dumps(event)))
    db.commit()
    return True

if __name__ == '__main__':
    SQLModel.metadata.create_all(deps.engine)
    with Session(deps.engine) as db:
        created = seed(db, os.getenv('DEMO_PASSWORD', ''))
    print('Fictional demo created.' if created else 'Existing demo preserved.')
