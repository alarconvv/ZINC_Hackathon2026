from test_onboarding import planned
from conftest import register
from sqlmodel import Session, select
from backend import deps
from backend.deps import User, UserState, AuditEvent, Consent

def test_isolation_export_and_hard_delete(client):
    h, s = planned(client)
    other = register(client, 'other@example.com')
    assert client.get('/me', headers=other).json()['state']['plan'] is None
    data = client.get('/account/export', headers=h).json()
    assert data['state']['plan'] == s['plan']
    assert data['consents'] and data['events']
    assert 'password_hash' not in str(data)
    assert client.get('/progress', headers=h).json()['board']['percent'] == 0
    assert client.delete('/account', headers=h).status_code == 204
    assert client.get('/me', headers=h).status_code == 401
    with Session(deps.engine) as db:
        user_id = data['account']['id']
        assert db.get(User, user_id) is None
        assert db.get(UserState, user_id) is None
        assert not db.exec(select(AuditEvent).where(AuditEvent.user_id == user_id)).all()
        assert not db.exec(select(Consent).where(Consent.user_id == user_id)).all()
    assert client.get('/me', headers=other).status_code == 200
