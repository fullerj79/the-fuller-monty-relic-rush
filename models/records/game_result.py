"""
models/records/game_result.py

Author: Jason Fuller

Game result record.

Responsibilities:
- Represent the immutable outcome of a completed game session
- Capture summary-level data suitable for persistence and analytics
- Provide safe serialization and rehydration helpers

Architectural role:
- Record model (persistence-friendly, immutable)
- Boundary object between domain logic and storage
- Consumed by repositories, scoring, and UI layers

Design notes:
- GameResult represents what happened, not how it happened
- Detailed runtime state belongs in GameState, not here
- Instances are append-only and never mutated
- Backwards compatible with historical records (display_name optional)

Logging:
- None (immutable record object)
"""

# ------------------------------------------------------------------
# Standard library imports
# ------------------------------------------------------------------

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional

# ------------------------------------------------------------------
# Domain imports
# ------------------------------------------------------------------

from models.domain.status import GameStatus


@dataclass(frozen=True)
class GameResult:
    """
    Immutable record of a completed game session.

    Structure:
    - user_email: stable user identifier
    - level_id: identifier of the level played
    - status: final GameStatus (COMPLETED or GAME_OVER)
    - score: final computed score
    - moves: total number of moves taken
    - items_collected: number of required items collected
    - finished_at: UTC timestamp of completion
    - snapshot: optional summary of final game state
    """

    user_email: str

    level_id: str

    status: GameStatus
    score: int

    moves: int
    items_collected: int

    finished_at: datetime

    snapshot: dict[str, Any] | None = None

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """
        Serialize this GameResult into a persistence-safe dictionary.

        Notes:
        - Enum values are stored as strings
        - datetime is stored as ISO-8601
        """
        return {
            "user_email": self.user_email,
            "level_id": self.level_id,
            "status": self.status.value,
            "score": self.score,
            "moves": self.moves,
            "items_collected": self.items_collected,
            "finished_at": self.finished_at.isoformat(),
            "snapshot": self.snapshot,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "GameResult":
        """
        Rehydrate a GameResult from a persisted dictionary.

        Backwards compatibility:
        - finished_at may already be datetime (defensive handling)
        """

        finished_at = data["finished_at"]
        if isinstance(finished_at, str):
            finished_at = datetime.fromisoformat(finished_at)

        return cls(
            user_email=data["user_email"],
            level_id=data["level_id"],
            status=GameStatus(data["status"]),
            score=data["score"],
            moves=data["moves"],
            items_collected=data["items_collected"],
            finished_at=finished_at,
            snapshot=data.get("snapshot"),
        )

    # ------------------------------------------------------------------
    # Derived helpers
    # ------------------------------------------------------------------

    @property
    def is_win(self) -> bool:
        """
        Indicate whether this result represents a completed win.
        """
        return self.status == GameStatus.COMPLETED

    @property
    def is_loss(self) -> bool:
        """
        Indicate whether this result represents a completed loss.
        """
        return self.status == GameStatus.GAME_OVER

