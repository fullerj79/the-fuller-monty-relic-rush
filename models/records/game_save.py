"""
Game save snapshot model.

Author: Jason Fuller
Date: 2/1/26

Represents a resumable snapshot of an in-progress game session.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from models.domain.game_state import GameState


@dataclass
class GameSave:
    """
    Represents the active, resumable game session for a user.

    Structure:
    - user_email: unique user identifier (acts as save identity)
    - level_id: identifier of the level being played
    - state: snapshot of the current GameState
    - created_at: timestamp when the session began
    - updated_at: timestamp of the most recent autosave

    Design notes:
    - There is exactly ONE active GameSave per user.
    - Active saves are overwritten automatically.
    - Completed/failed games are recorded separately as GameResult.
    - Persistence and lifecycle are handled by repositories/controllers.
    """

    user_email: str
    level_id: str
    state: GameState

    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
