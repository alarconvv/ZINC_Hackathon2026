from test_onboarding import planned

def post(client, headers, path, body=None):
    response = client.post(path, headers=headers, json=body or {})
    if response.status_code == 200 and 'version' in response.json():
        headers['If-Match'] = str(response.json()['version'])
    return response

def test_strength_finish_and_conflict(client):
    h, s = planned(client)
    activity = next(a for a in s['plan']['activities'] if a['section'] == 'strength')
    assert post(client, h, f"/activities/{activity['id']}/start").status_code == 200
    stale = dict(h)
    for _ in range(12):
        response = post(client, h, '/activities/active/set', {'reps': 10, 'effort': 5, 'pain': 0})
        assert response.status_code == 200, response.text
    assert response.json()['view']['active']['finished']
    assert response.json()['view']['active']['count'] == 12
    assert post(client, stale, '/schedule', {'section': 'yoga', 'day': 6}).status_code == 409

def test_stop_and_symptoms(client):
    h, s = planned(client)
    assert post(client, h, '/symptoms', {'text': 'I have chest pain'}).json()['state']['stopped']
    paths = ['/activities/any/start', '/activities/active/set', '/activities/active/pose', '/activities/active/answer', '/activities/active/finish']
    bodies = [{}, {'reps': 10, 'effort': 5, 'pain': 0}, {'effort': 5, 'pain': 0}, {'answer': 3}, {}]
    for path, body in zip(paths, bodies):
        assert post(client, h, path, body).status_code == 423
    for path in ['/activities/active', '/activities/active/puzzle']:
        assert client.get(path, headers=h).status_code == 423
