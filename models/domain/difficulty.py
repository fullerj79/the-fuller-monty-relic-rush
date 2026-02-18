"""
models/domain/difficulty.py

Author: Jason Fuller

Difficulty classification and policy resolution.

Responsibilities:
- Classify difficulty levels
- Resolve visibility, scoring policies, and scoring strategies
- Centralize difficulty-based configuration

Architectural role:
- Domain model (configuration classification)
- Selects policies and strategies
- Does not implement gameplay or scoring logic

Logging:
- DEBUG: policy and strategy resolution
"""

# ------------------------------------------------------------------
# Standard library imports
# ------------------------------------------------------------------
from enum import Enum

# ------------------------------------------------------------------
# Behavior / policies
# ------------------------------------------------------------------
from models.behavior.visibility import (
    EasyVisibility,
    MediumVisibility,
    HardVisibility,
)
from models.behavior.scoring_policy import (
    EasyScoring,
    MediumScoring,
    HardScoring,
)

# ------------------------------------------------------------------
# Scoring strategies
# ------------------------------------------------------------------
from models.domain.scoring import (
    StandardScore,
    MaxMovesScore,
)

# ------------------------------------------------------------------
# Local application imports
# ------------------------------------------------------------------
from utils.logger import get_logger


logger = get_logger(__name__)


class Difficulty(Enum):
    """
    Enumeration of supported difficulty levels.

    Difficulty selects policies and strategies but does not
    implement gameplay or scoring logic itself.
    """

    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

    # ------------------------------------------------------------------
    # Visibility policy
    # ------------------------------------------------------------------

    @property
    def visibility_policy(self):
        """
        Resolve the VisibilityPolicy for this difficulty.
        """
        logger.debug(
            "Resolving visibility policy",
            difficulty=self.value,
        )

        match self:
            case Difficulty.EASY:
                policy = EasyVisibility()
            case Difficulty.MEDIUM:
                policy = MediumVisibility()
            case Difficulty.HARD:
                policy = HardVisibility()
            case _:
                raise ValueError(f"Unhandled difficulty: {self}")

        logger.debug(
            "Visibility policy resolved",
            difficulty=self.value,
            policy=policy.__class__.__name__,
        )

        return policy

    # ------------------------------------------------------------------
    # Scoring multiplier policy
    # ------------------------------------------------------------------

    @property
    def scoring_policy(self):
        """
        Resolve the ScoringPolicy (multiplier behavior).

        This controls how difficulty scales efficiency,
        not how scores are calculated.
        """
        logger.debug(
            "Resolving scoring multiplier policy",
            difficulty=self.value,
        )

        match self:
            case Difficulty.EASY:
                policy = EasyScoring()
            case Difficulty.MEDIUM:
                policy = MediumScoring()
            case Difficulty.HARD:
                policy = HardScoring()
            case _:
                raise ValueError(f"Unhandled difficulty: {self}")

        logger.debug(
            "Scoring multiplier policy resolved",
            difficulty=self.value,
            policy=policy.__class__.__name__,
        )

        return policy

    # ------------------------------------------------------------------
    # Scoring strategy
    # ------------------------------------------------------------------

    @property
    def scoring_strategy(self):
        """
        Resolve the ScoreStrategy (scoring algorithm).

        This controls how a score is calculated.
        """
        logger.debug(
            "Resolving scoring strategy",
            difficulty=self.value,
        )

        match self:
            case Difficulty.EASY:
                strategy = StandardScore()
            case Difficulty.MEDIUM:
                strategy = StandardScore()
            case Difficulty.HARD:
                strategy = MaxMovesScore()
            case _:
                raise ValueError(f"Unhandled difficulty: {self}")

        logger.debug(
            "Scoring strategy resolved",
            difficulty=self.value,
            strategy=strategy.__class__.__name__,
        )

        return strategy

    # ------------------------------------------------------------------
    # Serialization helpers
    # ------------------------------------------------------------------

    @property
    def label(self) -> str:
        """
        Canonical string label for persistence.
        """
        return self.value
