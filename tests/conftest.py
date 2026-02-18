"""
tests/conftest.py

Author: Jason Fuller

Global pytest configuration and fixtures.

Design goals:
- Strict TEST environment enforcement
- Deterministic Mongo isolation
- Clean repository + controller injection
- Explicit isolation fixtures for branch-heavy tests
"""

# ============================================================
# Standard library
# ============================================================

import os
from pathlib import Path

# ============================================================
# Third-party
# ============================================================

import pytest
from dotenv import load_dotenv

# ============================================================
# Load TEST environment BEFORE any DB imports
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = PROJECT_ROOT / ".env.test"


def _load_test_env() -> None:
    if not load_dotenv(ENV_FILE):
        raise RuntimeError(f"Failed to load {ENV_FILE}")

    if not os.getenv("MONGODB_URI"):
        raise RuntimeError("MONGODB_URI not set in test environment")

    if os.getenv("APP_MODE") != "TEST":
        raise RuntimeError("Tests must run with APP_MODE=TEST")


_load_test_env()

# ============================================================
# DB + bootstrap
# ============================================================

from db.mongo import (
    users_collection,
    levels_collection,
    game_saves_collection,
    game_results_collection,
)

from db.bootstrap import ensure_indexes, seed_levels_if_missing

# ============================================================
# Repositories
# ============================================================

from models.repositories.user_repo import MongoUserRepository
from models.repositories.level_repo import MongoLevelRepository
from models.repositories.save_repo import MongoSaveRepository
from models.repositories.history_repo import MongoHistoryRepository

# ============================================================
# Controllers
# ============================================================

from controllers.user import UserController
from controllers.game import GameController

# ============================================================
# Session bootstrap
# ============================================================

@pytest.fixture(scope="session", autouse=True)
def test_environment():
    """
    Ensure DB indexes and seed levels exist once per session.
    """
    ensure_indexes()
    seed_levels_if_missing()
    yield


# ============================================================
# Clean mutable collections per test
# ============================================================

@pytest.fixture(autouse=True)
def clean_mutable_collections():
    """
    Reset mutable collections before and after each test.

    Levels are NOT cleared here because they are static seed data.
    """
    users_collection.delete_many({})
    game_saves_collection.delete_many({})
    game_results_collection.delete_many({})

    yield

    users_collection.delete_many({})
    game_saves_collection.delete_many({})
    game_results_collection.delete_many({})


# ============================================================
# Repository fixtures
# ============================================================

@pytest.fixture
def user_repo():
    return MongoUserRepository(users_collection)


@pytest.fixture
def level_repo():
    return MongoLevelRepository(levels_collection)


@pytest.fixture
def save_repo():
    return MongoSaveRepository(game_saves_collection)


@pytest.fixture
def history_repo():
    return MongoHistoryRepository(game_results_collection)


# ============================================================
# Controller fixtures
# ============================================================

@pytest.fixture
def user_controller(user_repo):
    return UserController(user_repo)


@pytest.fixture
def game_controller(level_repo, save_repo, history_repo):
    return GameController(
        level_repo=level_repo,
        save_repo=save_repo,
        history_repo=history_repo,
    )


# ============================================================
# Isolated collection fixtures
# ============================================================

@pytest.fixture
def isolated_level_collection():
    """
    Fully isolates level collection for cache / branch testing.
    """
    levels_collection.delete_many({})
    yield levels_collection
    levels_collection.delete_many({})
    seed_levels_if_missing()  # restore baseline seed


@pytest.fixture
def isolated_history_collection():
    game_results_collection.delete_many({})
    yield game_results_collection
    game_results_collection.delete_many({})


@pytest.fixture
def isolated_save_collection():
    game_saves_collection.delete_many({})
    yield game_saves_collection
    game_saves_collection.delete_many({})


# ============================================================
# Sample data fixtures
# ============================================================

@pytest.fixture
def sample_level_definition():
    """
    Minimal valid level definition compatible with LevelFactory.
    """
    return {
        "id": "test_level",
        "name": "Test Level",
        "difficulty": "easy",
        "start_room": "A",
        "rooms": {
            "A": {"exits": {"east": "B"}},
            "B": {
                "exits": {"west": "A"},
                "item": {"type": "villain", "name": "Test Villain"},
            },
        },
        "coords": {
            "A": [0, 0],
            "B": [1, 0],
        },
        "rules": {
            "required_items": [],
        },
    }


# ============================================================
# Sample GameState fixture
# ============================================================

from models.domain.game_state import GameState
from models.domain.player import Player
from models.domain.status import GameStatus


@pytest.fixture
def sample_state():
    """
    Minimal valid GameState for repository tests.
    """
    return GameState(
        level_id="test_level",
        player=Player(location="A"),
        visited_rooms={"A"},
        collected_items=set(),
        move_count=0,
        status=GameStatus.IN_PROGRESS,
        message=None,
    )
