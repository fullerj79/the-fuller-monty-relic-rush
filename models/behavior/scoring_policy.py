"""
Scoring policy definitions by difficulty.

Author: Jason Fuller
Date: 2/1/26

This module defines difficulty-based scoring policies used to modify
efficiency-based scoring. Policies encapsulate how difficulty affects
final score calculations without embedding that logic directly into
scoring strategies.

Architectural role:
- Domain policy (configuration + behavior)
- Injected into Level at construction time
- Consumed by ScoreStrategy implementations

ScoringPolicy instances are immutable and stateless.
"""

from abc import ABC, abstractmethod


class ScoringPolicy(ABC):
    """
    Abstract base class for difficulty-based scoring behavior.

    Design intent:
    - Encapsulate difficulty-specific scoring modifiers
    - Decouple difficulty logic from scoring algorithms
    - Enable future expansion (e.g., hardcore modes, penalties)

    Subclasses define how difficulty influences efficiency scoring.
    """

    @abstractmethod
    def multiplier(self) -> float:
        """
        Return the difficulty multiplier applied to efficiency scores.

        Returns:
        - Float multiplier (e.g., 1.0 for medium difficulty)

        Notes:
        - Must be deterministic
        - Must not depend on runtime state
        """
        pass


class EasyScoring(ScoringPolicy):
    """
    Scoring policy for easy difficulty.

    Design notes:
    - Reduced multiplier rewards completion over efficiency
    - Intended for onboarding and casual play
    """

    def multiplier(self) -> float:
        return 0.75


class MediumScoring(ScoringPolicy):
    """
    Scoring policy for medium difficulty.

    Design notes:
    - Baseline difficulty
    - No efficiency scaling bias
    """

    def multiplier(self) -> float:
        return 1.0


class HardScoring(ScoringPolicy):
    """
    Scoring policy for hard difficulty.

    Design notes:
    - Increased multiplier rewards optimal play
    - Intended for experienced players
    """

    def multiplier(self) -> float:
        return 1.25
