"""
Difficulty classification and policy resolution.

Author: Jason Fuller
Date: 2/1/26

This module defines Difficulty, an enumeration representing the intended
challenge level of a game configuration. Difficulty controls *policy
selection*, not gameplay rules.

Architectural role:
- Domain model (configuration classification)
- Centralizes difficulty-based behavior selection
- Consumed by LevelFactory at construction time

Difficulty does NOT:
- Enforce win/loss rules
- Mutate game state
- Encode UI behavior directly
"""

from enum import Enum

from models.behavior.visibility import (
    EasyVisibility,
    MediumVisibility,
    HardVisibility,
)
from models.domain.scoring import (
    StandardScore,
    MaxMovesScore,
)


class Difficulty(Enum):
    """
    Enumeration of supported difficulty levels.

    Values:
    - EASY: forgiving visibility and scoring
    - MEDIUM: balanced defaults
    - HARD: restricted visibility and efficiency penalties

    Design notes:
    - Difficulty selects policies, not logic.
    - All difficulty-based branching is centralized here.
    """

    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

    # ------------------------------------------------------------------
    # Policy resolution
    # ------------------------------------------------------------------

    def visibility_policy(self):
        """
        Resolve the VisibilityPolicy associated with this difficulty.
        """
        match self:
            case Difficulty.EASY:
                return EasyVisibility()
            case Difficulty.MEDIUM:
                return MediumVisibility()
            case Difficulty.HARD:
                return HardVisibility()

    def scoring_policy(self):
        """
        Resolve the ScoreStrategy associated with this difficulty.
        """
        match self:
            case Difficulty.EASY:
                return StandardScore()
            case Difficulty.MEDIUM:
                return StandardScore()
            case Difficulty.HARD:
                return MaxMovesScore()

    @property
    def label(self) -> str:
        """
        Return the canonical string label used in persistence formats.
        """
        return self.value
