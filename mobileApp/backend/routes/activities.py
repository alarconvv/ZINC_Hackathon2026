from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import FileResponse
from pydantic import BaseModel, StrictInt, StrictBool, Field
from sqlmodel import Session
from ..deps import db_session
from ..state_store import consent_required, load, save, unlocked, mutate
from ..views import screen_data
from ..zinc_core import engine

router = APIRouter()
class ScheduleBody(BaseModel):
    activity_id: str | None = None
    day: StrictInt | None = None
    section: str | None = None
    remove: StrictBool = False
class SetBody(BaseModel):
    reps: StrictInt
    effort: StrictInt
    pain: StrictInt
class PoseBody(BaseModel):
    effort: StrictInt
    pain: StrictInt
class AnswerBody(BaseModel):
    answer: StrictInt
class FinishBody(BaseModel):
    skipped: StrictBool = False
    minutes: StrictInt | None = None
class SymptomsBody(BaseModel):
    text: str = Field(max_length=2000)

@router.get('/plan')
def get_plan(user=Depends(consent_required), db: Session = Depends(db_session)):
    state, version = load(db, user.id)
    return {'version': version, 'state': state, 'view': screen_data(state)}

@router.post('/schedule')
def schedule(body: ScheduleBody, request: Request, user=Depends(consent_required), db: Session = Depends(db_session)):
    def apply(s):
        engine.change_schedule(s, **body.model_dump())
    return mutate(request, db, user, apply)

@router.post('/activities/{activity_id}/start')
def start(activity_id: str, request: Request, user=Depends(consent_required), db: Session = Depends(db_session)):
    def apply(s):
        engine.start_activity(s, activity_id)
    return mutate(request, db, user, apply)

@router.post('/activities/{activity_id}/skip')
def skip_activity(activity_id: str, request: Request, user=Depends(consent_required), db: Session = Depends(db_session)):
    def apply(s):
        active = s['activity_sessions'].get(s.get('active_activity'))
        if active and not active['finished'] and active['id'] != activity_id:
            raise ValueError('Finish or skip your current activity first. Your recorded work is saved.')
        engine.start_activity(s, activity_id)
        engine.finish_activity(s, skipped=True)
    return mutate(request, db, user, apply)

@router.get('/activities/active')
def active(user=Depends(consent_required), db: Session = Depends(db_session)):
    s, version = load(db, user.id)
    unlocked(s)
    try:
        engine.active_session(s)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from None
    return {'version': version, 'state': s, 'view': screen_data(s)}

@router.post('/activities/active/set')
def log_set(body: SetBody, request: Request, user=Depends(consent_required), db: Session = Depends(db_session)):
    def apply(s):
        engine.active_session(s)
        item = s['plan']['exercises'][s['cursor']] if s['cursor'] < len(s['plan']['exercises']) else None
        if not item:
            raise ValueError('This activity has already ended.')
        engine.log_set(s, item['id'], body.reps, body.effort, body.pain)
    return mutate(request, db, user, apply)

@router.post('/activities/active/pose')
def pose(body: PoseBody, request: Request, user=Depends(consent_required), db: Session = Depends(db_session)):
    return mutate(request, db, user, lambda s: engine.log_yoga(s, body.effort, body.pain))

@router.get('/activities/active/puzzle')
def puzzle(user=Depends(consent_required), db: Session = Depends(db_session)):
    s, version = load(db, user.id)
    unlocked(s)
    try:
        item = engine.current_puzzle(s)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from None
    return {'version': version, 'puzzle': {k: v for k, v in item.items() if k not in ('answer', 'explanation')}}

@router.post('/activities/active/answer')
def answer(body: AnswerBody, request: Request, user=Depends(consent_required), db: Session = Depends(db_session)):
    def apply(s):
        correct, explanation = engine.answer_puzzle(s, body.answer)
        return {'correct': correct, 'explanation': explanation}
    return mutate(request, db, user, apply)

@router.post('/activities/active/finish')
def finish(body: FinishBody, request: Request, user=Depends(consent_required), db: Session = Depends(db_session)):
    return mutate(request, db, user, lambda s: engine.finish_activity(s, **body.model_dump()))

@router.post('/symptoms')
def symptoms(body: SymptomsBody, request: Request, user=Depends(consent_required), db: Session = Depends(db_session)):
    if engine.red_flag(body.text):
        return stop(user, db)
    def apply(s):
        if engine.red_flag(body.text):
            engine.stop(s)
            return {'message': engine.STOP_MESSAGE}
        return {'message': 'Stop if you feel unwell. Follow clinician guidance for any concerns.'}
    return mutate(request, db, user, apply)

@router.post('/stop')
def stop(user=Depends(consent_required), db: Session = Depends(db_session)):
    # Stop must win even when the client has an old version.
    for _ in range(5):
        db.expire_all()
        s, version = load(db, user.id)
        if not s['stopped']:
            engine.stop(s)
        try:
            version = save(db, user.id, s, version)
            return {'version': version, 'state': s, 'view': screen_data(s), 'message': engine.STOP_MESSAGE}
        except HTTPException as exc:
            if exc.status_code != 409:
                raise
    raise HTTPException(409, 'Retry Stop immediately.')

@router.get('/content/{filename}')
def content(filename: str):
    allowed = {item['image'] for item in engine.catalog()}
    if filename not in allowed:
        raise HTTPException(404)
    return FileResponse(Path(engine.__file__).parent / 'content/img' / filename, media_type='image/svg+xml')

@router.post('/guide/dismiss')
def dismiss_guide(request: Request, user=Depends(consent_required), db: Session = Depends(db_session)):
    def apply(s):
        s['tour_done'] = True
    return mutate(request, db, user, apply)
