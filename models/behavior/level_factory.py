"""
models/behavior/level_factory.py

Author: Jason Fuller

Level factory and construction logic.

Responsibilities:
- Validate level definitions
- Construct Room, MapGraph, and Level domain objects
- Compute solvability and optimal move counts
- Resolve difficulty-dependent policies and strategies

Logging:
- DEBUG: construction steps, branching decisions
- INFO: major construction milestones
- WARN: invalid but recoverable inputs (none expected)
- ERROR: invalid definitions or unknown item types
"""

# ------------------------------------------------------------------
# Local application imports
# ------------------------------------------------------------------
from models.behavior.validation import (
    compute_optimal_moves,
    validate_level_definition,
)
from models.domain.difficulty import Difficulty
from models.domain.item import Relic, Villain
from models.domain.level import Level
from models.domain.map_graph import MapGraph
from models.domain.room import Room
from models.domain.rules import StandardRules
from utils.logger import get_logger


logger = get_logger(__name__)


class LevelFactory:
    """
    Factory for constructing validated, immutable Level objects.
    """

    @staticmethod
    def from_definition(defn: dict) -> Level:
        logger.debug(
            "Starting level construction",
            level_id=defn.get("id"),
            name=defn.get("name"),
        )

        # ------------------------------------------------------------
        # Validation
        # ------------------------------------------------------------
        logger.debug("Validating level definition")
        validate_level_definition(defn)

        # ------------------------------------------------------------
        # Rooms + items
        # ------------------------------------------------------------
        rooms: dict[str, Room] = {}

        for room_name, room_def in defn["rooms"].items():
            logger.debug(
                "Constructing room",
                room=room_name,
            )

            item = None
            item_def = room_def.get("item")

            if item_def:
                logger.debug(
                    "Room contains item",
                    room=room_name,
                    item_type=item_def["type"],
                    item_name=item_def.get("name"),
                )

                match item_def["type"]:
                    case "relic":
                        item = Relic(item_def["name"])
                    case "villain":
                        item = Villain(item_def["name"])
                    case _:
                        logger.error(
                            "Unknown item type",
                            room=room_name,
                            item_type=item_def["type"],
                        )
                        raise ValueError(
                            f"Unknown item type: {item_def['type']}"
                        )

            rooms[room_name] = Room(
                name=room_name,
                exits=room_def.get("exits", {}),
                item=item,
            )

        # ------------------------------------------------------------
        # Map graph
        # ------------------------------------------------------------
        logger.debug("Constructing MapGraph")

        map_graph = MapGraph(
            rooms=rooms,
            coords={k: tuple(v) for k, v in defn["coords"].items()},
        )

        # ------------------------------------------------------------
        # Rules + solvability
        # ------------------------------------------------------------
        required_items = set(defn["rules"]["required_items"])

        logger.info(
            "Required items resolved",
            items=sorted(required_items),
        )

        optimal_moves = compute_optimal_moves(
            map_graph=map_graph,
            start_room=defn["start_room"],
            required_items=required_items,
        )

        logger.info(
            "Optimal moves computed",
            optimal_moves=optimal_moves,
        )

        # ------------------------------------------------------------
        # Difficulty → policies & strategies
        # ------------------------------------------------------------
        difficulty = Difficulty(defn["difficulty"])

        logger.debug(
            "Difficulty resolved",
            difficulty=difficulty.value,
        )

        visibility_policy = difficulty.visibility_policy
        scoring_strategy = difficulty.scoring_strategy
        scoring_policy = difficulty.scoring_policy

        logger.debug(
            "Difficulty components resolved",
            visibility_policy=visibility_policy.__class__.__name__,
            scoring_strategy=scoring_strategy.__class__.__name__,
            scoring_policy=scoring_policy.__class__.__name__,
        )

        # ------------------------------------------------------------
        # Final Level
        # ------------------------------------------------------------
        level = Level(
            id=defn["id"],
            name=defn["name"],
            difficulty=difficulty,
            start_room=defn["start_room"],
            map=map_graph,
            rules=StandardRules(required_items),
            visibility=visibility_policy,
            scoring=scoring_strategy,
            optimal_moves=optimal_moves,
        )

        logger.info(
            "Level constructed successfully",
            level_id=level.id,
            difficulty=difficulty.value,
            scoring_strategy=scoring_strategy.__class__.__name__,
        )

        return level
