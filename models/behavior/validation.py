"""
models/behavior/validation.py

Author: Jason Fuller

Level validation and solvability checks.

Responsibilities:
- Validate structural correctness of level definitions
- Enforce invariants relied upon by runtime systems
- Compute level solvability and optimal move counts

Logging:
- DEBUG: validation steps, BFS state exploration
- INFO: validation lifecycle milestones, solvability success
- WARN: recoverable anomalies (none expected)
- ERROR: invalid or unsolvable level definitions
"""

# ------------------------------------------------------------------
# Standard library imports
# ------------------------------------------------------------------
from collections import deque

# ------------------------------------------------------------------
# Local application imports
# ------------------------------------------------------------------
from utils.logger import get_logger


logger = get_logger(__name__)


class LevelValidationError(Exception):
    """Raised when a level definition fails validation."""


# ------------------------------------------------------------------
# Structural validation
# ------------------------------------------------------------------

def validate_level_definition(defn: dict) -> None:
    """
    Validate the structural correctness of a level definition.

    Raises:
        LevelValidationError if the definition is invalid.
    """
    logger.info(
        "Validating level definition",
        level_id=defn.get("id"),
    )

    required_keys = {
        "id",
        "name",
        "difficulty",
        "start_room",
        "rooms",
        "coords",
        "rules",
    }

    missing = required_keys - defn.keys()
    if missing:
        logger.error(
            "Missing required level keys",
            missing=list(missing),
        )
        raise LevelValidationError(f"Missing required keys: {missing}")

    rooms = defn["rooms"]

    if defn["start_room"] not in rooms:
        logger.error(
            "Invalid start room",
            start_room=defn["start_room"],
        )
        raise LevelValidationError("Start room does not exist")

    # --------------------------------------------------------------
    # Exit validation
    # --------------------------------------------------------------

    for room, data in rooms.items():
        for direction, target in data.get("exits", {}).items():
            if target not in rooms:
                logger.error(
                    "Invalid exit detected",
                    room=room,
                    direction=direction,
                    target=target,
                )
                raise LevelValidationError(
                    f"Room '{room}' has invalid exit to '{target}'"
                )

    # --------------------------------------------------------------
    # Coordinate validation
    # --------------------------------------------------------------

    for room in rooms:
        if room not in defn["coords"]:
            logger.error(
                "Missing room coordinates",
                room=room,
            )
            raise LevelValidationError(f"Room '{room}' missing coordinates")

    # --------------------------------------------------------------
    # Villain validation
    # --------------------------------------------------------------

    villains = [
        r for r in rooms.values()
        if r.get("item") and r["item"]["type"] == "villain"
    ]

    if len(villains) != 1:
        logger.error(
            "Invalid villain count",
            count=len(villains),
        )
        raise LevelValidationError("Level must contain exactly one villain")

    logger.info("Level definition validation passed")


# ------------------------------------------------------------------
# Solvability / optimal move computation
# ------------------------------------------------------------------

def compute_optimal_moves(map_graph, start_room, required_items: set[str]) -> int:
    """
    Compute the minimum number of moves required to collect all required
    items and reach the villain.

    Uses BFS over (room, collected_items) state space.

    Raises:
        LevelValidationError if the level is not solvable.
    """
    logger.info(
        "Computing optimal moves",
        start_room=start_room,
        required_item_count=len(required_items),
        required_items=sorted(required_items),
    )

    visited: set[tuple[str, frozenset]] = set()
    queue = deque([(start_room, frozenset(), 0)])

    explored_states = 0

    while queue:
        room, items, dist = queue.popleft()
        explored_states += 1

        if (room, items) in visited:
            continue

        visited.add((room, items))

        logger.debug(
            "Exploring state",
            room=room,
            distance=dist,
            collected_items=sorted(items),
        )

        # ----------------------------------------------------------
        # Item pickup
        # ----------------------------------------------------------

        room_item = map_graph.rooms[room].item
        if (
            room_item
            and room_item.name in required_items
            and room_item.name not in items
        ):
            items = items | {room_item.name}

            logger.debug(
                "Collected required item",
                room=room,
                item=room_item.name,
                total_collected=len(items),
            )

        # ----------------------------------------------------------
        # Victory / terminal condition
        # ----------------------------------------------------------

        if room_item and room_item.render_key == "villain":
            logger.debug(
                "Encountered villain",
                room=room,
                collected_items=sorted(items),
                missing_items=sorted(required_items - items),
            )

            if items >= required_items:
                logger.info(
                    "Optimal solution found",
                    moves=dist,
                    states_explored=explored_states,
                )
                return dist

            # Terminal failure: cannot encounter villain early
            continue

        # ----------------------------------------------------------
        # Expand neighbors
        # ----------------------------------------------------------

        for _, nxt in map_graph.neighbors(room).items():
            queue.append((nxt, items, dist + 1))

    # --------------------------------------------------------------
    # Failure
    # --------------------------------------------------------------

    logger.error(
        "Level is not solvable",
        states_explored=explored_states,
        visited_state_count=len(visited),
        required_items=sorted(required_items),
    )

    raise LevelValidationError("Level is not solvable")
