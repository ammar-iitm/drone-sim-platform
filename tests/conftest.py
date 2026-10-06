import copy
from pathlib import Path

import pytest

from app import create_app
from app.scoring import load_rubric

ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture
def rubric():
    return copy.deepcopy(load_rubric(ROOT / "rubric.json"))


@pytest.fixture
def app(tmp_path):
    return create_app({"DATABASE": str(tmp_path / "test.db"), "TESTING": True})


@pytest.fixture
def client(app):
    return app.test_client()
