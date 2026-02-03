"""
Game result record.

Author: Jason Fuller
Date: 2/1/26

This module defines GameResult, an immutable record representing the
outcome of a completed game session. GameResult captures summary-level
data suitable for persistence, leaderboards, analytics, and replay
inspection without embedding mutable runtime state.

Architectural role:
- Record model (persistence-friendly, immutable)
- Boundary object between domain logic and storage
- Consumed by repositories, scoring, and UI layers

GameResult represents *what happened*, not *how it happened*.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional

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

    Design notes:
    - GameResult is append-only and never mutated
    - It is safe to persist, cache, and replay
    - Detailed runtime state belongs in GameState, not here
    """

    user_email: str
    level_id: str

    status: GameStatus
    score: int

    moves: int
    items_collected: int

    finished_at: datetime

    snapshot: Optional[Dict[str, Any]] = None

    # ---------- Serialization ----------

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize this GameResult into a persistence-safe dictionary.

        Notes:
        - Enum values are stored as strings
        - datetime is stored as UTC ISO-8601
        """
        return {
            "user_email": self.user_email,
            "level_id": self.level_id,
            "status": self.status.value,
            "score": self.score,
            "moves": self.moves,
            "items_collected": self.items_collected,
            "finished_at": self.finished_at,
            "snapshot": self.snapshot,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GameResult":
        """
        Rehydrate a GameResult from a persisted dictionary.

        Parameters:
        - data: dictionary produced by to_dict()

        Returns:
        - GameResult instance
        """
        return cls(
            user_email=data["user_email"],
            level_id=data["level_id"],
            status=GameStatus(data["status"]),
            score=data["score"],
            moves=data["moves"],
            items_collected=data["items_collected"],
            finished_at=data["finished_at"],
            snapshot=data.get("snapshot"),
        )

    # ---------- Derived helpers ----------

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
