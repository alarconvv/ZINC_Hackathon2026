from copy import deepcopy
import pytest
from fastapi import HTTPException
from sqlmodel import Session
from backend import deps
from backend.state_store import load, save
from backend.zinc_core import engine
from test_onboarding import planned, screened
from test_activities import post


def test_all_four_sections_and_saved_summary(client):
    h, s = planned(client)
    for section in ('yoga', 'brain', 'relaxation'):
        a = next(a for a in s['plan']['activities'] if a['section'] == section)
        result = post(client, h, f"/activities/{a['id']}/start")
        assert result.status_code == 200
        if section == 'yoga':
            for _ in range(5):
                result = post(client, h, '/activities/active/pose', {'effort': 4, 'pain': 0})
                assert result.status_code == 200
        elif section == 'brain':
            for _ in range(5):
                assert 'answer' not in client.get('/activities/active/puzzle', headers=h).json()['puzzle']
                result = post(client, h, '/activities/active/answer', {'answer': 0})
                assert result.status_code == 200
                assert 'explanation' in result.json()
        else:
            result = post(client, h, '/activities/active/finish', {'minutes': 5})
        assert result.json()['view']['active']['finished']
    progress = client.get('/progress', headers=h).json()
    assert progress['board']['done'] == 3
    assert progress['reasoning']['answers'] == 5
    assert progress['relaxation_minutes'] == 5
    assert len(progress['feedback']) == 5


def test_database_compare_and_swap(client):
    h, s = planned(client)
    uid = client.get('/account/export', headers=h).json()['account']['id']
    with Session(deps.engine) as a, Session(deps.engine) as b:
        first, v1 = load(a, uid)
        second, v2 = load(b, uid)
        engine.event(first, 'first_writer')
        save(a, uid, first, v1)
        engine.event(second, 'stale_writer')
        with pytest.raises(HTTPException) as exc:
            save(b, uid, second, v2)
        assert exc.value.status_code == 409
    saved = client.get('/account/export', headers=h).json()
    assert any(e['event'] == 'first_writer' for e in saved['events'])
    assert not any(e['event'] == 'stale_writer' for e in saved['events'])


def test_foreign_activity_and_tampered_state_rejected(client):
    first, s = planned(client)
    other, _ = screened(client, 'other@example.com')
    activity = s['plan']['activities'][0]['id']
    assert post(client, other, f'/activities/{activity}/start').status_code == 422
    result = client.get('/plan', headers=first).json()
    assert result['state']['plan'] == s['plan']
    assert client.post('/activities/active/set', headers=first, json={'reps': 10, 'effort': 0, 'pain': 0}).status_code == 422
    assert client.post('/schedule', headers={'Authorization': first['Authorization']}, json={'day': 6, 'section': 'yoga'}).status_code == 428


def test_stop_overrides_stale_client_and_survives_new_login(client):
    h, s = planned(client)
    activity = s['plan']['activities'][0]['id']
    post(client, h, f'/activities/{activity}/start')
    response = client.post('/stop', headers={**h, 'If-Match': '0'})
    assert response.status_code == 200
    token = client.post('/auth/login', json={'email': 'maria@example.com', 'password': 'a-long-test-password'}).json()['access_token']
    h['Authorization'] = 'Bearer ' + token
    assert client.get('/plan', headers=h).json()['state']['stopped']
    assert client.get('/activities/active', headers=h).status_code == 423


def test_red_flags_override_a_stale_version(client):
    for suffix, path, body in [('symptom', '/symptoms', {'text': 'chest pain'}), ('coach', '/coach', {'message': 'I feel dizzy'})]:
        h, s = planned(client, suffix + '@example.com')
        response = client.post(path, headers={**h, 'If-Match': '0'}, json=body)
        assert response.status_code == (200 if suffix == 'symptom' else 423)
        assert client.get('/plan', headers=h).json()['state']['stopped']


def test_first_run_guide_dismissal_survives_rollover(client):
    h, original = planned(client)
    result = post(client, h, '/guide/dismiss')
    assert result.json()['state']['tour_done']
    assert result.json()['state']['plan'] == original['plan']
    post(client, h, '/week/next')
    assert client.get('/plan', headers=h).json()['state']['tour_done']
