"""
models/behavior/visibility.py

Author: Jason Fuller

Visibility and fog-of-war policies.

Responsibilities:
- Define visibility strategies for UI projection
- Encode difficulty-based perception rules
- Provide immutable, stateless visibility policies

Architectural role:
- UI projection logic
- Implements the Strategy pattern
- Decouples perception from gameplay logic

Logging:
- DEBUG: projection details and per-room visibility checks
- INFO: visibility policy application
"""

# ------------------------------------------------------------------
# Standard library imports
# ------------------------------------------------------------------
from abc import ABC, abstractmethod
from dataclasses import dataclass

# ------------------------------------------------------------------
# Local application imports
# ------------------------------------------------------------------
from utils.logger import get_logger


logger = get_logger(__name__)


# ------------------------------------------------------------------
# UI projection model
# ------------------------------------------------------------------

@dataclass(frozen=True)
class LevelUIProjection:
    """
    Read-only projection of level information suitable for UI rendering.

    Structure:
    - show_full_map: whether all rooms may be rendered
    - show_items: whether item icons may be shown
    - show_villain: whether the villain may be shown
    - discovered_rooms: set of room identifiers considered visible

    Design notes:
    - This object is derived data and should not be persisted.
    - UI layers must rely exclusively on this projection.

    Invariants:
    - discovered_rooms is a subset of level.map.rooms
    """

    show_full_map: bool
    show_items: bool
    show_villain: bool
    discovered_rooms: set[str]

    def can_render_room(self, room_name: str) -> bool:
        """
        Determine whether a room should be rendered by the UI.
        """
        allowed = self.show_full_map or room_name in self.discovered_rooms

        logger.debug(
            "Room visibility check",
            room=room_name,
            show_full_map=self.show_full_map,
            is_discovered=room_name in self.discovered_rooms,
            can_render=allowed,
        )

        return allowed


# ------------------------------------------------------------------
# Visibility strategy base
# ------------------------------------------------------------------

class VisibilityPolicy(ABC):
    """
    Abstract base class for visibility strategies.

    Design intent:
    - Encapsulate perception rules independently of gameplay logic
    - Allow difficulty changes without modifying controllers or UI code
    """

    @abstractmethod
    def project(self, level, state) -> LevelUIProjection:
        """
        Produce a UI projection for the given level and game state.
        """
        raise NotImplementedError


# ------------------------------------------------------------------
# Concrete policies
# ------------------------------------------------------------------

class EasyVisibility(VisibilityPolicy):
    """
    Omniscient visibility policy.
    """

    def project(self, level, state) -> LevelUIProjection:
        logger.info(
            "Applying Easy visibility policy",
            level_id=level.id,
            visited_rooms=len(state.visited_rooms),
        )

        projection = LevelUIProjection(
            show_full_map=True,
            show_items=True,
            show_villain=True,
            discovered_rooms=set(level.map.rooms.keys()),
        )

        logger.debug(
            "Easy visibility projection created",
            visible_rooms=len(projection.discovered_rooms),
            show_items=projection.show_items,
            show_villain=projection.show_villain,
        )

        return projection


class MediumVisibility(VisibilityPolicy):
    """
    Partial-information visibility policy.
    """

    def project(self, level, state) -> LevelUIProjection:
        logger.info(
            "Applying Medium visibility policy",
            level_id=level.id,
            visited_rooms=len(state.visited_rooms),
        )

        projection = LevelUIProjection(
            show_full_map=True,
            show_items=False,
            show_villain=True,
            discovered_rooms=set(level.map.rooms.keys()),
        )

        logger.debug(
            "Medium visibility projection created",
            visible_rooms=len(projection.discovered_rooms),
            show_items=projection.show_items,
            show_villain=projection.show_villain,
        )

        return projection


class HardVisibility(VisibilityPolicy):
    """
    Fog-of-war visibility policy.
    """

    def project(self, level, state) -> LevelUIProjection:
        discovered = state.visited_rooms | {state.player.location}

        logger.info(
            "Applying Hard visibility policy",
            level_id=level.id,
            visited_rooms=len(state.visited_rooms),
            current_room=state.player.location,
        )

        projection = LevelUIProjection(
            show_full_map=False,
            show_items=False,
            show_villain=False,
            discovered_rooms=discovered,
        )

        logger.debug(
            "Hard visibility projection created",
            visible_rooms=len(projection.discovered_rooms),
            show_items=projection.show_items,
            show_villain=projection.show_villain,
        )

        return projection
