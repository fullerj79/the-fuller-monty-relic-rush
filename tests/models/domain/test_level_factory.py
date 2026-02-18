"""
tests/models/behavior/test_level_factory.py

Author: Jason Fuller

LevelFactory and UI projection tests.

Responsibilities:
- Validate LevelFactory construction from definitions
- Ensure UI projection produces correct structural output
- Verify invalid level definitions are rejected

Architectural role:
- Behavior layer test
- Guards level construction integrity
- Protects projection contract used by UI layer

Design notes:
- Tests focus on behavior and contract guarantees
- Avoids testing internal implementation details
- Ensures projection structure remains stable for consumers
"""

import pytest

from levels.seed_levels import LEVELS
from models.behavior.level_factory import LevelFactory
from models.domain.game_state import GameState


# ==========================================================
# UI Projection Contract
# ==========================================================

def test_level_ui_projection_returns_structure():
    """
    UI projection must return a structured dictionary
    containing room data for rendering.
    """
    definition = LEVELS[0]

    level = LevelFactory.from_definition(definition)

    state = GameState.start(
        level_id=level.id,
        start_room=level.start_room,
    )

    projection = level.ui_projection(state)

    assert isinstance(projection, dict)
    assert "rooms" in projection
    assert isinstance(projection["rooms"], dict)

    # Player location must exist in projection
    assert state.player.location in projection["rooms"]


# ==========================================================
# Factory Validation Behavior
# ==========================================================

def test_level_factory_rejects_unknown_item_type():
    """
    Factory must reject unknown item types
    to preserve domain integrity.
    """
    bad_def = {
        "id": "bad",
        "name": "Bad Level",
        "difficulty": "easy",
        "start_room": "A",
        "rooms": {
            "A": {
                "exits": {"east": "B"},
                "item": {"type": "unknown", "name": "X"},
            },
            "B": {
                "exits": {},
                "item": {"type": "villain", "name": "Boss"},
            },
        },
        "coords": {
            "A": (0, 0),
            "B": (1, 0),
        },
        "rules": {"required_items": []},
    }

    with pytest.raises(ValueError):
        LevelFactory.from_definition(bad_def)
