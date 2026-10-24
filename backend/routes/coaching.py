import asyncio, os
from copy import deepcopy
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from sqlmodel import Session
from ..deps import db_session
from ..state_store import consent_required, load, save, expected, unlocked, mutate
from ..views import screen_data
from ..zinc_core import engine, coach

router = APIRouter()
class MessageBody(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
class PreviewBody(BaseModel):
    exercise_id: str
    direction: str

@router.post('/coach')
async def coach_message(body: MessageBody, request: Request, user=Depends(consent_required), db: Session = Depends(db_session)):
    s, version = load(db, user.id)
    unlocked(s)
    if not engine.eligible(s):
        raise HTTPException(422, 'Complete screening and create your plan first.')
    if engine.red_flag(body.message):
        from .activities import stop
        stop(user, db)
        raise HTTPException(423, engine.STOP_MESSAGE)
    expected(request, version)
    working = deepcopy(s)
    working['messages'].append({'role': 'user', 'text': body.message})
    try:
        reply = await asyncio.wait_for(asyncio.to_thread(coach.coach_turn, body.message, working,
            {key: os.getenv(key) for key in ('GEMINI_API_KEY', 'MODEL')}, getattr(request.app.state, 'coach_runner', None)), timeout=30)
    except asyncio.TimeoutError:
        # The timed-out worker owns an isolated copy and can never commit later.
        working = deepcopy(s)
        working['messages'].append({'role': 'user', 'text': body.message})
        working['pending_change'] = None
        engine.event(working, 'fallback', failure_kind='timeout')
        reply = coach.FALLBACK
    working['messages'].append({'role': 'assistant', 'text': reply})
    version = save(db, user.id, working, version)
    return {'version': version, 'state': working, 'view': screen_data(working), 'reply': reply, 'pending_change': working['pending_change']}

@router.post('/proposal/preview')
def preview(body: PreviewBody, request: Request, user=Depends(consent_required), db: Session = Depends(db_session)):
    def apply(s):
        if not engine.eligible(s):
            raise ValueError('Complete screening and create your plan first.')
        s['pending_change'] = engine.progress(s['plan'], s['logs'], body.exercise_id, body.direction)
        engine.event(s, 'rules_preview', exercise_id=body.exercise_id)
    return mutate(request, db, user, apply)

@router.post('/proposal/accept')
def accept(request: Request, user=Depends(consent_required), db: Session = Depends(db_session)):
    return mutate(request, db, user, engine.accept_pending_change)

@router.post('/proposal/decline')
def decline(request: Request, user=Depends(consent_required), db: Session = Depends(db_session)):
    return mutate(request, db, user, engine.decline_pending_change)

@router.post('/week/next')
def next_week(request: Request, user=Depends(consent_required), db: Session = Depends(db_session)):
    return mutate(request, db, user, engine.start_next_week)
