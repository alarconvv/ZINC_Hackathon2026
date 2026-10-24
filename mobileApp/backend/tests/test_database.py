import pytest
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session
from backend import deps
from backend.deps import UserState

def test_foreign_keys_are_enforced_and_sql_parameters_are_hidden(client):
    with Session(deps.engine) as db:
        assert db.exec(text('PRAGMA foreign_keys')).scalar() == 1
        db.add(UserState(user_id='nonexistent',data='sensitive-health-fixture'))
        with pytest.raises(IntegrityError) as exc:
            db.commit()
        assert 'sensitive-health-fixture' not in str(exc.value)
        db.rollback()

def test_hosted_postgres_urls_use_the_installed_driver():
    assert deps.database_url('postgres://host/db') == 'postgresql+psycopg://host/db'
    assert deps.database_url('postgresql://host/db') == 'postgresql+psycopg://host/db'
    assert deps.database_url('sqlite:///local.db') == 'sqlite:///local.db'
