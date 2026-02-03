"""
Mutable game session state.

Author: Jason Fuller
Date: 2/1/26

This module defines GameState, the authoritative, mutable snapshot of a
single game session. GameState evolves over time in response to player
actions and is the primary object persisted when saving or restoring a
session.

Architectural role:
- Domain model (runtime/session state)
- Owned and mutated by the game controller
- Consumed by rules, scoring, UI projection, and persistence layers

GameState intentionally contains no static configuration, map structure,
or rule logic. It represents *what has happened*, not *what is allowed*.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from models.domain.player import Player
from models.domain.status import GameStatus


@dataclass
class GameState:
    """
    Represents the mutable state of a single game session.

    Structure:
    - player: player entity and current location
    - visited_rooms: rooms entered so far (used for fog-of-war and analytics)
    - collected_items: items collected during this session
    - move_count: number of movement actions taken
    - status: high-level game lifecycle state
    - message: last user-facing message emitted by rules or controller
    - event_log: append-only log of notable events
    - timestamps: session lifecycle metadata
    - encountered_villain: flag indicating villain encounter

    Invariants:
    - player.location is always a valid room identifier
    - visited_rooms always contains player.location
    - move_count is monotonic and never decreases
    - collected_items contains no duplicates
    - status transitions only via rules or controller logic

    Design notes:
    - GameState is intentionally mutable.
    - Each GameState instance belongs to exactly one game session.
    - GameState may be serialized/deserialized for persistence.

    This class does NOT:
    - define win/loss conditions
    - perform movement validation
    - calculate scores
    - render UI
    - mutate Level or MapGraph
    """

    player: Player

    visited_rooms: set[str] = field(default_factory=set)
    collected_items: set[str] = field(default_factory=set)
    move_count: int = 0

    status: GameStatus = GameStatus.IN_PROGRESS
    message: str | None = None
    event_log: list[str] = field(default_factory=list)

    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    encountered_villain: bool = False

    def visit(self, room_name: str) -> None:
        """
        Record that the player has entered a room.

        Side effects:
        - Adds the room to visited_rooms
        - Updates the updated_at timestamp

        Assumptions:
        - room_name is a valid room identifier for the active level
        - The caller ensures movement validity

        Notes:
        - This method does not increment move_count; that responsibility
          belongs to the controller to ensure consistent accounting.
        """
        self.visited_rooms.add(room_name)
        self.updated_at = datetime.now(timezone.utc)

    @classmethod
    def start(cls, *, start_room: str) -> "GameState":
        """
        Create a new GameState for a freshly started session.

        This factory guarantees that all GameState invariants are satisfied:
        - Player is initialized
        - Player starts in a valid room
        - visited_rooms contains the start room
        - counters and timestamps are initialized

        Args:
            start_room: Room identifier where the player begins

        Returns:
            A fully-initialized GameState instance
        """
        player = Player(location=start_room)

        state = cls(player=player)
        state.visited_rooms.add(start_room)

        return state
    