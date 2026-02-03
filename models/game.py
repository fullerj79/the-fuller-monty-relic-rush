"""
models/game.py

Author: Jason Fuller
Date: 2026-01-25

Purpose:
    This module defines the *data layer* for the Avengers Stone Collector game
    in the MVC Dash application.

What this file contains:
    - The original console game ROOM data structure (ROOMS)
    - The list of collectible items derived from ROOMS (ITEMS)
    - Direction constants (DIRECTIONS)
    - A lightweight GameState dataclass used by the controller + UI

What this file does NOT contain:
    - UI / Dash layout code
    - Validation logic for movement or item pickup
    - Database persistence or saving/loading behavior (planned later)

MVC Role:
    Model (data + state)
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Any


ROOMS = {
    'Space Room': {
        'item': 'Blue Stone',
        'South': 'Reality Room',
        'East': 'Avengers Campus'
    },
    'Avengers Campus': {
        'item': '',
        'South': 'Power Room',
        'East': 'Mind Room',
        'West': 'Space Room'
    },
    'Mind Room': {
        'item': 'Yellow Stone',
        'South': 'Time Room',
        'West': 'Avengers Campus'
    },
    'Reality Room': {
        'item': 'Red Stone',
        'North': 'Space Room',
        'South': 'Soul Room',
        'East': 'Power Room'
    },
    'Power Room': {
        'item': 'Purple Stone',
        'North': 'Avengers Campus',
        'East': 'Time Room',
        'West': 'Reality Room'
    },
    'Time Room': {
        'item': 'Green Stone',
        'North': 'Mind Room',
        'South': 'Avengers Compound',
        'West': 'Power Room'
    },
    'Soul Room': {
        'item': 'Orange Stone',
        'North': 'Reality Room'
    },
    'Avengers Compound': {
        'item': 'Villain',
        'North': 'Time Room'
    }
}

DIRECTIONS = ["North", "South", "East", "West"]
VILLAIN_ROOM_ITEM = "Villain"

# Build ITEMS set from ROOMS (same concept as original)
ITEMS = {v for v in {v['item'] for _, v in ROOMS.items() if v} if v not in ("", VILLAIN_ROOM_ITEM)}


@dataclass
class GameState:
    """
    Minimal state needed to play the game in a web UI.
    """
    current_room: str = "Avengers Campus"
    inventory: List[str] = field(default_factory=list)
    status: str = "playing"  # playing | completed | game_over
    message: str = ""        # last message for UI feedback
    event_log: List[str] = field(default_factory=list)

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "GameState":
        """
        Convert JSON/dict store data back into a GameState object.
        """
        return GameState(
            current_room=data.get("current_room", "Avengers Campus"),
            inventory=list(data.get("inventory", [])),
            status=data.get("status", "playing"),
            message=data.get("message", ""),
            event_log=list(data.get("event_log", [])),
        )
