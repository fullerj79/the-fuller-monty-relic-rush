"""
controllers/game.py

Author: Jason Fuller
Date: 2026-01-25

Purpose:
    This module defines the *gameplay logic layer*

What this file contains:
    - GameController class responsible for:
        * starting a new game
        * validating moves (North/South/East/West)
        * validating item pickup (stones)
        * determining win/lose conditions in the villain room
    - Helper methods that keep the UI simple (exits, current item, etc.)

What this file does NOT contain:
    - Dash callback definitions
    - Dash UI layout components
    - Saving/loading, pause, timers, scoring, or database-driven features (planned later)
"""

from __future__ import annotations
from typing import Dict, Any, List, Optional

from models.game import GameState, ROOMS, ITEMS, DIRECTIONS, VILLAIN_ROOM_ITEM


class GameController:
    """
    Controller for the Avengers Stone Collector game.

    Owns:
        - move validation
        - pickup validation
        - win/lose detection
        - event log updates
    """

    def __init__(self, game_model: GameState):
        """
        Args:
            game_model: The model layer object responsible for DB reads/writes.
        """
        self.game_model = game_model

    def new_game(self) -> GameState:
        """
        Start a new game.
        """
        return GameState(
            current_room="Avengers Campus",
            inventory=[],
            status="playing",
            message="New game started.",
            event_log=["New game started."]
        )


    def get_room(self, room_name: str) -> Dict[str, Any]:
        return ROOMS.get(room_name, {})


    def get_exits(self, room_name: str) -> List[str]:
        room = self.get_room(room_name)
        return [d for d in DIRECTIONS if d in room]


    def room_item(self, room_name: str) -> str:
        room = self.get_room(room_name)
        return room.get("item", "")


    def did_win(self, state: GameState) -> bool:
        """
        Player wins if they have collected all stones.
        """
        return len(state.inventory) >= len(ITEMS)


    def move(self, state: GameState, direction: str) -> GameState:
        """
        Attempt to move the player in a direction.
        """
        if state.status != "playing":
            state.message = "Game already ended."
            return state

        if direction not in DIRECTIONS:
            state.message = "Invalid direction."
            return state

        room = self.get_room(state.current_room)

        # Direction is valid, but may not exist from this room
        if direction not in room:
            state.message = "You bumped into a wall."
            state.event_log = (state.event_log or [])[-19:] + ["You bumped into a wall."]
            return state

        # Move to next room
        next_room = room[direction]
        state.current_room = next_room
        state.message = ""
        state.event_log = (state.event_log or [])[-19:] + [f"Moved {direction} to {next_room}."]

        # Check for villain
        item = self.room_item(next_room)
        if item == VILLAIN_ROOM_ITEM:
            if self.did_win(state):
                state.status = "completed"
                state.message = "You found Thanos... YOU WIN!"
                state.event_log = (state.event_log or [])[-19:] + ["You found Thanos with all stones. YOU WIN!"]
            else:
                state.status = "game_over"
                state.message = "You found Thanos too soon. GAME OVER!"
                state.event_log = (state.event_log or [])[-19:] + ["You found Thanos without all stones. GAME OVER!"]

        return state


    def can_pickup(self, state: GameState) -> Optional[str]:
        """
        Return the item name if the player is allowed to pick it up, else None.
        """
        if state.status != "playing":
            return None

        item = self.room_item(state.current_room)
        if not item or item == VILLAIN_ROOM_ITEM:
            return None

        if item in state.inventory:
            return None

        return item


    def pickup(self, state: GameState) -> GameState:
        """
        Attempt to pick up item in the current room.
        """
        if state.status != "playing":
            state.message = "Game already ended."
            return state

        item = self.can_pickup(state)
        if not item:
            state.message = "Nothing to pick up."
            return state

        state.inventory.append(item)
        state.message = f"Collected {item}!"
        state.event_log = (state.event_log or [])[-19:] + [f"Collected {item}!"]

        return state
