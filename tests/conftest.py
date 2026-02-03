import os
from pathlib import Path
from dotenv import load_dotenv

# --- Load test environment BEFORE importing db.mongo ---

PROJECT_ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = PROJECT_ROOT / ".env.test"

loaded = load_dotenv(ENV_FILE)

if not loaded:
    raise RuntimeError(f"Failed to load {ENV_FILE}")

if not os.getenv("MONGODB_URI"):
    raise RuntimeError("MONGODB_URI not set after loading .env.test")

import pytest
from db.mongo import (
    users_collection,
    levels_collection,
    game_saves_collection,
    game_results_collection,
)
from db.bootstrap import ensure_indexes, seed_levels_if_missing


@pytest.fixture(scope="session", autouse=True)
def test_environment():
    """
    Ensure test environment is initialized once per test session.
    """
    assert os.getenv("APP_MODE") == "TEST", "Tests must run in APP_MODE=TEST"

    ensure_indexes()
    seed_levels_if_missing()


@pytest.fixture(autouse=True)
def clean_collections():
    """
    Clean mutable collections between tests.
    """
    game_saves_collection.delete_many({})
    game_results_collection.delete_many({})
    users_collection.delete_many({})

    yield

@pytest.fixture(scope="session", autouse=True)
def cleanup_after_session(test_environment):
    """
    Final cleanup after all tests have completed.
    Guaranteed to run AFTER test_environment teardown.
    """
    yield
    users_collection.delete_many({})
    game_saves_collection.delete_many({})
    game_results_collection.delete_many({})
