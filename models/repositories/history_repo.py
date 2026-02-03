"""
Game history repository interfaces and implementations.

Author: Jason Fuller
Date: 2/1/26

This module defines the HistoryRepository abstraction and provides
two concrete implementations:
- InMemoryHistoryRepository (local dev / tests)
- MongoHistoryRepository (production persistence)

Architectural role:
- Repository layer (persistence boundary)
- Stores completed, append-only GameResult records

Design notes:
- History is write-once and query-only
- It does not store "active saves" (that is SaveRepository's job)
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List

from models.records.game_result import GameResult


class HistoryRepository(ABC):
    """
    Abstract repository interface for completed game results.

    Implementations:
    - InMemoryHistoryRepository (tests/local)
    - MongoHistoryRepository (MongoDB)
    """

    @abstractmethod
    def add(self, result: GameResult) -> None:
        """
        Persist a completed result (append-only).
        """
        raise NotImplementedError

    @abstractmethod
    def by_user(self, user_email: str) -> List[GameResult]:
        """
        Retrieve all completed results for a given user.
        """
        raise NotImplementedError

    @abstractmethod
    def top_scores(self, level_id: str, limit: int = 10) -> List[GameResult]:
        """
        Retrieve the top scores for a given level.
        """
        raise NotImplementedError


class InMemoryHistoryRepository(HistoryRepository):
    """
    In-memory implementation of HistoryRepository.

    Use cases:
    - Unit tests
    - Local development
    - Demo mode without DB
    """

    def __init__(self) -> None:
        self._results: list[GameResult] = []

    def add(self, result: GameResult) -> None:
        self._results.append(result)

    def by_user(self, user_email: str) -> list[GameResult]:
        return [r for r in self._results if r.user_email == user_email]

    def top_scores(self, level_id: str, limit: int = 10) -> list[GameResult]:
        return sorted(
            (r for r in self._results if r.level_id == level_id),
            key=lambda r: r.score,
            reverse=True,
        )[:limit]


class MongoHistoryRepository(HistoryRepository):
    """
    MongoDB implementation of HistoryRepository.

    Notes:
    - Mongo adds an internal '_id' field that must be removed when
      hydrating strongly-typed records.
    - GameResult is stored as a simple dict (serialization boundary).
    """

    def __init__(self, game_results_collection) -> None:
        """
        Inject the collection to keep this class testable.
        """
        self._col = game_results_collection

    def add(self, result: GameResult) -> None:
        self._col.insert_one(result.to_dict())

    def by_user(self, user_email: str) -> list[GameResult]:
        cursor = self._col.find({"user_email": user_email}).sort("finished_at", -1)

        results: list[GameResult] = []
        for doc in cursor:
            doc.pop("_id", None)
            results.append(GameResult.from_dict(doc))
        return results

    def top_scores(self, level_id: str, limit: int = 10) -> list[GameResult]:
        cursor = (
            self._col.find({"level_id": level_id})
            .sort("score", -1)
            .limit(limit)
        )

        results: list[GameResult] = []
        for doc in cursor:
            doc.pop("_id", None)
            results.append(GameResult.from_dict(doc))
        return results
