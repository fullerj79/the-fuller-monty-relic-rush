"""
models/domain/rules.py

Author: Jason Fuller

Level rules and win/loss logic.

Responsibilities:
- Interpret GameState changes after player actions
- Determine win/loss conditions
- Perform lifecycle state transitions

Architectural role:
- Domain logic (behavioral rules)
- Owns win/loss conditions and terminal state transitions
- Invoked by the GameController after state updates

Design notes:
- Rules are immutable and stateless
- All runtime information is read from and written to GameState
- No persistence or UI responsibilities

Logging:
- DEBUG: rule evaluation and decision paths
- INFO: terminal win/loss resolution
"""

# ------------------------------------------------------------------
# Standard library imports
# ------------------------------------------------------------------
from abc import ABC, abstractmethod

# ------------------------------------------------------------------
# Domain imports
# ------------------------------------------------------------------
from models.domain.item import Villain
from models.domain.status import GameStatus

# ------------------------------------------------------------------
# Local application imports
# ------------------------------------------------------------------
from utils.logger import get_logger


logger = get_logger(__name__)


class LevelRules(ABC):
    """
    Abstract base class for level rule sets.

    Design intent:
    - Encapsulate win/loss logic separately from game state and UI
    - Allow multiple rule implementations to coexist
    - Enable swapping rules without modifying controllers
    """

    @abstractmethod
    def check(self, state, room) -> None:
        """
        Evaluate rules after a player enters a room.

        Side effects:
        - May update state.status
        - May update state.message
        """
        raise NotImplementedError


class StandardRules(LevelRules):
    """
    Standard win/loss ruleset for a level.

    Rule definition:
    - Encounter villain with all required items → WIN
    - Encounter villain without all required items → LOSS
    - All other encounters have no immediate effect
    """

    def __init__(self, required_items: set[str]):
        """
        Initialize the ruleset with required items.

        Args:
            required_items: Set of item identifiers required to win
        """
        self.required_items = required_items

    def check(self, state, room) -> None:
        """
        Apply standard win/loss rules for the current room.
        """
        logger.debug(
            "Evaluating level rules",
            room=room.name,
            has_villain=isinstance(room.item, Villain),
            collected_items=len(state.collected_items),
            required_items=len(self.required_items),
        )

        if isinstance(room.item, Villain):
            if state.collected_items >= self.required_items:
                state.status = GameStatus.COMPLETED
                state.message = "You defeated the villain!"

                logger.info(
                    "Game completed successfully",
                    collected_items=len(state.collected_items),
                )
            else:
                state.status = GameStatus.GAME_OVER
                state.message = "You found the villain too soon."

                logger.info(
                    "Game over: villain encountered too early",
                    collected_items=len(state.collected_items),
                    missing_items=len(self.required_items - state.collected_items),
                )
