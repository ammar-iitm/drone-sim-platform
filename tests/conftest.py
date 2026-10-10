import copy
import os
from pathlib import Path

import pytest

from app import create_app
from app.scoring import load_rubric

ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture
def rubric():
    return copy.deepcopy(load_rubric(ROOT / "rubric.json"))


# Set TEST_DATABASE_URL to a throwaway Postgres database to run the same tests on Postgres.
# Its tables are dropped before every test.
PG_URL = os.environ.get("TEST_DATABASE_URL")


@pytest.fixture
def app(tmp_path):
    if PG_URL:
        import psycopg
        with psycopg.connect(PG_URL, autocommit=True) as conn:
            conn.execute("DROP TABLE IF EXISTS events, sessions, trainees CASCADE")
        return create_app({"DATABASE_URL": PG_URL, "TESTING": True})
    return create_app({"DATABASE": str(tmp_path / "test.db"), "TESTING": True})


@pytest.fixture
def client(app):
    return app.test_client()
