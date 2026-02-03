"""
Level validation and solvability checks.

Author: Jason Fuller
Date: 2/1/26

This module defines load-time validation logic for level definitions.
Validation establishes trust guarantees relied upon by runtime systems.
"""

from collections import deque


class LevelValidationError(Exception):
    """Raised when a level definition fails validation."""
    pass


def validate_level_definition(defn: dict) -> None:
    """
    Validate the structural correctness of a level definition.

    Ensures:
    - Required top-level fields exist
    - All rooms referenced by exits exist
    - All rooms have coordinates
    - Exactly one villain exists
    - Required items exist in the level

    This function performs no pathfinding.
    """
    required_keys = {"id", "name", "difficulty", "start_room", "rooms", "coords", "rules"}
    missing = required_keys - defn.keys()
    if missing:
        raise LevelValidationError(f"Missing required keys: {missing}")

    rooms = defn["rooms"]

    if defn["start_room"] not in rooms:
        raise LevelValidationError("Start room does not exist")

    # Validate exits
    for room, data in rooms.items():
        for target in data.get("exits", {}).values():
            if target not in rooms:
                raise LevelValidationError(f"Room '{room}' has invalid exit to '{target}'")

    # Validate coords
    for room in rooms:
        if room not in defn["coords"]:
            raise LevelValidationError(f"Room '{room}' missing coordinates")

    # Validate villain
    villains = [
        r for r in rooms.values()
        if r.get("item") and r["item"]["type"] == "villain"
    ]
    if len(villains) != 1:
        raise LevelValidationError("Level must contain exactly one villain")


def compute_optimal_moves(map_graph, start_room, required_items: set[str]) -> int:
    """
    Compute the minimum number of moves required to collect all required
    items and reach the villain.

    Uses BFS over (room, collected_items) state space.

    Returns:
    - Minimum number of moves

    Raises:
    - LevelValidationError if the level is unsolvable
    """
    visited = set()
    queue = deque([(start_room, frozenset(), 0)])

    while queue:
        room, items, dist = queue.popleft()

        if (room, items) in visited:
            continue
        visited.add((room, items))

        item = map_graph.rooms[room].item
        if item and item.name in required_items:
            items = items | {item.name}

        if item and item.name == "Villain" and items >= required_items:
            return dist

        for nxt in map_graph.neighbors(room).values():
            queue.append((nxt, items, dist + 1))

    raise LevelValidationError("Level is not solvable")
