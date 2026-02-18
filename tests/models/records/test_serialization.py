"""
tests/models/records/test_serialization.py

Author: Jason Fuller

GameState serialization tests.

Responsibilities:
- Validate GameState → dict conversion
- Validate dict → GameState reconstruction
- Ensure enum and set handling are preserved
- Guard persistence boundary integrity

Architectural role:
- Records / serialization layer test
- Protects domain ↔ storage contract
- Ensures safe round-trip persistence behavior

Design notes:
- Focuses on behavior, not implementation
- Guards enum and collection restoration
- Ensures no data loss during round-trip
"""

from models.domain.game_state import GameState
from models.domain.player import Player
from models.domain.status import GameStatus
from models.records.serialization import (
    gamestate_to_dict,
    gamestate_from_dict,
)


# ==========================================================
# Round-Trip Integrity
# ==========================================================

def test_game_state_serialization_roundtrip():
    """
    GameState should serialize to a dictionary and
    reconstruct back to an equivalent domain object.
    """
    state = GameState(
        level_id="level_test",
        player=Player("A"),
        move_count=5,
        collected_items={"Relic"},
        status=GameStatus.IN_PROGRESS,
        message="Started",
        event_log=["Started"],
    )

    data = gamestate_to_dict(state)
    restored = gamestate_from_dict(data)

    assert restored.level_id == "level_test"
    assert restored.player.location == "A"
    assert restored.move_count == 5
    assert restored.collected_items == {"Relic"}
    assert restored.status == GameStatus.IN_PROGRESS
