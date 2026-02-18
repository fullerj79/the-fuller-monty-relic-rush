"""
models/repositories/level_repo.py

Author: Jason Fuller

Level repository interfaces and implementations.

Responsibilities:
- Load level definitions from persistence or memory
- Construct immutable Level domain objects via LevelFactory
- Supply validated, ready-to-use Level instances to controllers

Architectural role:
- Repository layer (read-only configuration data)
- Boundary between persistence formats and domain models
- Does NOT own gameplay state or mutation logic

Design notes:
- Levels are immutable once constructed
- Repository is read-only by design
- Level validation occurs exactly once per process
- Mongo-backed repository caches constructed levels in memory

Logging:
- DEBUG: repository initialization, cache hits
- INFO: successful level construction and caching
"""

from __future__ import annotations

# ------------------------------------------------------------------
# Standard library
# ------------------------------------------------------------------

from abc import ABC, abstractmethod
from typing import Iterable, Any

# ------------------------------------------------------------------
# Domain / behavior
# ------------------------------------------------------------------

from models.domain.level import Level
from models.behavior.level_factory import LevelFactory

# ------------------------------------------------------------------
# Logging
# ------------------------------------------------------------------

from utils.logger import get_logger

log = get_logger("models.repositories.level_repo")


# ------------------------------------------------------------------
# Repository interface
# ------------------------------------------------------------------

class LevelRepository(ABC):
    """
    Abstract repository interface for level definitions.
    """

    @abstractmethod
    def get(self, level_id: str) -> Level | None:
        """
        Retrieve a single level by id.
        """
        raise NotImplementedError

    @abstractmethod
    def list(self) -> Iterable[Level]:
        """
        Retrieve all available levels.
        """
        raise NotImplementedError


# ------------------------------------------------------------------
# In-memory implementation
# ------------------------------------------------------------------

class InMemoryLevelRepository(LevelRepository):
    """
    In-memory level repository.

    Intended for:
    - Unit tests
    - Local development
    - Seeded configuration
    """

    def __init__(self, level_defs: Iterable[dict[str, Any]]) -> None:
        log.info("Initializing InMemoryLevelRepository")

        self._levels: dict[str, Level] = {}

        for defn in level_defs:
            level_id = defn.get("id")
            log.debug(
                "Constructing level from definition (in-memory)",
                level_id=level_id,
            )
            self._levels[level_id] = LevelFactory.from_definition(defn)

        log.info(
            "InMemoryLevelRepository initialized",
            level_count=len(self._levels),
        )

    def get(self, level_id: str) -> Level | None:
        log.debug(
            "Resolving level (in-memory)",
            level_id=level_id,
        )
        return self._levels.get(level_id)

    def list(self) -> Iterable[Level]:
        log.debug("Listing all levels (in-memory)")
        return self._levels.values()


# ------------------------------------------------------------------
# MongoDB implementation
# ------------------------------------------------------------------

class MongoLevelRepository(LevelRepository):
    """
    MongoDB-backed implementation of LevelRepository.

    Production behavior:
    - Level definitions are fetched once per level_id
    - Levels are validated and constructed exactly once
    - Constructed Level objects are cached in-process
    - Subsequent access is zero-I/O and zero-validation

    Notes:
    - MongoDB documents are treated as immutable configuration
    - Internal MongoDB fields (_id) are excluded at query time
    """

    def __init__(self, levels_collection) -> None:
        self._col = levels_collection
        self._cache: dict[str, Level] = {}

        log.info("Initialized MongoLevelRepository")

    def get(self, level_id: str) -> Level | None:
        # ----------------------------------------------------------
        # Fast path: in-memory cache
        # ----------------------------------------------------------

        cached = self._cache.get(level_id)
        if cached:
            log.debug(
                "Level resolved from cache",
                level_id=level_id,
            )
            return cached

        # ----------------------------------------------------------
        # Slow path: fetch + construct (once)
        # ----------------------------------------------------------

        log.debug(
            "Fetching level from MongoDB",
            level_id=level_id,
        )

        doc = self._col.find_one({"id": level_id}, {"_id": 0})
        if not doc:
            log.warn(
                "Level not found in MongoDB",
                level_id=level_id,
            )
            return None

        level = LevelFactory.from_definition(doc)

        self._cache[level_id] = level

        log.info(
            "Level constructed and cached from MongoDB",
            level_id=level_id,
        )

        return level

    def list(self) -> Iterable[Level]:
        log.debug("Listing all levels from MongoDB")

        for doc in self._col.find({}, {"_id": 0}):
            level_id = doc.get("id")

            cached = self._cache.get(level_id)
            if cached:
                yield cached
                continue

            log.debug(
                "Constructing and caching level from MongoDB",
                level_id=level_id,
            )

            level = LevelFactory.from_definition(doc)
            self._cache[level_id] = level
            yield level
