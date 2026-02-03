"""
tests/test_level_solvability.py

Author: Jason Fuller
Date: 2/1/26

Tests that ensure levels are solvable via BFS validation.
"""

from db.mongo import levels_collection
from models.repositories.level_repo import MongoLevelRepository

from models.behavior.level_factory import LevelFactory


def test_level_is_solvable():
    repo = MongoLevelRepository(levels_collection)
    level_def = repo.get("level_1")

    # If this does not raise, the level is solvable
    level = LevelFactory.from_definition(level_def)

    assert level.optimal_moves > 0
