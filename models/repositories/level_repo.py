"""
Level repository interfaces and implementations.

Author: Jason Fuller
Date: 2/1/26

This module defines the LevelRepository abstraction and provides
concrete implementations for retrieving level definitions from
different persistence backends.

Architectural role:
- Repository layer (read-only configuration data)
- Supplies raw level definitions (dicts)
- Does NOT construct domain objects

Design decisions:
- Repositories return unvalidated dictionaries
- LevelFactory is the single authority for validation + construction
- Levels are treated as immutable configuration data
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable, Dict, Any, Optional


# ============================================================================
# Repository interface
# ============================================================================

class LevelRepository(ABC):
    """
    Abstract repository interface for level definitions.

    Implementations:
    - InMemoryLevelRepository
    - MongoLevelRepository

    Notes:
    - Repositories return raw level definitions (dicts)
    - Domain objects are constructed by LevelFactory
    - No mutation operations are supported (levels are static)
    """

    @abstractmethod
    def get(self, level_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a level definition by its unique identifier.
        """
        raise NotImplementedError

    @abstractmethod
    def list(self) -> Iterable[Dict[str, Any]]:
        """
        List all available level definitions.
        """
        raise NotImplementedError


# ============================================================================
# In-memory implementation
# ============================================================================

class InMemoryLevelRepository(LevelRepository):
    """
    In-memory level repository.

    Use cases:
    - Unit tests
    - Local development
    - Demo / offline modes

    Implementation notes:
    - Levels are keyed by id
    - Definitions are assumed to be valid dictionaries
    """

    def __init__(self, levels: Iterable[Dict[str, Any]]) -> None:
        self._levels = {lvl["id"]: lvl for lvl in levels}

    def get(self, level_id: str) -> Optional[Dict[str, Any]]:
        return self._levels.get(level_id)

    def list(self) -> Iterable[Dict[str, Any]]:
        return self._levels.values()


# ============================================================================
# MongoDB implementation
# ============================================================================

class MongoLevelRepository(LevelRepository):
    """
    MongoDB-backed implementation of LevelRepository.

    Notes:
    - Levels are assumed to be authored and validated upstream
    - MongoDB's internal '_id' field is stripped on read
    - Repository is read-only by design
    """

    def __init__(self, levels_collection) -> None:
        """
        Inject the MongoDB collection to keep this repository testable
        and decoupled from global state.
        """
        self._col = levels_collection

    def get(self, level_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a single level definition by id.
        """
        return self._col.find_one(
            {"id": level_id},
            {"_id": 0},  # strip Mongo internal id
        )

    def list(self) -> Iterable[Dict[str, Any]]:
        """
        List all level definitions.
        """
        return self._col.find({}, {"_id": 0})
