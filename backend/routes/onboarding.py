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
