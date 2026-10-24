from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlmodel import Session
from ..deps import Consent, current_user, db_session

router = APIRouter()
class ConsentBody(BaseModel):
    collect_health_data: bool
    version: str = Field(min_length=1, max_length=40)

@router.post('/consent')
def consent(body: ConsentBody, user=Depends(current_user), db: Session = Depends(db_session)):
    if not body.collect_health_data or body.version != '2026-10-beta':
        raise HTTPException(422, 'Agree to the current consent before continuing.')
    record = Consent(user_id=user.id, collect_health_data=True, version=body.version)
    db.add(record)
    db.commit()
    db.refresh(record)
    return {'collect_health_data': True, 'version': record.version, 'timestamp': record.timestamp}

from typing import Literal
from fastapi import Request
from pydantic import StrictBool, StrictInt
from sqlmodel import select
from ..state_store import consent_required, mutate, load
from ..zinc_core import engine

class ProfileBody(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    age: StrictInt = Field(ge=20, le=110)
    level: Literal['beginner', 'active', 'trained']
    limits: list[Literal['knees', 'back', 'balance']] = []
    mci: StrictBool = False
    clinician_clearance: StrictBool = False

class SafetyBody(BaseModel):
    answers: dict[str, StrictBool]

class PlanBody(BaseModel):
    start_date: str | None = None
    choices: dict[str, list[StrictInt]] | None = None
    toggles: dict[str, StrictBool] = {}

@router.get('/me')
def me(user=Depends(current_user), db: Session = Depends(db_session)):
    state, version = load(db, user.id)
    consent = db.exec(select(Consent).where(Consent.user_id == user.id)).first()
    return {'user': {'name': user.name, 'email': user.email}, 'consented': bool(consent), 'version': version, 'state': state}

@router.put('/profile')
def profile(body: ProfileBody, request: Request, user=Depends(consent_required), db: Session = Depends(db_session)):
    def apply(s):
        if s['plan']:
            raise ValueError('A plan already exists. Profile screening cannot be replaced during training.')
        if not body.name.strip():
            raise ValueError('Enter your first name.')
        s['profile'].update(body.model_dump(), name=body.name.strip())
        s['safety_result'] = None
        s['screening_answers'] = {}
        user.name = body.name.strip()
        db.add(user)
        engine.event(s, 'profile_saved')
    return mutate(request, db, user, apply)

@router.get('/safety/questions')
def questions(user=Depends(consent_required)):
    return {'questions': engine.QUESTIONS, 'caveat': 'This shortened screen is not the full PAR-Q+. Content pending professional review. Follow clinician guidance and stop if you feel unwell.'}

@router.post('/safety')
def safety(body: SafetyBody, request: Request, user=Depends(consent_required), db: Session = Depends(db_session)):
    def apply(s):
        if s['plan']:
            raise ValueError('Screening cannot be replaced after plan creation.')
        result = engine.safety_check(body.answers)
        blocked = (s['profile']['age'] >= 80 or s['profile']['mci']) and not s['profile']['clinician_clearance']
        s['screening_answers'] = body.answers
        s['safety_result'] = result if not blocked else 'clinician'
        s['onboarding_step'] = 2
        engine.event(s, 'screening', result=s['safety_result'])
        message = ('Please see a clinician before starting. No plan will be generated and coaching is blocked. Seek urgent help for current severe symptoms.' if result == 'clinician' else 'Clinician sign-off is required. Return to your profile after obtaining guidance.' if blocked else 'Cleared with limits — supported mode' if result == 'limits' or s['profile']['age'] >= 80 or s['profile']['mci'] else "You're cleared to start")
        return {'result': 'clinician' if blocked or result == 'clinician' else 'cleared_limits' if result == 'limits' else 'cleared', 'signoff_block': blocked, 'message': message}
    return mutate(request, db, user, apply)

@router.post('/plan')
def plan(body: PlanBody, request: Request, user=Depends(consent_required), db: Session = Depends(db_session)):
    def apply(s):
        if s['plan']:
            raise ValueError('Your plan already exists.')
        if not s['screening_answers']:
            raise ValueError('Complete screening first.')
        if not set(body.toggles) <= {'yoga', 'brain'}:
            raise ValueError('Choose valid focus options.')
        s['profile']['toggles'] = {'yoga': False, 'brain': False, **body.toggles}
        initial = engine.make_week(s['profile'], s['safety_result'], engine.AVAILABLE, body.start_date)
        s['plan'] = engine.choose_days(initial, body.choices) if body.choices is not None else initial
        engine.event(s, 'plan_created')
    return mutate(request, db, user, apply)
