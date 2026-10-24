import os, sqlite3
from sqlalchemy import event as sa_event
from sqlalchemy.engine import Engine
from datetime import datetime, timezone
from uuid import uuid4
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel import SQLModel, Field, Session, create_engine
import jwt

class User(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    email: str = Field(index=True, unique=True)
    password_hash: str
    name: str

class UserState(SQLModel, table=True):
    user_id: str = Field(primary_key=True, foreign_key='user.id')
    data: str
    version: int = 0

class AuditEvent(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: str = Field(index=True, foreign_key='user.id')
    data: str

class Consent(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: str = Field(index=True, foreign_key='user.id')
    collect_health_data: bool
    version: str
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

@sa_event.listens_for(Engine, 'connect')
def sqlite_foreign_keys(connection, _record):
    if isinstance(connection, sqlite3.Connection):
        connection.execute('PRAGMA foreign_keys=ON')

def database_url(value):
    for prefix in ('postgres://', 'postgresql://'):
        if value.startswith(prefix):
            return 'postgresql+psycopg://' + value[len(prefix):]
    return value

url = database_url(os.getenv('DATABASE_URL', 'sqlite:///backend/zinc.db'))
engine = create_engine(url, hide_parameters=True, connect_args={'check_same_thread': False} if url.startswith('sqlite') else {})

def db_session():
    with Session(engine) as db:
        yield db

def jwt_secret():
    secret = os.getenv('JWT_SECRET', '')
    if len(secret) < 32:
        raise HTTPException(503, 'Server authentication is not configured.')
    return secret

bearer = HTTPBearer(auto_error=False)
def current_user(credentials: HTTPAuthorizationCredentials | None = Depends(bearer), db: Session = Depends(db_session)):
    try:
        if not credentials:
            raise ValueError()
        payload = jwt.decode(credentials.credentials, jwt_secret(), algorithms=['HS256'], options={'require': ['exp', 'sub']})
        user = db.get(User, payload['sub'])
        if not user:
            raise ValueError()
        return user
    except (jwt.PyJWTError, ValueError):
        raise HTTPException(401, 'Sign in to continue.') from None
