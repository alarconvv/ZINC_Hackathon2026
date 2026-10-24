import os
os.environ['JWT_SECRET'] = 'test-only-secret-never-use-for-hosting-123456'
import pytest
from sqlmodel import SQLModel, create_engine
from fastapi.testclient import TestClient
from backend import deps, auth
from backend.main import app

@pytest.fixture
def client(tmp_path, monkeypatch):
    db = create_engine('sqlite:///' + str(tmp_path / 'test.db'), connect_args={'check_same_thread': False})
    monkeypatch.setattr(deps, 'engine', db)
    auth.attempts.clear()
    SQLModel.metadata.create_all(db)
    with TestClient(app) as client:
        yield client
    db.dispose()

def register(client, email='maria@example.com'):
    response = client.post('/auth/register', json={'email': email, 'password': 'a-long-test-password', 'name': 'Maria'})
    assert response.status_code == 201, response.text
    return {'Authorization': 'Bearer ' + response.json()['access_token']}
