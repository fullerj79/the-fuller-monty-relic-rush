"""
Game status enumeration.

Author: Jason Fuller
Date: 2/1/26

This module defines GameStatus, a finite enumeration representing the
lifecycle state of a game session. GameStatus captures high-level outcome
and progression information without owning behavior.

Architectural role:
- Domain model (state classification)
- Stored as part of GameState
- Consumed by rules, scoring, and UI layers

GameStatus is intentionally modeled as an enum rather than a class
hierarchy. Status represents *what is true*, not *what should happen*.
"""

from enum import Enum


class GameStatus(Enum):
    """
    Enumeration of possible game lifecycle states.

    Values:
    - IN_PROGRESS: game is active and accepting player actions
    - COMPLETED: game has ended in a win
    - GAME_OVER: game has ended in a loss

    Design notes:
    - GameStatus is a declarative fact, not a behavior controller.
    - Transitions are owned by rules and controller logic.
    - Consumers should react to status, not modify it arbitrarily.

    This enum does NOT:
    - enforce allowed actions
    - trigger side effects
    - manage state transitions
    """

    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    GAME_OVER = "game_over"

    @property
    def is_terminal(self) -> bool:
        """
        Indicate whether this status represents a terminal game state.

        Returns:
        - True for COMPLETED or GAME_OVER
        - False for IN_PROGRESS

        Notes:
        - This helper centralizes terminal-state checks.
        - Avoids scattering status comparisons across the codebase.
        """
        return self in {GameStatus.COMPLETED, GameStatus.GAME_OVER}
