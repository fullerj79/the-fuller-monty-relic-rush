"""
tests/models/domain/test_rules.py

Author: Jason Fuller

Rules domain model tests.

Responsibilities:
- Validate StandardRules victory conditions
- Validate defeat conditions
- Ensure non-villain rooms do not alter game state

Architectural role:
- Domain layer test
- Guards core win/lose rule logic
- Protects invariant transitions of GameState.status

Design notes:
- Focuses on observable state transitions
- Does not test controller orchestration
- Ensures rule logic remains deterministic
"""

from models.domain.rules import StandardRules
from models.domain.room import Room
from models.domain.item import Villain
from models.domain.game_state import GameState
from models.domain.player import Player
from models.domain.status import GameStatus


# ==========================================================
# Helpers
# ==========================================================

def make_state(collected=None):
    """
    Create a minimal GameState for rule testing.
    """
    return GameState(
        level_id="level_test",
        player=Player("A"),
        collected_items=set(collected or []),
        move_count=0,
        status=GameStatus.IN_PROGRESS,
        message="",
        event_log=[],
    )


# ==========================================================
# Victory / Defeat Logic
# ==========================================================

def test_encounter_villain_with_all_items_wins():
    """
    If all required items are collected,
    encountering villain should complete the game.
    """
    rules = StandardRules(required_items={"relic1", "relic2"})
    villain_room = Room("BossRoom", item=Villain("Boss"), exits={})

    state = make_state(collected={"relic1", "relic2"})
    rules.check(state, villain_room)

    assert state.status == GameStatus.COMPLETED


def test_encounter_villain_without_all_items_loses():
    """
    Missing required items should result in GAME_OVER.
    """
    rules = StandardRules(required_items={"relic1", "relic2"})
    villain_room = Room("BossRoom", item=Villain("Boss"), exits={})

    state = make_state(collected={"relic1"})
    rules.check(state, villain_room)

    assert state.status == GameStatus.GAME_OVER


def test_non_villain_room_no_status_change():
    """
    Entering a non-villain room should not change status.
    """
    rules = StandardRules(required_items={"relic1"})
    normal_room = Room("SafeRoom", item=None, exits={})

    state = make_state()
    rules.check(state, normal_room)

    assert state.status == GameStatus.IN_PROGRESS
