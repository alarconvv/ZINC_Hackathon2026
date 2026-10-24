"""Whole-core snapshots with compare-and-swap; clients never submit state."""
import json
from fastapi import Depends, HTTPException, Request
from sqlalchemy import update
from sqlmodel import Session, select
from .deps import UserState, AuditEvent, Consent, current_user, db_session
from .zinc_core import engine

def consent_required(user=Depends(current_user), db: Session = Depends(db_session)):
    if not db.exec(select(Consent).where(Consent.user_id == user.id, Consent.collect_health_data == True)).first():
        raise HTTPException(403, 'Consent is required before onboarding.')
    return user

def load(db, user_id):
    row = db.get(UserState, user_id)
    if not row:
        raise HTTPException(401, 'Sign in to continue.')
    return json.loads(row.data), row.version

def save(db, user_id, state, version):
    old = db.get(UserState, user_id)
    previous = len(json.loads(old.data)['events'])
    changed = db.execute(update(UserState).where(UserState.user_id == user_id, UserState.version == version).values(data=json.dumps(state), version=version + 1))
    if changed.rowcount != 1:
        db.rollback()
        raise HTTPException(409, 'Your data changed. Refresh and try again.')
    for event in state['events'][previous:]:
        db.add(AuditEvent(user_id=user_id, data=json.dumps(event)))
    db.commit()
    return version + 1

def expected(request, version):
    value = request.headers.get('If-Match')
    if value is None:
        raise HTTPException(428, 'Refresh your data before saving.')
    if value != str(version):
        raise HTTPException(409, 'Your data changed. Refresh and try again.')

def unlocked(state):
    if state['stopped']:
        raise HTTPException(423, engine.STOP_MESSAGE)

def mutate(request: Request, db, user, fn, *, check_stop=True):
    state, version = load(db, user.id)
    if check_stop:
        unlocked(state)
    expected(request, version)
    try:
        extra = fn(state) or {}
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from None
    version = save(db, user.id, state, version)
    from .views import screen_data
    return {'version': version, 'state': state, 'view': screen_data(state), **extra}
