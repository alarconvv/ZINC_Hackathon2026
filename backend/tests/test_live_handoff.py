from copy import deepcopy
import httpx
import pytest
from backend.verify_live import verify_api, LiveCheckError, main

class FakeAPI:
    def __init__(self, event='coach_success', changed=False):
        self.state = {'plan': {'version': 1}, 'next_plan': None, 'stopped': False, 'events': []}
        self.event, self.changed = event, changed
        self.paths = []
    def post(self, path, **kwargs):
        self.paths.append(path)
        if path == '/auth/login':
            return httpx.Response(200, json={'access_token': 'fixture-only'})
        after = deepcopy(self.state)
        after['events'].append({'event': self.event})
        if self.changed:
            after['plan']['version'] = 2
        return httpx.Response(200, json={'state': after, 'reply': 'Keep following your displayed plan.', 'pending_change': None})
    def get(self, path, **kwargs):
        return httpx.Response(200, json={'state': self.state, 'version': 0, 'consented': True})

def test_live_handoff_requires_provider_success_and_never_accepts():
    api = FakeAPI()
    assert verify_api(api, 'fixture@example.com', 'not-a-real-password')['status'] == 'PASS'
    assert api.paths == ['/auth/login', '/coach']
    for api in (FakeAPI('fallback'), FakeAPI(changed=True)):
        with pytest.raises(LiveCheckError):
            verify_api(api, 'fixture@example.com', 'not-a-real-password')

def test_live_handoff_blocks_missing_configuration_without_network(monkeypatch,capsys):
    for key in ('ZINC_API_URL','DEMO_EMAIL','DEMO_PASSWORD'):
        monkeypatch.delenv(key,raising=False)
    assert main() == 2
    assert 'BLOCKED' in capsys.readouterr().out
