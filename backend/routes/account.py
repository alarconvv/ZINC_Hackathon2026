import json
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlmodel import Session, select, delete
from ..deps import User, UserState, AuditEvent, Consent, current_user, db_session
from ..state_store import consent_required, load, expected
from ..zinc_core import progress_board
from .home_tests import scoreboard

router = APIRouter()
@router.get('/progress')
def progress(week: int | None = None, user=Depends(consent_required), db: Session = Depends(db_session)):
    s, version = load(db, user.id)
    plans = s['history'] + ([s['plan']] if s['plan'] else [])
    plan = next((p for p in plans if p['week'] == week), None) if week is not None else s['plan']
    if not plan:
        raise HTTPException(404, 'No saved week was found.')
    sessions = [a for a in s['activity_sessions'].values() if a['week'] == plan['week']]
    answers = [answer for a in sessions for answer in a['answers']]
    correct = sum(a['correct'] for a in answers)
    return {'scoreboard': scoreboard(s), 'version': version, 'week': plan['week'], 'weeks': [{'week': p['week'], 'start_date': p['start_date']} for p in plans],
        'date_range': progress_board.date_range(plan), 'board': progress_board.summarize(plan, s['activity_sessions']),
        'reasoning': {'answers': len(answers), 'correct': correct, 'accuracy': round(100 * correct / len(answers)) if answers else None},
        'relaxation_minutes': sum(a.get('completed_minutes', 0) for a in sessions if a['section'] == 'relaxation'),
        'feedback': progress_board.feedback_rows(s, plan), 'accepted_changes': [e for e in s['events'] if e['event'] == 'accepted' and e.get('week') == plan['week']]}

@router.get('/account/export')
def export(user=Depends(current_user), db: Session = Depends(db_session)):
    s, version = load(db, user.id)
    return {'account': {'id': user.id, 'name': user.name, 'email': user.email}, 'state': s, 'version': version,
        'consents': [c.model_dump(exclude={'id', 'user_id'}) for c in db.exec(select(Consent).where(Consent.user_id == user.id))],
        'events': [json.loads(e.data) for e in db.exec(select(AuditEvent).where(AuditEvent.user_id == user.id))]}

@router.delete('/account', status_code=204)
def delete_account(request: Request, user=Depends(current_user), db: Session = Depends(db_session)):
    _, version = load(db, user.id)
    expected(request, version)
    for model in (AuditEvent, Consent, UserState):
        db.exec(delete(model).where(model.user_id == user.id))
    db.delete(user)
    db.commit()
    return Response(status_code=204)
