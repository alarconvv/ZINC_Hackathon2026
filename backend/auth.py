from collections import defaultdict, deque
from datetime import datetime, timedelta, timezone
from threading import Lock
from time import monotonic
import re, json
from argon2 import PasswordHasher
from argon2.exceptions import VerificationError, InvalidHashError
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field as PField, field_validator
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select
import jwt
from .deps import User, UserState, db_session, jwt_secret
from .zinc_core import engine

router = APIRouter(prefix='/auth', tags=['accounts'])
hasher = PasswordHasher()
# Hashing even for unknown accounts reduces timing differences.
dummy = hasher.hash('not-an-account-password')
attempts = defaultdict(deque)
lock = Lock()

class Login(BaseModel):
    email: str = PField(max_length=254)
    password: str = PField(max_length=1024)
    @field_validator('email')
    @classmethod
    def email_valid(cls, value):
        value = value.strip().lower()
        if not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+', value):
            raise ValueError('Enter a valid email address.')
        return value

class Register(Login):
    password: str = PField(min_length=10, max_length=1024)
    name: str = PField(min_length=1, max_length=80)
    @field_validator('name')
    @classmethod
    def name_valid(cls, value):
        if not value.strip():
            raise ValueError('Enter your first name.')
        return value.strip()

def token(user):
    return {'access_token': jwt.encode({'sub': user.id, 'exp': datetime.now(timezone.utc) + timedelta(hours=24)}, jwt_secret(), algorithm='HS256'), 'token_type': 'bearer', 'user': {'name': user.name, 'email': user.email}}

@router.post('/register', status_code=201)
def register(body: Register, db: Session = Depends(db_session)):
    jwt_secret()
    user = User(email=body.email, name=body.name, password_hash=hasher.hash(body.password))
    state = engine.new_state({'name': body.name, 'age': 52, 'level': 'beginner', 'limits': [], 'mci': False, 'clinician_clearance': False, 'toggles': {'yoga': False, 'brain': False}})
    try:
        db.add(user)
        db.flush()
        db.add(UserState(user_id=user.id, data=json.dumps(state)))
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, 'Unable to create this account. Try signing in.') from None
    return token(user)

@router.post('/login')
def login(body: Login, db: Session = Depends(db_session)):
    with lock:
        now = monotonic()
        # Expire inactive entries as well as each email's current window.
        for email in list(attempts):
            while attempts[email] and attempts[email][0] <= now - 60:
                attempts[email].popleft()
            if not attempts[email]:
                del attempts[email]
        if len(attempts[body.email]) >= 5:
            raise HTTPException(429, 'Too many attempts. Try again in a minute.', headers={'Retry-After': '60'})
        attempts[body.email].append(now)
    user = db.exec(select(User).where(User.email == body.email)).first()
    try:
        hasher.verify(user.password_hash if user else dummy, body.password)
    except (VerificationError, InvalidHashError):
        raise HTTPException(401, 'Email or password is incorrect.') from None
    if not user:
        raise HTTPException(401, 'Email or password is incorrect.')
    return token(user)
