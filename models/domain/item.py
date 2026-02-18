"""
models/domain/item.py

Author: Jason Fuller

Item domain models.

Responsibilities:
- Define immutable item value objects
- Provide polymorphic hooks for room-entry behavior
- Emit domain-level side effects via GameState mutation

Architectural role:
- Domain model (static definition + polymorphic behavior)
- Items are immutable value objects
- Behavior is executed via polymorphic hooks

Design notes:
- Items do not manage their own location or persistence
- Items do not own lifecycle or win/loss logic
- Rendering semantics are expressed symbolically

Logging:
- DEBUG: item encounter and behavior execution
"""

# ------------------------------------------------------------------
# Standard library imports
# ------------------------------------------------------------------
from dataclasses import dataclass

# ------------------------------------------------------------------
# Local application imports
# ------------------------------------------------------------------
from utils.logger import get_logger


logger = get_logger(__name__)


@dataclass(frozen=True)
class Item:
    """
    Base class for all items that may appear in a room.

    Structure:
    - name: human-readable identifier
    - render_key: symbolic identifier used by the UI layer

    Polymorphism:
    - Subclasses override on_enter() to define behavior when
      a player enters a room containing this item.
    """

    name: str
    render_key: str = "empty"

    def on_enter(self, state) -> None:
        """
        Polymorphic hook invoked when a player enters a room
        containing this item.

        Default behavior:
        - No-op
        """
        logger.debug(
            "Entered room containing non-interactive item",
            item_name=self.name,
            render_key=self.render_key,
        )


# ------------------------------------------------------------------
# Relic
# ------------------------------------------------------------------

class Relic(Item):
    """
    Collectible item required to complete a level.

    Behavior:
    - Automatically collected on room entry
    - Records collection in GameState
    - Emits a collection event

    UI semantics:
    - render_key = "relic"
    """

    def __init__(self, name: str):
        super().__init__(name=name, render_key="relic")

    def on_enter(self, state) -> None:
        if self.name in state.collected_items:
            logger.debug(
                "Relic already collected; skipping",
                item_name=self.name,
            )
            return

        state.collected_items.add(self.name)
        state.event_log.append(f"Collected {self.name}")
        state.message = f"Collected {self.name}"

        logger.debug(
            "Relic collected",
            item_name=self.name,
            total_collected=len(state.collected_items),
        )


# ------------------------------------------------------------------
# Villain
# ------------------------------------------------------------------

class Villain(Item):
    """
    Represents the level's villain or final encounter.

    Behavior:
    - Marks that the villain has been encountered
    - Emits an encounter event
    - Win/loss resolution handled by rules

    UI semantics:
    - render_key = "villain"
    """

    def __init__(self, name: str = "Villain"):
        super().__init__(name=name, render_key="villain")

    def on_enter(self, state) -> None:
        if state.encountered_villain:
            logger.debug(
                "Villain already encountered; ignoring",
                item_name=self.name,
            )
            return

        state.encountered_villain = True
        state.event_log.append("Encountered the villain")

        logger.debug(
            "Villain encountered",
            item_name=self.name,
        )
