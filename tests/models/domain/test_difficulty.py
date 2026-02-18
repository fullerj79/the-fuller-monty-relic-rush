"""
tests/models/domain/test_difficulty.py

Author: Jason Fuller

Difficulty domain model tests.

Responsibilities:
- Validate Difficulty enum behavior
- Ensure invalid difficulty values raise errors
- Verify required strategy/policy attachments
- Ensure scoring multipliers scale correctly

Architectural role:
- Domain layer test
- Guards enum integrity and policy wiring
- Ensures difficulty configuration remains consistent

Design notes:
- Tests focus on behavior, not implementation details
- Protects strategy composition invariants
- Ensures monotonic difficulty scaling behavior
"""

import pytest

from models.domain.difficulty import Difficulty


# ==========================================================
# Enum Value Validation
# ==========================================================

def test_difficulty_enum_values():
    """
    Enum should resolve valid difficulty strings
    and preserve identity.
    """
    assert Difficulty("easy") is Difficulty.EASY
    assert Difficulty("medium") is Difficulty.MEDIUM
    assert Difficulty("hard") is Difficulty.HARD

    assert Difficulty.EASY.value == "easy"
    assert Difficulty.MEDIUM.value == "medium"
    assert Difficulty.HARD.value == "hard"


def test_invalid_difficulty_raises():
    """Invalid difficulty string should raise ValueError."""
    with pytest.raises(ValueError):
        Difficulty("impossible")


# ==========================================================
# Strategy / Policy Wiring
# ==========================================================

def test_difficulty_has_scoring_strategy():
    """Each difficulty must attach a scoring strategy."""
    for difficulty in Difficulty:
        assert difficulty.scoring_strategy is not None


def test_difficulty_has_visibility_policy():
    """Each difficulty must attach a visibility policy."""
    for difficulty in Difficulty:
        assert difficulty.visibility_policy is not None


def test_difficulty_has_scoring_policy():
    """Each difficulty must attach a scoring policy."""
    for difficulty in Difficulty:
        assert difficulty.scoring_policy is not None


# ==========================================================
# Scoring Behavior
# ==========================================================

def test_scoring_policy_multiplier_monotonic():
    """
    Scoring multiplier must scale monotonically
    with increasing difficulty.
    """
    easy = Difficulty.EASY.scoring_policy.multiplier()
    medium = Difficulty.MEDIUM.scoring_policy.multiplier()
    hard = Difficulty.HARD.scoring_policy.multiplier()

    assert easy <= medium <= hard
