"""
models/repositories/history_repo.py

Author: Jason Fuller

Game history repository interfaces and implementations.

Responsibilities:
- Persist completed GameResult records (append-only)
- Query historical results by user or leaderboard ranking

Architectural role:
- Repository layer (persistence boundary)
- Owns storage and retrieval of completed game outcomes
- Does NOT manage active game sessions or GameState

Design notes:
- History is immutable once written
- Repositories return strongly-typed domain records
- Mongo implementation strips persistence-only fields (_id)

Logging:
- DEBUG: repository initialization, query execution, result counts
- INFO: persistence of completed game results
"""

from __future__ import annotations

# ------------------------------------------------------------------
# Standard library
# ------------------------------------------------------------------

from abc import ABC, abstractmethod

# ------------------------------------------------------------------
# Domain / records
# ------------------------------------------------------------------

from models.records.game_result import GameResult

# ------------------------------------------------------------------
# Logging
# ------------------------------------------------------------------

from utils.logger import get_logger, LogLevel

log = get_logger("models.repositories.history_repo")


# ------------------------------------------------------------------
# Repository interface
# ------------------------------------------------------------------

class HistoryRepository(ABC):
    """
    Abstract repository interface for completed game results.

    Implementations:
    - InMemoryHistoryRepository (tests / local)
    - MongoHistoryRepository (production)
    """

    @abstractmethod
    def add(self, result: GameResult) -> None:
        """
        Persist a completed game result (append-only).
        """
        raise NotImplementedError

    @abstractmethod
    def by_user(self, user_email: str) -> list[GameResult]:
        """
        Retrieve all completed results for a given user.
        """
        raise NotImplementedError

    @abstractmethod
    def top_scores(self, level_id: str, limit: int = 10) -> list[GameResult]:
        """
        Retrieve the top scores for a given level.
        """
        raise NotImplementedError


# ------------------------------------------------------------------
# In-memory implementation
# ------------------------------------------------------------------

class InMemoryHistoryRepository(HistoryRepository):
    """
    In-memory implementation of HistoryRepository.

    Use cases:
    - Unit tests
    - Local development
    - Demo mode without persistence
    """

    def __init__(self) -> None:
        self._results: list[GameResult] = []
        log.debug("Initialized InMemoryHistoryRepository")

    def add(self, result: GameResult) -> None:
        log.debug(
            "Recording game result (in-memory)",
            data={
                "user_email": result.user_email,
                "level_id": result.level_id,
                "score": result.score,
            },
        )
        self._results.append(result)

    def by_user(self, user_email: str) -> list[GameResult]:
        log.debug(
            "Fetching history for user (in-memory)",
            data={"user_email": user_email},
        )
        return [r for r in self._results if r.user_email == user_email]

    def top_scores(self, level_id: str, limit: int = 10) -> list[GameResult]:
        log.debug(
            "Fetching leaderboard (in-memory)",
            data={"level_id": level_id, "limit": limit},
        )
        return sorted(
            (r for r in self._results if r.level_id == level_id),
            key=lambda r: r.score,
            reverse=True,
        )[:limit]


# ------------------------------------------------------------------
# MongoDB implementation
# ------------------------------------------------------------------

class MongoHistoryRepository(HistoryRepository):
    """
    MongoDB-backed implementation of HistoryRepository.

    Notes:
    - MongoDB adds an internal '_id' field which is stripped
      before hydrating GameResult objects.
    - GameResult is stored as a serialized dictionary.
    """

    def __init__(self, game_results_collection) -> None:
        """
        Args:
            game_results_collection: Injected MongoDB collection
        """
        self._col = game_results_collection
        log.info("Initialized MongoHistoryRepository")

    def add(self, result: GameResult) -> None:
        log.info(
            "Persisting game result",
            data={
                "user_email": result.user_email,
                "level_id": result.level_id,
                "score": result.score,
            },
        )
        self._col.insert_one(result.to_dict())

    def by_user(self, user_email: str) -> list[GameResult]:
        log.debug("Querying user history", data={"user_email": user_email})

        cursor = self._col.find(
            {"user_email": user_email}
        ).sort("finished_at", -1)

        results: list[GameResult] = []
        for doc in cursor:
            doc.pop("_id", None)
            results.append(GameResult.from_dict(doc))

        log.debug(
            "User history retrieved",
            data={"user_email": user_email, "count": len(results)},
        )
        return results

    def top_scores(self, level_id: str, limit: int = 10) -> list[GameResult]:
        log.debug(
            "Querying leaderboard",
            data={"level_id": level_id, "limit": limit},
        )

        cursor = (
            self._col.find({"level_id": level_id})
            .sort("score", -1)
            .limit(limit)
        )

        results: list[GameResult] = []
        for doc in cursor:
            doc.pop("_id", None)
            results.append(GameResult.from_dict(doc))

        log.debug(
            "Leaderboard retrieved",
            data={"level_id": level_id, "count": len(results)},
        )
        return results
