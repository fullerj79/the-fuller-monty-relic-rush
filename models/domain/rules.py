"""
Level rules and win/loss logic.

Author: Jason Fuller
Date: 2/1/26

This module defines the rules layer responsible for interpreting
GameState changes and determining game outcomes. Rules translate
in-game events (e.g., encountering a villain) into lifecycle
transitions such as win or loss.

Architectural role:
- Domain logic (behavioral rules)
- Owns win/loss conditions and state transitions
- Invoked by the game controller after state updates

Rules are immutable and stateless. They do not track progress over time
and do not persist data. All runtime information is read from and
written to GameState.
"""

from abc import ABC, abstractmethod
from models.domain.item import Villain
from models.domain.status import GameStatus


class LevelRules(ABC):
    """
    Abstract base class for level rule sets.

    Design intent:
    - Encapsulate win/loss logic separately from game state and UI
    - Allow multiple rule implementations to coexist
    - Enable swapping rules without modifying controllers

    Subclasses define how GameState transitions occur in response
    to player actions and encounters.

    This class does NOT:
    - perform movement
    - track state across turns
    - calculate scores
    - interact with UI or persistence layers
    """

    @abstractmethod
    def check(self, state, room) -> None:
        """
        Evaluate rules after a player enters a room.

        Parameters:
        - state: current GameState instance
        - room: Room object the player has entered

        Side effects:
        - May update state.status
        - May update state.message

        Notes:
        - This method is expected to be called by the controller
          after movement and item hooks have been processed.
        """
        pass


class StandardRules(LevelRules):
    """
    Standard win/loss ruleset for a level.

    Rule definition:
    - If the player encounters the villain AND has collected all
      required items, the game is won.
    - If the player encounters the villain without all required
      items, the game is lost.
    - All other encounters have no immediate effect.

    Design notes:
    - Required items are provided at construction time.
    - This ruleset assumes exactly one villain encounter per level.
    - Optimal-move BFS validation relies on these rules being stable.
    """

    def __init__(self, required_items: set[str]):
        """
        Initialize the ruleset with required items.

        Parameters:
        - required_items: set of item identifiers required to win

        Assumptions:
        - required_items is non-empty
        - Item identifiers are unique within the level
        """
        self.required_items = required_items

    def check(self, state, room) -> None:
        """
        Apply standard win/loss rules for the current room.

        This method interprets the presence of a Villain item and
        compares the player's collected items against the required
        set.

        Side effects:
        - Updates state.status to COMPLETED or GAME_OVER
        - Sets a user-facing message describing the outcome

        Notes:
        - This method does not remove items or alter the map.
        - Repeated calls after a terminal state are safe but
          expected to be short-circuited by the controller.
        """
        if isinstance(room.item, Villain):
            if state.collected_items >= self.required_items:
                state.status = GameStatus.COMPLETED
                state.message = "You defeated the villain!"
            else:
                state.status = GameStatus.GAME_OVER
                state.message = "You found the villain too soon."
