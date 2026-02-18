"""
models/records/serialization.py

Author: Jason Fuller

GameState serialization helpers.

Responsibilities:
- Serialize GameState into JSON-compatible dictionaries
- Deserialize GameState from persisted representations
- Bridge runtime domain objects and storage/UI layers

Architectural role:
- Record-layer utility
- Boundary between domain models and persistence formats
- Used by controllers, callbacks, and repositories

Design notes:
- Serialization is deterministic and reversible
- No validation or business logic is performed here
- Errors should surface to callers if data is malformed

Logging:
- None (pure transformation helpers)
"""

# ------------------------------------------------------------------
# Standard library imports
# ------------------------------------------------------------------
from datetime import datetime
from typing import Any

# ------------------------------------------------------------------
# Domain imports
# ------------------------------------------------------------------
from models.domain.game_state import GameState
from models.domain.player import Player
from models.domain.status import GameStatus


# ------------------------------------------------------------------
# Serialization
# ------------------------------------------------------------------

def gamestate_to_dict(state: GameState) -> dict[str, Any]:
    """
    Serialize a GameState into a JSON-compatible dictionary.

    Notes:
        - Sets are converted to lists
        - Enum values are stored as strings
        - datetimes are stored as ISO-8601 strings
    """
    return {
        "level_id": state.level_id,
        "player": {
            "location": state.player.location,
        },
        "visited_rooms": list(state.visited_rooms),
        "collected_items": list(state.collected_items),
        "move_count": state.move_count,
        "status": state.status.value,
        "message": state.message,
        "event_log": list(state.event_log),
        "encountered_villain": state.encountered_villain,
        "started_at": state.started_at.isoformat(),
        "updated_at": state.updated_at.isoformat(),
    }


# ------------------------------------------------------------------
# Deserialization
# ------------------------------------------------------------------

def gamestate_from_dict(data: dict[str, Any]) -> GameState:
    """
    Deserialize a GameState from a persisted dictionary.

    Assumptions:
        - Data was produced by gamestate_to_dict
        - Required keys are present
    """
    player_data = data["player"]

    player = Player(
        location=player_data["location"],
    )

    state = GameState(
        level_id=data["level_id"],
        player=player,
        visited_rooms=set(data.get("visited_rooms", [])),
        collected_items=set(data.get("collected_items", [])),
        move_count=data.get("move_count", 0),
        status=GameStatus(
            data.get("status", GameStatus.IN_PROGRESS.value)
        ),
        message=data.get("message"),
        event_log=list(data.get("event_log", [])),
        encountered_villain=data.get("encountered_villain", False),
        started_at=datetime.fromisoformat(data["started_at"]),
        updated_at=datetime.fromisoformat(data["updated_at"]),
    )

    # Reassert core invariant: current location is always visited
    state.visited_rooms.add(state.player.location)

    return state
