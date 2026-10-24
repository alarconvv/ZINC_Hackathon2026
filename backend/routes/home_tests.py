"""Record-only results: never call progression or alter prescriptions."""
from datetime import datetime, timezone, timedelta
from typing import Literal
from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, Field, StrictInt
from sqlmodel import Session
from ..deps import db_session
from ..state_store import consent_required, load, mutate
from ..zinc_core import engine
router = APIRouter()
class TestBody(BaseModel):
    kind: Literal['chair_stand', 'single_leg_balance']
    value: StrictInt = Field(ge=0, le=500)

def scoreboard(s):
    records = s.get('home_tests', [])
    latest = max((datetime.fromisoformat(r['timestamp']) for r in records), default=None)
    due = bool(latest and datetime.now(timezone.utc) - latest >= timedelta(weeks=8))
    return {'records': records, 'retest_due': due}

@router.get('/tests')
def history(user=Depends(consent_required), db: Session = Depends(db_session)):
    s, version = load(db, user.id)
    return {'version': version, **scoreboard(s)}

@router.post('/tests')
def record(body: TestBody, request: Request, user=Depends(consent_required), db: Session = Depends(db_session)):
    def apply(s):
        if not engine.eligible(s):
            raise ValueError('Complete screening and create your plan before recording a home test.')
        if body.kind == 'single_leg_balance' and body.value > 30:
            raise ValueError('Record at most 30 seconds for this timer.')
        s.setdefault('home_tests', []).append({'kind': body.kind, 'value': body.value, 'unit': 'stands' if body.kind == 'chair_stand' else 'seconds', 'timestamp': datetime.now(timezone.utc).isoformat()})
        engine.event(s, 'home_test_recorded', kind_name=body.kind)
        return {'scoreboard': scoreboard(s)}
    return mutate(request, db, user, apply)
