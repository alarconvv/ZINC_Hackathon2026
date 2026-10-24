from datetime import datetime, timezone, timedelta
from sqlmodel import Session
from backend import deps
from backend.state_store import load, save
from test_onboarding import planned
from test_activities import post

def test_home_results_are_record_only_and_retest_is_eight_weeks(client):
    h, before = planned(client)
    r = post(client, h, '/tests', {'kind': 'chair_stand', 'value': 12})
    assert r.status_code == 200
    after = r.json()['state']
    for field in ('plan', 'next_plan', 'logs', 'pending_change'):
        assert after[field] == before[field]
    assert r.json()['scoreboard']['records'][0]['value'] == 12
    uid = client.get('/account/export', headers=h).json()['account']['id']
    with Session(deps.engine) as db:
        state, version = load(db, uid)
        state['home_tests'][0]['timestamp'] = (datetime.now(timezone.utc)-timedelta(weeks=8,days=1)).isoformat()
        save(db,uid,state,version)
    assert client.get('/progress',headers=h).json()['scoreboard']['retest_due']
    client.post('/stop',headers=h)
    assert post(client,h,'/tests',{'kind':'chair_stand','value':15}).status_code == 423
