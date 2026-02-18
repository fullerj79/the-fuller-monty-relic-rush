"""
Game save repository interfaces and implementations.

Author: Jason Fuller

Architectural role:
- Repository layer (persistence boundary)
- Stores *active, resumable* game sessions only
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Optional

from models.records.game_save import GameSave
from models.records.serialization import gamestate_to_dict, gamestate_from_dict


# ============================================================================ #
# Repository interface
# ============================================================================ #

class SaveRepository(ABC):
    """
    Abstract repository interface for active game saves.
    """

    @abstractmethod
    def upsert_active(self, game_save: GameSave) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_active(self, user_email: str):
        raise NotImplementedError

    @abstractmethod
    def delete_active(self, user_email: str) -> None:
        raise NotImplementedError


# ============================================================================ #
# In-memory implementation
# ============================================================================ #

class InMemorySaveRepository(SaveRepository):
    """
    In-memory SaveRepository implementation.
    """

    def __init__(self) -> None:
        self._saves: dict[str, GameSave] = {}

    def upsert_active(self, game_save: GameSave) -> None:
        self._saves[game_save.user_email] = game_save

    def get_active(self, user_email: str):
        save = self._saves.get(user_email)
        if not save:
            return None

        return GameSave(
            user_email=save.user_email,
            level_id=save.level_id,
            state=gamestate_from_dict(save.state),
            created_at=save.created_at,
            updated_at=save.updated_at,
        )

    def delete_active(self, user_email: str) -> None:
        self._saves.pop(user_email, None)


# ============================================================================ #
# MongoDB implementation
# ============================================================================ #

class MongoSaveRepository(SaveRepository):
    """
    MongoDB implementation of SaveRepository.
    """

    def __init__(self, game_saves_collection) -> None:
        self._col = game_saves_collection


    def upsert_active(self, game_save: GameSave) -> None:
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


    def get_active(self, user_email: str):
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
        self._col.delete_one({"user_email": user_email})
