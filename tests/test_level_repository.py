"""
tests/test_level_repository.py

Author: Jason Fuller
Date: 2/1/26

Integration tests for loading and constructing Level objects from MongoDB.
"""

from db.mongo import levels_collection
from models.repositories.level_repo import MongoLevelRepository

from models.behavior.level_factory import LevelFactory


def test_level_can_be_loaded_and_validated():
    repo = MongoLevelRepository(levels_collection)

    level_def = repo.get("level_1")
    assert level_def is not None

    level = LevelFactory.from_definition(level_def)

    assert level.id == "level_1"
    assert level.start_room == "Space Room"
    assert level.start_room in level.map.rooms
    assert len(level.map.rooms) > 0
