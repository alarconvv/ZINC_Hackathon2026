from copy import deepcopy
from datetime import date
from test_onboarding import planned, screened
from test_activities import post


def test_suggested_week_is_read_only_and_matches_plan(client):
    h, before = screened(client)
    response = client.get('/plan/suggestion', headers=h)
    assert response.status_code == 200
    suggestion = response.json()
    assert len(suggestion['choices']['strength']) == 2
    assert client.get('/me', headers=h).json()['version'] == before['version']
    result = post(client, h, '/plan', {'choices': suggestion['choices'], 'start_date': suggestion['start_date']})
    assert result.status_code == 200
    assert len(result.json()['view']['activities']) == 8
    assert client.get('/plan/suggestion', headers=h).status_code == 422


def test_suggestion_respects_clinician_gate(client):
    h, _ = screened(client, symptom=True)
    assert client.get('/plan/suggestion', headers=h).status_code == 422


def test_remove_baseline_keeps_recommendation_and_survives_rollover(client):
    h, s = planned(client)
    activity = next(a for a in s['plan']['activities'] if a['section'] == 'strength')
    result = post(client, h, '/schedule', {'activity_id': activity['id'], 'remove': True})
    assert result.status_code == 200, result.text
    snapshot = result.json()
    assert len(snapshot['state']['plan']['activities']) == 7
    assert snapshot['state']['logs'] == {**s['logs'], 'version': s['logs']['version'] + 1}
    assert snapshot['state']['events'][-1]['event'] == 'activity_removed'
    strength = next(r for r in snapshot['view']['recommendations'] if r['section'] == 'strength')
    assert strength == {'section': 'strength', 'scheduled': 1, 'recommended': 2}
    next_week = post(client, h, '/week/next')
    assert next_week.status_code == 200
    assert len(next_week.json()['state']['plan']['activities']) == 7
    assert post(client, h, '/schedule', {'section': 'strength', 'day': 2}).status_code == 422
    assert post(client, h, '/schedule', {'section': 'strength', 'day': 0}).status_code == 200


def test_initial_week_still_requires_recommended_days(client):
    h, _ = screened(client)
    assert post(client, h, '/plan', {'choices': {'strength': [0], 'yoga': [1, 5], 'brain': [1, 5], 'relaxation': [1, 5]}}).status_code == 422


def test_skip_preserves_partial_work_and_cannot_remove_started_activity(client):
    h, s = planned(client)
    activity = next(a for a in s['plan']['activities'] if a['section'] == 'strength')
    post(client, h, f"/activities/{activity['id']}/start")
    result = post(client, h, '/activities/active/set', {'reps': 10, 'effort': 5, 'pain': 0}).json()
    records = deepcopy(result['state']['logs']['sessions'])
    assert post(client, h, '/schedule', {'activity_id': activity['id'], 'remove': True}).status_code == 422
    result = post(client, h, f"/activities/{activity['id']}/skip")
    assert result.status_code == 200
    state = result.json()['state']
    assert state['activity_sessions'][activity['id']]['finished']
    assert state['activity_sessions'][activity['id']]['status'] == 'partial'
    assert state['logs']['sessions'] == records
    assert post(client, h, f"/activities/{activity['id']}/skip").status_code == 422


def test_skip_unstarted_activity_does_not_count_as_completed(client):
    h, s = planned(client)
    activity = next(a for a in s['plan']['activities'] if a['section'] == 'yoga')
    result = post(client, h, f"/activities/{activity['id']}/skip")
    assert result.status_code == 200
    assert result.json()['state']['activity_sessions'][activity['id']]['status'] == 'skipped'
    assert client.get('/progress', headers=h).json()['board']['done'] == 0
    post(client, h, '/stop')
    assert post(client, h, f"/activities/{activity['id']}/skip").status_code == 423


def test_today_action_and_next_week_preview(client, monkeypatch):
    from backend import views
    class Monday(date):
        @classmethod
        def today(cls):
            return cls(2026, 10, 19)
    monkeypatch.setattr(views, 'date', Monday)
    h, _ = planned(client)
    view = client.get('/plan', headers=h).json()['view']
    assert view['today_action']['kind'] == 'start'
    assert view['next_week']['week'] == 2
    assert view['next_week']['start_date'] == '2026-10-26'
    assert view['next_week']['end_date'] == '2026-11-01'
    target = view['today_action']['activity']['id']
    assert post(client, h, f'/activities/{target}/start').json()['view']['today_action']['kind'] == 'resume'
    post(client, h, f'/activities/{target}/skip')
    assert client.get('/plan', headers=h).json()['view']['today_action']['kind'] == 'rest'


def test_empty_schedule_has_empty_action_and_no_division_error(client):
    h, s = planned(client)
    for activity in s['plan']['activities']:
        result = post(client, h, '/schedule', {'activity_id': activity['id'], 'remove': True})
        assert result.status_code == 200
    assert result.json()['view']['today_action']['kind'] == 'empty'
    assert client.get('/progress', headers=h).json()['board']['percent'] == 0
