from conftest import register

def test_register_login_and_limits(client):
    register(client)
    body = {'email': 'maria@example.com', 'password': 'a-long-test-password'}
    assert client.post('/auth/login', json=body).status_code == 200
    wrong = client.post('/auth/login', json={**body, 'password': 'wrong'})
    unknown = client.post('/auth/login', json={**body, 'email': 'unknown@example.com'})
    assert wrong.status_code == unknown.status_code == 401
    assert wrong.json() == unknown.json()
    for _ in range(3):
        client.post('/auth/login', json=body)
    assert client.post('/auth/login', json=body).status_code == 429
    assert client.post('/auth/register', json={**body, 'password': 'short', 'name': 'M'}).status_code == 422
