"""
tests/models/domain/test_scoring.py

Author: Jason Fuller

Scoring domain model tests.

Responsibilities:
- Validate StandardScore behavior
- Validate MaxMovesScore penalty logic
- Ensure scoring respects completion state
- Ensure efficiency handling is safe and capped

Architectural role:
- Domain layer test
- Guards scoring invariants
- Protects reward and penalty logic consistency

Design notes:
- Uses lightweight dummy objects (SimpleNamespace)
- Tests observable score outcomes, not internal math
- Ensures no unsafe division or negative behavior
"""

from types import SimpleNamespace

from models.domain.status import GameStatus
from models.domain.scoring import StandardScore, MaxMovesScore


# ==========================================================
# Dummy Scaffolding
# ==========================================================

class DummyScoringPolicy:
    """
    Minimal scoring policy stub for multiplier control.
    """
    def __init__(self, multiplier=1.0):
        self._multiplier = multiplier

    def multiplier(self):
        return self._multiplier


def make_level(required_count=2, optimal_moves=5, multiplier=1.0):
    """
    Create a minimal level-like object for scoring tests.
    """
    return SimpleNamespace(
        id="test_level",
        optimal_moves=optimal_moves,
        rules=SimpleNamespace(
            required_items={"A", "B"} if required_count == 2 else set()
        ),
        difficulty=SimpleNamespace(
            value="easy",
            scoring_policy=DummyScoringPolicy(multiplier),
        ),
    )


def make_state(status, move_count=5, collected=None):
    """
    Create a minimal state-like object for scoring tests.
    """
    return SimpleNamespace(
        status=status,
        move_count=move_count,
        collected_items=set(collected or []),
    )


# ==========================================================
# StandardScore Tests
# ==========================================================

def test_progress_only_score_when_not_completed():
    """
    Non-completed games should not receive win bonus.
    """
    level = make_level()
    state = make_state(GameStatus.GAME_OVER, collected=["A"])

    score = StandardScore().calculate(state, level)

    assert score > 0
    assert score < 1000  # no win bonus


def test_full_win_score():
    """
    Completed game should include win base score.
    """
    level = make_level(multiplier=1.0)
    state = make_state(
        GameStatus.COMPLETED,
        move_count=5,
        collected=["A", "B"],
    )

    score = StandardScore().calculate(state, level)

    assert score >= 1000  # includes WIN_BASE


def test_efficiency_capped_at_one():
    """
    Efficiency should not exceed 1.0 even if moves < optimal.
    """
    level = make_level(optimal_moves=5)
    state = make_state(
        GameStatus.COMPLETED,
        move_count=2,
        collected=["A", "B"],
    )

    score = StandardScore().calculate(state, level)

    assert score > 1000  # capped efficiency


def test_zero_moves_safe_efficiency():
    """
    Zero moves should not cause division errors.
    """
    level = make_level(optimal_moves=5)
    state = make_state(
        GameStatus.COMPLETED,
        move_count=0,
        collected=["A", "B"],
    )

    score = StandardScore().calculate(state, level)

    assert score > 0


# ==========================================================
# MaxMovesScore Tests
# ==========================================================

def test_no_penalty_when_within_optimal():
    """
    MaxMovesScore should equal StandardScore when
    move_count <= optimal_moves.
    """
    level = make_level(optimal_moves=5)
    state = make_state(
        GameStatus.COMPLETED,
        move_count=5,
        collected=["A", "B"],
    )

    base = StandardScore().calculate(state, level)
    penalized = MaxMovesScore().calculate(state, level)

    assert penalized == base


def test_penalty_applied_when_over_optimal():
    """
    MaxMovesScore should penalize when moves exceed optimal.
    """
    level = make_level(optimal_moves=5)
    state = make_state(
        GameStatus.COMPLETED,
        move_count=10,
        collected=["A", "B"],
    )

    base = StandardScore().calculate(state, level)
    penalized = MaxMovesScore().calculate(state, level)

    assert penalized < base


def test_no_penalty_if_not_completed():
    """
    Non-completed games should not receive move penalties.
    """
    level = make_level(optimal_moves=5)
    state = make_state(
        GameStatus.GAME_OVER,
        move_count=10,
        collected=["A"],
    )

    penalized = MaxMovesScore().calculate(state, level)
    base = StandardScore().calculate(state, level)

    assert penalized == base
