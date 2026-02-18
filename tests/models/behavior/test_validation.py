"""
tests/models/behavior/test_validation.py

Author: Jason Fuller

Level validation and path computation tests.

Responsibilities:
- Validate structural correctness of level definitions
- Ensure invalid level configurations raise LevelValidationError
- Verify optimal move computation logic
- Ensure unsolvable maps are rejected

Architectural role:
- Domain behavior test
- Validates integrity constraints at the validation boundary
- Guards correctness of graph traversal and rules enforcement

Design notes:
- Structural validation tests operate on raw level definitions (dicts)
- Optimal move tests use lightweight dummy graph objects
- Tests focus on behavioral guarantees, not implementation details
"""

import pytest

from models.behavior.validation import (
    validate_level_definition,
    compute_optimal_moves,
    LevelValidationError,
)


# ==========================================================
# Fixtures for Structural Validation
# ==========================================================

def valid_level_def():
    """
    Minimal valid level definition.

    A -> B (villain)
    """
    return {
        "id": "level_test",
        "name": "Test Level",
        "difficulty": "easy",
        "start_room": "A",
        "rooms": {
            "A": {"exits": {"east": "B"}, "item": None},
            "B": {
                "exits": {"west": "A"},
                "item": {"type": "villain"},
            },
        },
        "coords": {
            "A": (0, 0),
            "B": (1, 0),
        },
        "rules": {},
    }


# ==========================================================
# validate_level_definition Tests
# ==========================================================

def test_validate_level_definition_success():
    """Valid level definition should not raise."""
    validate_level_definition(valid_level_def())


def test_validate_level_missing_key():
    """Missing required top-level keys should raise."""
    level = valid_level_def()
    del level["name"]

    with pytest.raises(LevelValidationError):
        validate_level_definition(level)


def test_validate_invalid_start_room():
    """Start room must exist in rooms definition."""
    level = valid_level_def()
    level["start_room"] = "Z"

    with pytest.raises(LevelValidationError):
        validate_level_definition(level)


def test_validate_invalid_exit_target():
    """Exit targets must reference valid rooms."""
    level = valid_level_def()
    level["rooms"]["A"]["exits"]["north"] = "Z"

    with pytest.raises(LevelValidationError):
        validate_level_definition(level)


def test_validate_missing_coordinates():
    """All rooms must have coordinate entries."""
    level = valid_level_def()
    del level["coords"]["A"]

    with pytest.raises(LevelValidationError):
        validate_level_definition(level)


def test_validate_multiple_villains():
    """Only one villain is allowed per level."""
    level = valid_level_def()
    level["rooms"]["A"]["item"] = {"type": "villain"}

    with pytest.raises(LevelValidationError):
        validate_level_definition(level)


# ==========================================================
# compute_optimal_moves Tests
# ==========================================================

class DummyItem:
    """Minimal item representation for path tests."""

    def __init__(self, name=None, render_key=None):
        self.name = name
        self.render_key = render_key


class DummyRoom:
    """Minimal room representation for path tests."""

    def __init__(self, item=None):
        self.item = item


class DummyMap:
    """
    Minimal graph structure compatible with compute_optimal_moves.
    """

    def __init__(self):
        self.rooms = {}
        self._neighbors = {}

    def neighbors(self, room):
        return self._neighbors.get(room, {})


def test_compute_optimal_moves_simple_path():
    """
    A -> B (villain)
    No required items.
    Expected optimal moves: 1
    """
    m = DummyMap()
    m.rooms = {
        "A": DummyRoom(),
        "B": DummyRoom(DummyItem(render_key="villain")),
    }
    m._neighbors = {
        "A": {"east": "B"},
        "B": {},
    }

    moves = compute_optimal_moves(m, "A", set())
    assert moves == 1


def test_compute_optimal_moves_with_required_item():
    """
    A (contains required item) -> B (villain)
    Required item collected before moving.
    Expected optimal moves: 1
    """
    m = DummyMap()
    m.rooms = {
        "A": DummyRoom(DummyItem(name="Relic1")),
        "B": DummyRoom(DummyItem(render_key="villain")),
    }
    m._neighbors = {
        "A": {"east": "B"},
        "B": {},
    }

    moves = compute_optimal_moves(m, "A", {"Relic1"})
    assert moves == 1


def test_compute_optimal_moves_unsolvable():
    """
    Villain unreachable from start.
    Should raise LevelValidationError.
    """
    m = DummyMap()
    m.rooms = {
        "A": DummyRoom(),
        "B": DummyRoom(DummyItem(render_key="villain")),
    }
    m._neighbors = {
        "A": {},  # No path to villain
        "B": {},
    }

    with pytest.raises(LevelValidationError):
        compute_optimal_moves(m, "A", set())
