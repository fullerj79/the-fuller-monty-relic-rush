"""
models/domain/map_graph.py

Author: Jason Fuller

Map graph and spatial layout.

Responsibilities:
- Represent immutable room connectivity
- Provide spatial metadata for UI rendering
- Expose topology queries for navigation and pathfinding

Architectural role:
- Domain model (static structure)
- Represents logical connectivity between rooms
- Provides spatial hints for rendering, not gameplay rules

Design notes:
- MapGraph is immutable after construction
- Coordinates encode layout only; they do not imply adjacency
- Movement rules are governed by exits, not spatial proximity

Logging:
- DEBUG: graph construction and topology queries
"""

# ------------------------------------------------------------------
# Domain imports
# ------------------------------------------------------------------
from models.domain.room import Room

# ------------------------------------------------------------------
# Local application imports
# ------------------------------------------------------------------
from utils.logger import get_logger


logger = get_logger(__name__)


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
    """

    def __init__(
        self,
        rooms: dict[str, Room],
        coords: dict[str, tuple[int, int]],
    ):
        """
        Construct a MapGraph from validated room and coordinate data.

        Assumptions:
        - rooms and coords have already been validated for consistency
        - no runtime mutation will occur after construction
        """
        self.rooms = rooms
        self.coords = coords

        # ----------------------------------------------------------
        # Spatial extents (rendering only)
        # ----------------------------------------------------------

        xs = {x for x, _ in coords.values()}
        ys = {y for _, y in coords.values()}

        self._xs_sorted = sorted(xs)
        self._ys_sorted = sorted(ys)

        self.width = len(self._xs_sorted)
        self.height = len(self._ys_sorted)

        logger.debug(
            "MapGraph constructed",
            room_count=len(rooms),
            width=self.width,
            height=self.height,
            x_range=self._xs_sorted,
            y_range=self._ys_sorted,
        )

    # ------------------------------------------------------------------
    # Topology
    # ------------------------------------------------------------------

    def move(self, current_room: str, direction: str) -> str | None:
        """
        Resolve a movement request from a room in a given direction.

        Returns:
            Destination room_id if the exit exists, otherwise None.
        """
        dest = self.rooms[current_room].exits.get(direction)

        logger.debug(
            "Resolving move",
            from_room=current_room,
            direction=direction,
            to_room=dest,
        )

        return dest

    def neighbors(self, room_name: str) -> dict[str, str]:
        """
        Return all outgoing exits for a given room.

        Returns:
            Mapping of direction → neighboring room_id.
        """
        exits = self.rooms[room_name].exits

        logger.debug(
            "Fetching neighbors",
            room=room_name,
            exit_count=len(exits),
            exits=exits,
        )

        return exits

    # ------------------------------------------------------------------
    # Rendering helpers
    # ------------------------------------------------------------------

    def grid_x_index(self, x: int) -> int:
        """
        Convert a raw x-coordinate into a compact grid column index.

        This avoids phantom columns caused by sparse coordinates.
        """
        return self._xs_sorted.index(x)

    def grid_y_index(self, y: int) -> int:
        """
        Convert a raw y-coordinate into a compact grid row index.
        """
        return self._ys_sorted.index(y)
