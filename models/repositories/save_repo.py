"""
Game save repository interfaces and implementations.

Author: Jason Fuller
Date: 2/1/26

This module defines the SaveRepository abstraction and provides
two concrete implementations:
- InMemorySaveRepository (tests / local dev)
- MongoSaveRepository (MongoDB persistence)

Architectural role:
- Repository layer (persistence boundary)
- Stores *active, resumable* game sessions only

Design decisions:
- Saves represent IN-PROGRESS runs only
- Exactly one active save per user is supported
- save_id is treated as a logical slot identifier (often == user_email)
- Saves are overwriteable (autosave model)
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import List, Optional

from models.records.game_save import GameSave
from models.records.serialization import gamestate_to_dict, gamestate_from_dict


# ============================================================================
# Repository interface
# ============================================================================

class SaveRepository(ABC):
    """
    Abstract repository interface for active game saves.

    Implementations:
    - InMemorySaveRepository
    - MongoSaveRepository

    This repository is responsible ONLY for:
    - in-progress sessions
    - resume / abandon behavior

    Completed games are handled by HistoryRepository.
    """

    @abstractmethod
    def upsert_active(self, game_save: GameSave) -> None:
        """
        Create or overwrite the user's active save.
        """
        raise NotImplementedError

    @abstractmethod
    def get_active(self, user_email: str) -> Optional[GameSave]:
        """
        Retrieve the user's active save, if any.
        """
        raise NotImplementedError

    @abstractmethod
    def delete_active(self, user_email: str) -> None:
        """
        Delete the user's active save (quit or finalize).
        """
        raise NotImplementedError


# ============================================================================
# In-memory implementation
# ============================================================================

class InMemorySaveRepository(SaveRepository):
    """
    In-memory SaveRepository implementation.

    Use cases:
    - Unit tests
    - Local development
    - Demo mode without persistence

    Implementation notes:
    - Keyed by user_email
    - Overwrites on autosave
    """

    def __init__(self) -> None:
        self._saves: dict[str, GameSave] = {}

    def upsert_active(self, game_save: GameSave) -> None:
        self._saves[game_save.user_email] = game_save

    def get_active(self, user_email: str) -> Optional[GameSave]:
        return self._saves.get(user_email)

    def delete_active(self, user_email: str) -> None:
        self._saves.pop(user_email, None)


# ============================================================================
# MongoDB implementation
# ============================================================================

class MongoSaveRepository(SaveRepository):
    """
    MongoDB implementation of SaveRepository.

    Notes:
    - MongoDB adds an internal '_id' field which is ignored here
    - GameState is serialized via models.records.serialization
    - Autosave is implemented via update_one(..., upsert=True)
    """

    def __init__(self, game_saves_collection) -> None:
        """
        Inject the MongoDB collection to keep this repository testable.
        """
        self._col = game_saves_collection

    def upsert_active(self, game_save: GameSave) -> None:
        """
        Create or overwrite the user's active save.
        """
        self._col.update_one(
            {"user_email": game_save.user_email},
            {
                "$set": {
                    "level_id": game_save.level_id,
                    "state": gamestate_to_dict(game_save.state),
                    "updated_at": datetime.now(timezone.utc),
                },
                "$setOnInsert": {
                    "created_at": game_save.created_at,
                },
            },
            upsert=True,
        )

    def get_active(self, user_email: str) -> Optional[GameSave]:
        """
        Retrieve the user's active save, if present.
        """
        doc = self._col.find_one({"user_email": user_email})
        if not doc:
            return None

        return GameSave(
            user_email=doc["user_email"],
            level_id=doc["level_id"],
            state=gamestate_from_dict(doc["state"]),
            created_at=doc.get("created_at"),
            updated_at=doc.get("updated_at"),
        )

    def delete_active(self, user_email: str) -> None:
        """
        Delete the user's active save.
        """
        self._col.delete_one({"user_email": user_email})
