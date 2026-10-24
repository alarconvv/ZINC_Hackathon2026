from conftest import register

def test_consent_needs_auth_and_true(client):
    assert client.post('/consent', json={'collect_health_data': True, 'version': '2026-10-beta'}).status_code == 401
    headers = register(client)
    assert client.post('/consent', headers=headers, json={'collect_health_data': False, 'version': '2026-10-beta'}).status_code == 422
    result = client.post('/consent', headers=headers, json={'collect_health_data': True, 'version': '2026-10-beta'})
    assert result.status_code == 200
    assert result.json()['timestamp']
