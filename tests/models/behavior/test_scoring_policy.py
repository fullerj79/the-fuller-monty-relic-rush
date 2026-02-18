"""
tests/models/behavior/test_scoring_policy.py

Author: Jason Fuller

Scoring policy tests.

Responsibilities:
- Validate difficulty-based scoring behavior
- Ensure multiplier ordering across difficulty levels
- Guard against regression in scoring policy logic

Architectural role:
- Domain behavior test
- Verifies integration between Difficulty enum and its scoring policy
- Ensures difficulty progression impacts scoring consistently

Design notes:
- Multiplier ordering is expected to be monotonic:
    EASY <= MEDIUM <= HARD
- Does not assert exact values to avoid coupling tests
  to specific scoring constants
"""

from models.domain.difficulty import Difficulty


def test_difficulty_scoring_multiplier():
    """
    Ensure scoring multipliers increase with difficulty.

    This protects the invariant that harder levels
    provide equal or greater scoring weight than easier ones.
    """
    easy = Difficulty.EASY
    medium = Difficulty.MEDIUM
    hard = Difficulty.HARD

    assert easy.scoring_policy.multiplier() <= medium.scoring_policy.multiplier()
    assert medium.scoring_policy.multiplier() <= hard.scoring_policy.multiplier()
