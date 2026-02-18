"""
tests/models/domain/test_item.py

Author: Jason Fuller

Item domain model tests.

Responsibilities:
- Validate base Item behavior
- Verify Relic interaction logic
- Verify Villain interaction logic
- Ensure GameState mutation occurs correctly

Architectural role:
- Domain layer test
- Guards item behavior invariants
- Ensures item interactions mutate GameState safely

Design notes:
- Focused on domain behavior only
- No controller or repository involvement
- Protects item-to-state interaction contracts
"""

from models.domain.item import Item, Relic, Villain
from models.domain.game_state import GameState
from models.domain.player import Player
from models.domain.status import GameStatus


# ==========================================================
# Helpers
# ==========================================================

def make_state():
    """Create a minimal valid GameState for item interaction tests."""
    return GameState(
        level_id="test_level",
        player=Player("A"),
        collected_items=set(),
        move_count=0,
        status=GameStatus.IN_PROGRESS,
        message=None,
        event_log=[],
    )


# ==========================================================
# Base Item Tests
# ==========================================================

def test_item_creation():
    """Item should initialize with name and render key."""
    item = Item(name="Relic", render_key="relic")

    assert item.name == "Relic"
    assert item.render_key == "relic"


def test_item_string_behavior():
    """Item fields should be string types."""
    item = Item(name="Relic", render_key="relic")

    assert isinstance(item.name, str)
    assert isinstance(item.render_key, str)


# ==========================================================
# Relic Behavior Tests
# ==========================================================

def test_relic_on_enter_collects_item():
    """
    Relic should:
    - Add itself to collected_items
    - Append collection message to event_log
    """
    state = make_state()
    relic = Relic("Relic1")

    relic.on_enter(state)

    assert "Relic1" in state.collected_items
    assert "Collected Relic1" in state.event_log[-1]


def test_relic_on_enter_not_duplicate():
    """
    Relic should not duplicate collection
    if entered multiple times.
    """
    state = make_state()
    relic = Relic("Relic1")

    relic.on_enter(state)
    relic.on_enter(state)

    assert list(state.collected_items).count("Relic1") == 1


# ==========================================================
# Villain Behavior Tests
# ==========================================================

def test_villain_on_enter_sets_flag():
    """
    Villain should set encountered_villain flag on state.
    """
    state = make_state()
    villain = Villain("Boss")

    villain.on_enter(state)

    assert state.encountered_villain is True
