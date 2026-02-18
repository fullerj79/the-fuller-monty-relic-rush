"""
models/domain/game_state.py

Author: Jason Fuller

Mutable game session state.

Responsibilities:
- Represent the authoritative, mutable state of a single game session
- Track player progress, movement, and collected items
- Provide safe mutation helpers used by the game controller

Architectural role:
- Domain model (runtime/session state)
- Owned and mutated by the GameController
- Consumed by rules, scoring, UI projection, and persistence layers

Design notes:
- GameState is intentionally mutable
- Represents what has happened, not what is allowed
- Contains no static configuration, map structure, or rule logic
- Timestamp mutation is owned by the controller at persistence boundaries

Logging:
- DEBUG: state mutations and lifecycle events
"""

# ------------------------------------------------------------------
# Standard library imports
# ------------------------------------------------------------------
from dataclasses import dataclass, field
from datetime import datetime, timezone

# ------------------------------------------------------------------
# Local application imports
# ------------------------------------------------------------------
from models.domain.player import Player
from models.domain.status import GameStatus
from utils.logger import get_logger


logger = get_logger(__name__)


@dataclass
class GameState:
    """
    Represents the mutable state of a single game session.

    Structure:
    - level_id: identifier of the active level configuration
    - player: player entity and current location
    - visited_rooms: rooms entered so far (fog-of-war and analytics)
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
    - level_id never changes for the lifetime of this state
    """

    level_id: str
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

    # ------------------------------------------------------------------
    # State mutation helpers
    # ------------------------------------------------------------------

    def visit(self, room_name: str) -> None:
        """
        Record that the player has entered a room.

        Side effects:
        - Adds the room to visited_rooms

        Assumptions:
        - room_name is a valid room identifier for the active level
        - The caller ensures movement validity

        Notes:
        - Does not increment move_count
        - Does not update timestamps (controller-owned)
        """
        self.visited_rooms.add(room_name)

        logger.debug(
            "Player visited room",
            room=room_name,
            visited_room_count=len(self.visited_rooms),
        )

    # ------------------------------------------------------------------
    # Factory
    # ------------------------------------------------------------------

    @classmethod
    def start(cls, *, level_id: str, start_room: str) -> "GameState":
        """
        Create a new GameState for a freshly started session.

        Guarantees:
        - Player is initialized
        - Player starts in a valid room
        - visited_rooms contains the start room
        - level_id is bound immutably
        - counters and timestamps are initialized

        Args:
            level_id: Identifier of the level being played
            start_room: Room identifier where the player begins

        Returns:
            A fully-initialized GameState instance
        """
        logger.debug(
            "Initializing new GameState",
            level_id=level_id,
            start_room=start_room,
        )

        player = Player(location=start_room)

        state = cls(
            level_id=level_id,
            player=player,
        )

        state.visited_rooms.add(start_room)

        logger.info(
            "GameState initialized",
            level_id=level_id,
            start_room=start_room,
        )

        return state
