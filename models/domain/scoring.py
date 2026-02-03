"""
Scoring strategies and difficulty modifiers.

Author: Jason Fuller
Date: 2/1/26

This module defines the scoring layer responsible for translating a
completed or failed GameState into a numeric score. Scores are designed
to be deterministic, comparable, and replayable across sessions.

Architectural role:
- Domain logic (evaluation and ranking)
- Consumes GameState and Level metadata
- Produces persistent, leaderboard-ready results

Scoring logic is intentionally isolated from controllers, rules, and UI
to allow rebalancing and historical re-scoring without altering gameplay.
"""

from abc import ABC, abstractmethod
from models.domain.status import GameStatus


class ScoreStrategy(ABC):
    """
    Abstract base class for scoring strategies.

    Design intent:
    - Encapsulate scoring logic independently of gameplay rules
    - Allow multiple scoring models to coexist (e.g., standard, hardcore)
    - Enable retroactive rescoring of historical runs

    Subclasses must implement a deterministic calculation that depends
    only on the provided GameState and Level configuration.
    """

    @abstractmethod
    def calculate(self, state, level) -> int:
        """
        Calculate a score for the given game state and level.

        Parameters:
        - state: final GameState for the session
        - level: Level configuration used for the session

        Returns:
        - Integer score suitable for persistence and comparison

        Notes:
        - This method must be pure (no side effects).
        - Repeated calls with identical inputs must yield identical results.
        """
        pass


class StandardScore(ScoreStrategy):
    """
    Standard scoring implementation.

    Scoring model:
    - Winning always scores higher than losing.
    - Partial progress is rewarded even on failure.
    - Efficiency is measured relative to the level's optimal move count.
    - Difficulty scales efficiency, not correctness.

    This strategy balances fairness, player feedback, and leaderboard
    stability while remaining explainable to players.
    """

    WIN_BASE = 1000
    MAX_PROGRESS_SCORE = 500
    MAX_EFFICIENCY_SCORE = 1000

    DIFFICULTY_MULTIPLIER = {
        "easy": 0.75,
        "medium": 1.0,
        "hard": 1.25,
    }

    def calculate(self, state, level) -> int:
        collected = len(state.collected_items)
        total_required = len(level.rules.required_items)

        progress = collected / total_required if total_required else 0.0
        progress_score = int(self.MAX_PROGRESS_SCORE * progress)

        if state.status != GameStatus.COMPLETED:
            return progress_score

        efficiency = min(level.optimal_moves / state.move_count, 1.0)
        efficiency_score = int(self.MAX_EFFICIENCY_SCORE * efficiency)

        multiplier = self.DIFFICULTY_MULTIPLIER[level.difficulty]

        return int(
            self.WIN_BASE
            + progress_score
            + efficiency_score * multiplier
        )


class MaxMovesScore(StandardScore):
    """
    Scoring strategy with a maximum-move penalty.

    Design intent:
    - Penalize inefficient play without altering win/loss rules
    - Preserve determinism and leaderboard comparability
    - Allow difficulty- or mode-specific tuning

    This strategy extends StandardScore rather than replacing it,
    ensuring consistency with baseline scoring expectations.
    """

    # Hard cap after which efficiency is heavily penalized
    OVERAGE_PENALTY_FACTOR = 0.5

    def calculate(self, state, level) -> int:
        """
        Compute the final score with an efficiency penalty when
        move count exceeds the level's optimal solution.

        Algorithm overview:
        1. Compute the base score using StandardScore logic
        2. If the game was not completed, return base score
        3. If completed and move_count exceeds optimal_moves:
           - Apply a penalty proportional to overage

        Notes:
        - This strategy does NOT enforce a move limit
        - It only affects scoring, not gameplay outcomes
        """
        base_score = super().calculate(state, level)

        if state.status != GameStatus.COMPLETED:
            return base_score

        if level.optimal_moves is None:
            return base_score

        if state.move_count <= level.optimal_moves:
            return base_score

        overage = state.move_count - level.optimal_moves
        penalty_ratio = min(overage / level.optimal_moves, 1.0)

        penalty = int(base_score * penalty_ratio * self.OVERAGE_PENALTY_FACTOR)

        return max(base_score - penalty, 0)
