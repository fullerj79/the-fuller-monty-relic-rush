"""
Map graph and spatial layout.

Author: Jason Fuller
Date: 2/1/26

This module defines MapGraph, the immutable representation of a level's
topology and spatial embedding. MapGraph models rooms as nodes and exits
as directed edges, with optional coordinate metadata used exclusively
for visualization.

Architectural role:
- Domain model (static structure)
- Represents logical connectivity between rooms
- Provides spatial hints for rendering (coords), not gameplay rules

MapGraph is intentionally immutable after construction. Any runtime
mutation would invalidate pathfinding guarantees, solvability proofs,
and cached optimal-move calculations.
"""

from models.domain.room import Room


class MapGraph:
    """
    Immutable graph representing room connectivity and layout.

    Structure:
    - rooms: mapping of room_id → Room object
    - coords: mapping of room_id → (x, y) coordinates

    Invariants:
    - Every room_id in rooms has a corresponding entry in coords
    - coords are unique per room_id (no overlaps)
    - exits reference only valid room_ids in rooms
    - coords encode spatial layout only; they do not imply adjacency

    Design notes:
    - Rooms define logical connectivity via exits.
    - Coordinates exist solely to support map rendering and UI projection.
    - Movement rules are based on exits, not coordinate proximity.

    This class does NOT:
    - track player position
    - enforce visibility rules
    - mutate rooms or items
    - perform validation (handled at load time)
    """

    def __init__(self, rooms: dict[str, Room], coords: dict[str, tuple[int, int]]):
        """
        Construct a MapGraph from validated room and coordinate data.

        Assumptions:
        - rooms and coords have already been validated for consistency
        - no runtime mutation will occur after construction

        Parameters:
        - rooms: mapping of room identifiers to Room objects
        - coords: mapping of room identifiers to (x, y) coordinates
        """
        self.rooms = rooms
        self.coords = coords

    def move(self, current_room: str, direction: str) -> str | None:
        """
        Resolve a movement request from a room in a given direction.

        Parameters:
        - current_room: the room identifier the player is currently in
        - direction: direction string (e.g., 'North', 'South')

        Returns:
        - room_id of the destination room if the exit exists
        - None if no exit exists in the given direction

        Notes:
        - This method performs no state mutation.
        - Validation of current_room is the caller's responsibility.
        """
        return self.rooms[current_room].exits.get(direction)

    def neighbors(self, room_name: str) -> dict[str, str]:
        """
        Return all outgoing exits for a given room.

        Parameters:
        - room_name: room identifier

        Returns:
        - mapping of direction → neighboring room_id

        This method exposes topology only and does not imply any ordering
        or spatial relationship beyond what exits explicitly define.
        """
        return self.rooms[room_name].exits
