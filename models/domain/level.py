"""
models/domain/level.py

Author: Jason Fuller

Level composition and configuration.

Responsibilities:
- Represent an immutable, fully-validated level configuration
- Encapsulate static map, rules, visibility, and scoring behavior
- Provide UI-safe projections derived from GameState

Architectural role:
- Domain model (static configuration)
- Constructed once at load time
- Shared safely across multiple game sessions
- Consumed by controllers, UI projection, scoring, and validation logic

Logging:
- DEBUG: UI projection generation and visibility decisions
"""

# ------------------------------------------------------------------
# Standard library imports
# ------------------------------------------------------------------
from dataclasses import dataclass

# ------------------------------------------------------------------
# Domain imports
# ------------------------------------------------------------------
from models.domain.map_graph import MapGraph
from models.domain.rules import LevelRules
from models.domain.difficulty import Difficulty
from models.domain.scoring import ScoreStrategy
from models.behavior.visibility import VisibilityPolicy

# ------------------------------------------------------------------
# Local application imports
# ------------------------------------------------------------------
from utils.logger import get_logger


logger = get_logger(__name__)


@dataclass(frozen=True)
class Level:
    """
    Represents a single playable, immutable level definition.
    """

    id: str
    name: str
    difficulty: Difficulty
    start_room: str

    map: MapGraph
    rules: LevelRules
    visibility: VisibilityPolicy
    scoring: ScoreStrategy

    optimal_moves: int | None = None

    # ------------------------------------------------------------------
    # UI projection
    # ------------------------------------------------------------------

    def ui_projection(self, state) -> dict:
        """
        Produce a UI-safe projection of this level for the given game state.
        """
        logger.debug(
            "Generating level UI projection",
            level_id=self.id,
            player_room=state.player.location,
            visited_rooms=len(state.visited_rooms),
            collected_items=len(state.collected_items),
        )

        visibility = self.visibility.project(self, state)

        rooms: dict[str, dict] = {}
        max_x = 0
        max_y = 0

        for room_name, room in self.map.rooms.items():
            x, y = self.map.coords[room_name]
            max_x = max(max_x, x)
            max_y = max(max_y, y)

            # ----------------------------------------------------------
            # Fog-of-war handling
            # ----------------------------------------------------------
            if not visibility.can_render_room(room_name):
                rooms[room_name] = {
                    "x": x,
                    "y": y,
                    "render": "hidden",
                }
                continue

            # ----------------------------------------------------------
            # Player rendering
            # ----------------------------------------------------------
            if room_name == state.player.location:
                render = "player"

            # ----------------------------------------------------------
            # Item-based rendering
            # ----------------------------------------------------------
            elif room.item:
                if room.item.render_key == "villain":
                    render = (
                        "villain"
                        if visibility.show_villain
                        else "empty"
                    )

                elif room.item.render_key == "relic":
                    render = (
                        "relic"
                        if visibility.show_items
                        and room.item.name not in state.collected_items
                        else "empty"
                    )

                else:
                    render = "empty"

            else:
                render = "empty"

            rooms[room_name] = {
                "x": x,
                "y": y,
                "render": render,
            }

        projection = {
            "player_room": state.player.location,
            "grid": {
                "width": max_x + 1,
                "height": max_y + 1,
            },
            "rooms": rooms,
        }

        logger.debug(
            "Level UI projection generated",
            grid=projection["grid"],
            visible_rooms=sum(
                1 for r in rooms.values() if r["render"] != "hidden"
            ),
        )

        return projection
