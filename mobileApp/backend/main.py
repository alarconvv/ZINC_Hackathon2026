from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from contextlib import asynccontextmanager
from . import deps, auth
@asynccontextmanager
async def lifespan(app):
    deps.SQLModel.metadata.create_all(deps.engine)
    yield

app = FastAPI(lifespan=lifespan, title='ZINC Beta', version='0.1.0')
app.add_middleware(CORSMiddleware, allow_origins=os.getenv('CORS_ORIGINS', 'http://localhost:8081,http://127.0.0.1:8081').split(','), allow_methods=['GET', 'POST', 'PUT', 'DELETE'], allow_headers=['Authorization', 'Content-Type', 'If-Match'])

@app.get('/health')
def health():
    return {'status': 'ok', 'service': 'ZINC Beta'}

app.include_router(auth.router)
from .routes import onboarding
app.include_router(onboarding.router)
from .routes import activities
app.include_router(activities.router)
from .routes import coaching
app.include_router(coaching.router)
from .routes import account
app.include_router(account.router)
from .routes import home_tests
app.include_router(home_tests.router)
