from conftest import register

def screened(client, email='maria@example.com', age=52, symptom=False, clearance=False, mci=False):
    headers = register(client, email)
    assert client.get('/safety/questions', headers=headers).status_code == 403
    assert client.post('/consent', headers=headers, json={'collect_health_data': True, 'version': '2026-10-beta'}).status_code == 200
    response = client.put('/profile', headers={**headers, 'If-Match': '0'}, json={'name': 'Maria', 'age': age, 'level': 'beginner', 'limits': ['knees'], 'mci': mci, 'clinician_clearance': clearance})
    assert response.status_code == 200, response.text
    answers = {key: False for key in client.get('/safety/questions', headers=headers).json()['questions']}
    answers['chest'] = symptom
    response = client.post('/safety', headers={**headers, 'If-Match': '1'}, json={'answers': answers})
    assert response.status_code == 200, response.text
    return {**headers, 'If-Match': '2'}, response.json()

def planned(client, email='maria@example.com'):
    headers, _ = screened(client, email)
    response = client.post('/plan', headers=headers, json={'start_date': '2026-10-19'})
    assert response.status_code == 200, response.text
    return {**headers, 'If-Match': str(response.json()['version'])}, response.json()['state']

def test_plan_and_safety_gates(client):
    headers, s = planned(client)
    assert s['plan']['tier'] == 'Protect'
    headers, result = screened(client, 'blocked@example.com', symptom=True)
    assert result['result'] == 'clinician'
    assert client.post('/plan', headers=headers, json={}).status_code == 422
    headers, result = screened(client, 'older@example.com', age=82)
    assert result['signoff_block']
    assert client.post('/plan', headers=headers, json={}).status_code == 422
    headers, result = screened(client, 'mci@example.com', mci=True)
    assert result['signoff_block']
