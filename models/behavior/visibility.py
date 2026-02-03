"""
Visibility and fog-of-war policies.

Author: Jason Fuller
Date: 2/1/26

This module defines visibility strategies that control how much of a
level is revealed to the player at any given time. Visibility policies
do not affect gameplay logic; they only influence what information is
exposed to the UI.

Architectural role:
- UI projection logic
- Implements the Strategy pattern
- Encodes difficulty-based perception rules

Visibility policies are immutable and stateless. They derive all output
from Level and GameState without modifying either.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
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
    - UI layers must rely exclusively on this projection, not raw state.

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

        Parameters:
        - room_name: room identifier

        Returns:
        - True if the room may be rendered
        - False if the room should be hidden (fog-of-war)

        Notes:
        - This method centralizes fog-of-war logic.
        - UI code should not reimplement visibility checks.
        """
        return self.show_full_map or room_name in self.discovered_rooms


class VisibilityPolicy(ABC):
    """
    Abstract base class for visibility strategies.

    Design intent:
    - Encapsulate perception rules independently of gameplay logic
    - Allow difficulty changes without modifying controllers or UI code

    Subclasses implement different visibility behaviors (e.g., easy,
    medium, hard) by producing a LevelUIProjection.
    """

    @abstractmethod
    def project(self, level, state) -> LevelUIProjection:
        """
        Produce a UI projection for the given level and game state.

        Parameters:
        - level: active Level configuration
        - state: current GameState

        Returns:
        - LevelUIProjection describing what the UI may display

        Side effects:
        - None
        """
        pass


class EasyVisibility(VisibilityPolicy):
    """
    Omniscient visibility policy.

    Behavior:
    - Entire map is visible at all times
    - Items and villain are always revealed

    Intended use:
    - Beginner-friendly mode
    - Debugging and development
    """

    def project(self, level, state) -> LevelUIProjection:
        return LevelUIProjection(
            show_full_map=True,
            show_items=True,
            show_villain=True,
            discovered_rooms=set(level.map.rooms.keys()),
        )


class MediumVisibility(VisibilityPolicy):
    """
    Partial-information visibility policy.

    Behavior:
    - Entire map layout is visible
    - Items and villain are hidden

    Intended use:
    - Standard gameplay
    - Emphasizes navigation and planning without spoilers
    """

    def project(self, level, state) -> LevelUIProjection:
        return LevelUIProjection(
            show_full_map=True,
            show_items=False,
            show_villain=False,
            discovered_rooms=set(level.map.rooms.keys()),
        )


class HardVisibility(VisibilityPolicy):
    """
    Fog-of-war visibility policy.

    Behavior:
    - Only rooms the player has visited are visible
    - Items and villain are hidden
    - Map is gradually revealed through exploration

    Intended use:
    - Advanced gameplay
    - Encourages careful exploration and memory
    """

    def project(self, level, state) -> LevelUIProjection:
        discovered = state.visited_rooms | {state.player.location}
        return LevelUIProjection(
            show_full_map=False,
            show_items=False,
            show_villain=False,
            discovered_rooms=discovered,
        )
