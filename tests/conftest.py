import pytest
import tempfile

from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    """
    Shared FastAPI test client
    """

    with TestClient(app) as c:
        yield c

@pytest.fixture
def sample_resume_text():

    return """
    Riley Thompson

    Skills:
    Python
    SQL
    AWS
    Docker
    React
    """

import tempfile


@pytest.fixture
def temp_resume_file():

    content = b"Python AWS SQL"

    with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as f:

        f.write(content)

        yield f.name

import os


@pytest.fixture(autouse=True)
def cleanup_test_db():

    test_db = "test_jobs.db"

    if os.path.exists(test_db):
        os.remove(test_db)

    yield

    if os.path.exists(test_db):
        os.remove(test_db)

@pytest.fixture
def mock_jobs():

    return [
        {
            "id": 1,
            "title": "TEST",
            "company": "TEST",
            "location": "TEST",
            "score": 0.95,
            "show": 1
        }
    ]