"""
models/domain/scoring.py

Author: Jason Fuller

Scoring strategies.

Responsibilities:
- Define deterministic scoring algorithms
- Calculate final scores from GameState and Level
- Delegate difficulty scaling to ScoringPolicy

Architectural role:
- Domain logic (scoring algorithms)
- Invoked by the GameController during finalization
- Independent of UI and persistence

Logging:
- DEBUG: score breakdown and intermediate calculations
- INFO: final score computation and applied penalties
"""

# ------------------------------------------------------------------
# Standard library imports
# ------------------------------------------------------------------
from abc import ABC, abstractmethod

# ------------------------------------------------------------------
# Domain imports
# ------------------------------------------------------------------
from models.domain.status import GameStatus

# ------------------------------------------------------------------
# Local application imports
# ------------------------------------------------------------------
from utils.logger import get_logger


logger = get_logger(__name__)


class ScoreStrategy(ABC):
    """
    Abstract base class for scoring strategies.

    A ScoreStrategy defines how a final score is calculated.
    Difficulty scaling is applied via ScoringPolicy.
    """

    @abstractmethod
    def calculate(self, state, level) -> int:
        """
        Calculate a deterministic score for a completed or failed run.
        """
        raise NotImplementedError


class StandardScore(ScoreStrategy):
    """
    Standard scoring implementation.

    Scoring model:
    - Progress is always rewarded
    - Winning unlocks efficiency scoring
    - Difficulty scales efficiency, not correctness
    """

    WIN_BASE = 1000
    MAX_PROGRESS_SCORE = 500
    MAX_EFFICIENCY_SCORE = 1000

    def calculate(self, state, level) -> int:
        logger.info(
            "Calculating score",
            level_id=level.id,
            difficulty=level.difficulty.value,
            status=state.status,
            move_count=state.move_count,
            optimal_moves=level.optimal_moves,
        )

        # ------------------------------------------------------------
        # Progress score
        # ------------------------------------------------------------

        collected = len(state.collected_items)
        total_required = len(level.rules.required_items)

        progress = collected / total_required if total_required else 0.0
        progress_score = int(self.MAX_PROGRESS_SCORE * progress)

        logger.debug(
            "Progress score computed",
            collected=collected,
            required=total_required,
            progress=progress,
            progress_score=progress_score,
        )

        if state.status != GameStatus.COMPLETED:
            logger.info(
                "Game not completed; returning progress-only score",
                score=progress_score,
            )
            return progress_score

        # ------------------------------------------------------------
        # Efficiency score
        # ------------------------------------------------------------

        if not level.optimal_moves or state.move_count <= 0:
            efficiency = 1.0
        else:
            efficiency = min(level.optimal_moves / state.move_count, 1.0)

        efficiency_score = int(self.MAX_EFFICIENCY_SCORE * efficiency)

        logger.debug(
            "Efficiency score computed",
            efficiency=efficiency,
            efficiency_score=efficiency_score,
        )

        # ------------------------------------------------------------
        # Difficulty > ScoringPolicy
        # ------------------------------------------------------------

        scoring_policy = level.difficulty.scoring_policy
        multiplier = scoring_policy.multiplier()

        logger.info(
            "Applying scoring policy",
            difficulty=level.difficulty.value,
            policy=scoring_policy.__class__.__name__,
            multiplier=multiplier,
        )

        # ------------------------------------------------------------
        # Score breakdown
        # ------------------------------------------------------------

        logger.debug(
            "Score breakdown",
            win_base=self.WIN_BASE,
            progress_score=progress_score,
            efficiency_score=efficiency_score,
            multiplier=multiplier,
        )

        final_score = int(
            self.WIN_BASE
            + progress_score
            + efficiency_score * multiplier
        )

        logger.info(
            "Final score computed",
            score=final_score,
        )

        return final_score


class MaxMovesScore(StandardScore):
    """
    Scoring strategy with a maximum-move penalty.

    Penalizes inefficient play without enforcing a hard move limit.
    """

    OVERAGE_PENALTY_FACTOR = 0.5

    def calculate(self, state, level) -> int:
        base_score = super().calculate(state, level)

        if state.status != GameStatus.COMPLETED:
            logger.debug("Skipping max-move penalty (game not completed)")
            return base_score

        if not level.optimal_moves:
            logger.warn(
                "Skipping max-move penalty (optimal_moves undefined)",
            )
            return base_score

        if state.move_count <= level.optimal_moves:
            logger.debug("No move overage; no penalty applied")
            return base_score

        overage = state.move_count - level.optimal_moves
        penalty_ratio = min(overage / level.optimal_moves, 1.0)
        penalty = int(base_score * penalty_ratio * self.OVERAGE_PENALTY_FACTOR)

        final_score = max(base_score - penalty, 0)

        logger.info(
            "Max-move penalty applied",
            base_score=base_score,
            overage=overage,
            penalty=penalty,
            final_score=final_score,
        )

        return final_score
