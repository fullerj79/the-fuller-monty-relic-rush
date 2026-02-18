"""
models/behavior/scoring_policy.py

Author: Jason Fuller

Scoring policy definitions by difficulty.

Responsibilities:
- Define difficulty-based scoring multipliers
- Modify efficiency-based scores without embedding logic in strategies
- Provide immutable, stateless scoring policies

Logging:
- DEBUG: scoring multiplier resolution
"""

# ------------------------------------------------------------------
# Standard library imports
# ------------------------------------------------------------------
from abc import ABC, abstractmethod

# ------------------------------------------------------------------
# Local application imports
# ------------------------------------------------------------------
from utils.logger import get_logger


logger = get_logger(__name__)


class ScoringPolicy(ABC):
    """
    Abstract base class for difficulty-based scoring behavior.

    ScoringPolicy defines how difficulty modifies efficiency-based
    scoring without embedding that logic directly into score strategies.

    Policies are:
    - Immutable
    - Stateless
    - Deterministic
    """

    @abstractmethod
    def multiplier(self) -> float:
        """
        Return the difficulty multiplier applied to efficiency scores.

        Returns:
            float: Difficulty multiplier (e.g. 1.0 for medium difficulty)
        """
        raise NotImplementedError


class EasyScoring(ScoringPolicy):
    """
    Scoring policy for easy difficulty.

    Rewards completion over efficiency.
    Intended for onboarding and casual play.
    """

    def multiplier(self) -> float:
        value = 0.75

        logger.debug(
            "Easy scoring multiplier resolved",
            multiplier=value,
        )

        return value


class MediumScoring(ScoringPolicy):
    """
    Scoring policy for medium difficulty.

    Baseline difficulty with no efficiency bias.
    """

    def multiplier(self) -> float:
        value = 1.0

        logger.debug(
            "Medium scoring multiplier resolved",
            multiplier=value,
        )

        return value


class HardScoring(ScoringPolicy):
    """
    Scoring policy for hard difficulty.

    Rewards optimal and efficient play.
    Intended for experienced players.
    """

    def multiplier(self) -> float:
        value = 1.25

        logger.debug(
            "Hard scoring multiplier resolved",
            multiplier=value,
        )

        return value
