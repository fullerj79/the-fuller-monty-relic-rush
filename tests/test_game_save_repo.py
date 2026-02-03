"""
tests/test_game_save_repo.py

Author: Jason Fuller
Date: 2/1/26

Integration tests for saving and loading in-progress game state.
"""

from models.records.game_save import GameSave
from models.domain.game_state import GameState

from db.mongo import game_saves_collection
from models.repositories.save_repo import MongoSaveRepository


def test_game_save_round_trip():
    repo = MongoSaveRepository(game_saves_collection)

    # Create a valid game state using the domain constructor
    state = GameState.start(
        start_room="Space Room",
    )

    save = GameSave(
        user_email="test@example.com",
        level_id="level_1",
        state=state,
    )

    repo.upsert_active(save)

    loaded = repo.get_active("test@example.com")

    assert loaded is not None
    assert loaded.state.player.location == "Space Room"
    assert loaded.state.move_count == 0
