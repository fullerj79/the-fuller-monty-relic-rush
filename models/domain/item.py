"""
Item domain models.

Author: Jason Fuller
Date: 2/1/26

This module defines Item and its concrete subclasses. Items represent
interactive entities that can exist within a Room and trigger behavior
when encountered by the player.

Architectural role:
- Domain model (static definition + polymorphic behavior)
- Items are immutable value objects
- Behavior is executed via polymorphic hooks

Items do not manage their own location, lifecycle, or persistence.
Those concerns are handled by Room, GameState, and higher-level systems.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Item:
    """
    Base class for all items that may appear in a room.

    Structure:
    - name: human-readable identifier for the item

    Design notes:
    - Items are immutable value objects.
    - Items do not track whether they have been collected.
    - Items do not know which room they belong to.

    Polymorphism:
    - Subclasses override on_enter() to define behavior when a player
      enters a room containing this item.

    This class does NOT:
    - mutate game state directly beyond its defined hook
    - enforce win/loss rules
    - handle persistence or scoring
    """

    name: str

    def on_enter(self, state) -> None:
        """
        Polymorphic hook invoked when a player enters a room
        containing this item.

        Default behavior:
        - No-op (base Item has no effect)

        Parameters:
        - state: GameState instance for the active session

        Assumptions:
        - This method is called by the controller or rules engine
        - State mutation is intentional and controlled

        Subclasses are expected to override this method.
        """
        pass


class Relic(Item):
    """
    Collectible item required to complete a level.

    Behavior:
    - Adds itself to the player's collected_items
    - Emits a collection event

    Design notes:
    - Collection is recorded in GameState, not in the Item or Room.
    - Relics are treated as unique by name.
    """

    def on_enter(self, state) -> None:
        # Record collection in the mutable game state
        state.collected_items.add(self.name)
        state.event_log.append(f"Collected {self.name}")


class Villain(Item):
    """
    Represents the level's villain or final encounter.

    Behavior:
    - Marks that the villain has been encountered
    - Actual win/loss resolution is handled by LevelRules

    Design notes:
    - Villain does not decide the outcome of the game.
    - This separation allows alternate rulesets to reuse the same item.
    """

    def on_enter(self, state) -> None:
        state.encountered_villain = True
        state.event_log.append("Encountered the villain")
