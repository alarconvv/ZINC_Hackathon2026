"""Human-run HTTPS coach check. Never accepts a proposal or prints credentials."""
import json, os
from urllib.parse import urlparse
import httpx

class LiveCheckError(ValueError):
    pass

def checked(response):
    if response.status_code != 200:
        raise LiveCheckError('The API request did not succeed.')
    return response.json()

def verify_api(client, email, password):
    login = checked(client.post('/auth/login', json={'email': email, 'password': password}))
    headers = {'Authorization': 'Bearer ' + login['access_token']}
    before = checked(client.get('/me', headers=headers))
    state = before['state']
    if not before.get('consented') or not state.get('plan') or state.get('stopped'):
        raise LiveCheckError('Use a consented, screened fictional account with an unstopped plan.')
    after = checked(client.post('/coach', headers={**headers, 'If-Match': str(before['version'])},
        json={'message': 'Explain the activities in my saved weekly plan without proposing changes.'}))
    events = after['state']['events'][len(state['events']):]
    if (not isinstance(after.get('reply'), str) or not after['reply'].strip()
            or not any(e['event'] == 'coach_success' for e in events)
            or any(e['event'] == 'fallback' for e in events)):
        raise LiveCheckError('The provider did not produce a verified live reply.')
    if after['state']['plan'] != state['plan'] or after['state'].get('next_plan') != state.get('next_plan'):
        raise LiveCheckError('The explanatory request changed a saved prescription.')
    return {'status': 'PASS', 'stage': 'live_coach', 'plan_unchanged': True, 'proposal_pending': bool(after.get('pending_change'))}

def main():
    base, email, password = (os.getenv(k, '') for k in ('ZINC_API_URL', 'DEMO_EMAIL', 'DEMO_PASSWORD'))
    url = urlparse(base)
    secure = url.scheme == 'https' or url.scheme == 'http' and url.hostname in ('localhost', '127.0.0.1', '::1')
    if not base or not email or not password or not secure or url.username or url.password:
        print(json.dumps({'status': 'BLOCKED', 'stage': 'configuration', 'reason': 'Set an HTTPS API origin and fictional account environment variables.'}))
        return 2
    try:
        with httpx.Client(base_url=base.rstrip('/'), timeout=40) as client:
            result = verify_api(client, email, password)
    except (httpx.HTTPError, ValueError, KeyError, TypeError):
        print(json.dumps({'status': 'FAIL', 'stage': 'live_coach', 'reason': 'Check server configuration and the fictional account; no proposal was accepted.'}))
        return 1
    print(json.dumps(result))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
