from test_onboarding import planned
from test_activities import post

def test_proposal_acceptance_and_rollover(client):
    h, s = planned(client)
    activity = next(a for a in s['plan']['activities'] if a['section'] == 'strength')
    post(client, h, f"/activities/{activity['id']}/start")
    post(client, h, '/activities/active/set', {'reps': 10, 'effort': 5, 'pain': 0})
    assert post(client, h, '/proposal/preview', {'exercise_id': 'sit_to_stand', 'direction': 'harder'}).status_code == 200
    assert post(client, h, '/proposal/accept').status_code == 422
    for _ in range(11):
        post(client, h, '/activities/active/set', {'reps': 10, 'effort': 5, 'pain': 0})
    post(client, h, '/proposal/preview', {'exercise_id': 'sit_to_stand', 'direction': 'harder'})
    result = post(client, h, '/proposal/accept')
    assert result.status_code == 200, result.text
    assert result.json()['state']['plan']['exercises'][0]['reps'] == 10
    assert result.json()['state']['next_plan']['exercises'][0]['reps'] == 11
    assert post(client, h, '/week/next').json()['state']['plan']['exercises'][0]['reps'] == 11

def test_coach_stub_and_stop(client):
    client.app.state.coach_runner = lambda message, context, secrets: 'Keep following your displayed plan.'
    try:
        h, s = planned(client)
        result = post(client, h, '/coach', {'message': 'Hello'})
        assert result.status_code == 200, result.text
        assert result.json()['reply'] == 'Keep following your displayed plan.'
        assert result.json()['state']['messages'][-1]['source'] == 'gemini'
        assert result.json()['view']['coach_source'] == 'gemini'
        assert post(client, h, '/coach', {'message': 'I feel dizzy'}).status_code == 423
        for path, body in [('/coach', {'message': 'Hello'}), ('/proposal/preview', {'exercise_id': 'row', 'direction': 'same'}), ('/proposal/accept', {}), ('/proposal/decline', {}), ('/week/next', {})]:
            assert post(client, h, path, body).status_code == 423
    finally:
        del client.app.state.coach_runner
