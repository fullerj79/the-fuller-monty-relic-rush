"""
Level factory and construction logic.

Author: Jason Fuller
Date: 2/1/26

This module defines LevelFactory, the single entry point for constructing
validated Level instances from external representations (e.g., database
documents, JSON files, or hard-coded test data).

Architectural role:
- Boundary between persistence formats and domain models
- Enforces validation and invariants at load time
- Produces fully-initialized, immutable Level instances
"""

from models.domain.level import Level
from models.domain.map_graph import MapGraph
from models.domain.room import Room
from models.domain.item import Relic, Villain
from models.domain.rules import StandardRules
from models.domain.difficulty import Difficulty
from models.behavior.validation import (
    validate_level_definition,
    compute_optimal_moves,
)


class LevelFactory:
    """
    Factory for constructing validated Level objects.

    Design notes:
    - All Level instances MUST be created through this factory.
    - Validation and solvability checks occur exactly once, at load time.
    - Returned Level objects are immutable and safe to share across sessions.
    """

    @staticmethod
    def from_definition(defn: dict) -> Level:
        """
        Construct a Level from a raw definition dictionary.

        Expected structure of defn:
        {
            "id": str,
            "name": str,
            "difficulty": "easy" | "medium" | "hard",
            "start_room": str,
            "rooms": {
                room_name: {
                    "exits": {direction: room_name},
                    "item": {
                        "type": "relic" | "villain",
                        "name": str
                    } | None
                }
            },
            "coords": {
                room_name: [x, y]
            },
            "rules": {
                "required_items": [str, ...]
            }
        }

        Raises:
        - LevelValidationError if the definition is invalid or unsolvable
        """
        # Structural validation (schema, references, connectivity)
        validate_level_definition(defn)

        # Construct rooms and items
        rooms: dict[str, Room] = {}
        for name, data in defn["rooms"].items():
            item = None
            item_def = data.get("item")

            if item_def:
                if item_def["type"] == "relic":
                    item = Relic(item_def["name"])
                elif item_def["type"] == "villain":
                    item = Villain(item_def["name"])
                else:
                    raise ValueError(f"Unknown item type: {item_def['type']}")

            rooms[name] = Room(
                name=name,
                exits=data.get("exits", {}),
                item=item,
            )

        map_graph = MapGraph(
            rooms=rooms,
            coords={k: tuple(v) for k, v in defn["coords"].items()},
        )

        required_items = set(defn["rules"]["required_items"])

        # Algorithmic validation + optimal solution computation
        optimal_moves = compute_optimal_moves(
            map_graph=map_graph,
            start_room=defn["start_room"],
            required_items=required_items,
        )

        difficulty = Difficulty(defn["difficulty"])

        return Level(
            id=defn["id"],
            name=defn["name"],
            difficulty=difficulty,
            start_room=defn["start_room"],
            map=map_graph,
            rules=StandardRules(required_items),
            visibility=difficulty.visibility_policy,
            scoring=difficulty.scoring_policy,
            optimal_moves=optimal_moves,
        )
