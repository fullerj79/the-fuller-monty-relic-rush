"""
models/records/game_save.py

Author: Jason Fuller

Game save snapshot model.

Represents a resumable snapshot of an in-progress game session.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass(frozen=True)
class GameSave:
    """
    Represents the active, resumable game session for a user.

    Structure:
    - user_email: unique user identifier (acts as save identity)
    - level_id: identifier of the level being played
    - state: serialized snapshot of GameState (immutable dict)
    - created_at: timestamp when the session began
    - updated_at: timestamp of the most recent autosave

    Design notes:
    - This object represents a persistence snapshot, not live state
    - state must be produced via gamestate_to_dict(...)
    """

    user_email: str
    level_id: str
    state: dict[str, Any]

    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
