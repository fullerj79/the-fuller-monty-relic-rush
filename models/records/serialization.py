"""
Game state serialization helpers.

Author: Jason Fuller
Date: 2/1/26

This module defines pure functions for serializing and deserializing
GameState objects to and from JSON-compatible dictionaries.

Architectural role:
- Persistence boundary
- Enables autosave, manual save, and restore
- Keeps domain models free of storage concerns

Serialization logic is intentionally centralized here to prevent
schema drift and duplicated persistence code across repositories.
"""

from datetime import datetime
from typing import Dict, Any

from models.domain.game_state import GameState
from models.domain.player import Player
from models.domain.status import GameStatus


# -------------------------
# Serialization
# -------------------------

def gamestate_to_dict(state: GameState) -> Dict[str, Any]:
    """
    Serialize a GameState into a JSON-compatible dictionary.

    Parameters:
    - state: GameState instance to serialize

    Returns:
    - dict suitable for persistence (Mongo, file, cache)

    Design notes:
    - Only runtime state is serialized.
    - Level configuration is referenced externally via level_id.
    - Datetimes are serialized as ISO-8601 strings.
    """
    return {
        "player": {
            "location": state.player.location,
            "inventory": list(state.player.inventory),
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


# -------------------------
# Deserialization
# -------------------------

def gamestate_from_dict(data: Dict[str, Any]) -> GameState:
    """
    Deserialize a GameState from a dictionary.

    Parameters:
    - data: dictionary produced by gamestate_to_dict

    Returns:
    - Reconstructed GameState instance

    Assumptions:
    - Input data has already been validated or originated from a trusted source
    - Level configuration is loaded separately

    Raises:
    - KeyError if required fields are missing
    - ValueError if enum or datetime parsing fails
    """
    player_data = data["player"]

    player = Player(
        location=player_data["location"],
        inventory=set(player_data.get("inventory", [])),
    )

    state = GameState(
        player=player,
        visited_rooms=set(data.get("visited_rooms", [])),
        collected_items=set(data.get("collected_items", [])),
        move_count=data.get("move_count", 0),
        status=GameStatus(data.get("status", GameStatus.IN_PROGRESS.value)),
        message=data.get("message"),
        event_log=list(data.get("event_log", [])),
        encountered_villain=data.get("encountered_villain", False),
        started_at=datetime.fromisoformat(data["started_at"]),
        updated_at=datetime.fromisoformat(data["updated_at"]),
    )

    return state
