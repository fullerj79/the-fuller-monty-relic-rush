"""
models/domain/status.py

Author: Jason Fuller

Game status enumeration.

Responsibilities:
- Represent the lifecycle state of a game session
- Classify game outcomes without owning behavior

Architectural role:
- Domain model (state classification)
- Stored as part of GameState
- Consumed by rules, scoring, and UI layers

Design notes:
- GameStatus represents what is true, not what should happen
- Transitions are owned by rules and controller logic
- Modeled as an enum for clarity and exhaustiveness

Logging:
- None (pure declarative state)
"""

# ------------------------------------------------------------------
# Standard library imports
# ------------------------------------------------------------------
from enum import Enum


class GameStatus(Enum):
    """
    Enumeration of possible game lifecycle states.

    Values:
    - IN_PROGRESS: game is active and accepting player actions
    - COMPLETED: game has ended in a win
    - GAME_OVER: game has ended in a loss
    """

    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    GAME_OVER = "game_over"

    @property
    def is_terminal(self) -> bool:
        """
        Indicate whether this status represents a terminal game state.

        Returns:
            True for COMPLETED or GAME_OVER, False otherwise.
        """
        return self in {GameStatus.COMPLETED, GameStatus.GAME_OVER}
