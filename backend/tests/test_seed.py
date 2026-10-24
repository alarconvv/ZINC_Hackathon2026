from sqlmodel import Session
from backend import deps
from backend.seed_demo import seed, demo_state
from backend.zinc_core import progress_board

def test_demo_is_populated_by_real_engine_calls_and_seed_is_idempotent(client):
    s = demo_state()
    board = progress_board.summarize(s['plan'], s['activity_sessions'])
    assert s['profile']['age'] == 52 and s['plan']['tier'] == 'Protect'
    assert board['percent'] == 75
    assert len(s['logs']['sessions']) == 14
    assert s['next_plan']['exercises'][0]['reps'] == 11
    with Session(deps.engine) as db:
        assert seed(db, 'fixture-password-not-production')
        assert not seed(db, 'another-fixture-password')
