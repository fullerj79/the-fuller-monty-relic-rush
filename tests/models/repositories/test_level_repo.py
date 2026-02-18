"""
tests/models/repositories/test_level_repo.py

Author: Jason Fuller

LevelRepository tests.

Responsibilities:
- Validate InMemoryLevelRepository behavior
- Validate MongoLevelRepository behavior
- Ensure cache correctness
- Ensure not-found semantics
- Ensure list() contract returns domain models

Architectural role:
- Repository layer test
- Guards persistence boundary for level definitions
- Ensures caching layer integrity
- Protects domain reconstruction behavior

Design notes:
- Tests shared contract via level_repo fixture
- Verifies cache identity semantics (object reuse)
- Ensures consistent behavior across implementations
"""

from models.repositories.level_repo import (
    InMemoryLevelRepository,
    MongoLevelRepository,
)
from models.domain.level import Level


# ==========================================================
# Shared Behavior (Real level_repo fixture)
# ==========================================================

class TestLevelRepositoryIntegration:
    """
    Validates shared repository contract via level_repo fixture.
    """

    def test_list_returns_levels(self, level_repo):
        levels = list(level_repo.list())

        assert isinstance(levels, list)
        assert len(levels) > 0
        assert isinstance(levels[0], Level)

    def test_get_unknown_returns_none(self, level_repo):
        result = level_repo.get("not_real")
        assert result is None

    def test_cache_hit(self, level_repo):
        """
        Repeated get() calls for the same level
        should return the identical object (cache).
        """
        level = list(level_repo.list())[0]

        first = level_repo.get(level.id)
        second = level_repo.get(level.id)

        assert first is second


# ==========================================================
# InMemoryLevelRepository
# ==========================================================

class TestInMemoryLevelRepository:
    """
    Pure in-memory repository behavior tests.
    """

    def test_get_not_found(self):
        repo = InMemoryLevelRepository([])
        assert repo.get("nope") is None

    def test_list_returns_domain_models(self, sample_level_definition):
        repo = InMemoryLevelRepository([sample_level_definition])

        levels = list(repo.list())

        assert len(levels) == 1
        assert isinstance(levels[0], Level)


# ==========================================================
# MongoLevelRepository
# ==========================================================

class TestMongoLevelRepository:
    """
    MongoDB-backed repository tests.

    Ensures:
    - Proper reconstruction of Level domain models
    - Cache behavior matches in-memory implementation
    - Not-found behavior is consistent
    """

    def test_get_not_found(self, isolated_level_collection):
        repo = MongoLevelRepository(isolated_level_collection)
        assert repo.get("nope") is None

    def test_cache_hit(self, isolated_level_collection, sample_level_definition):
        isolated_level_collection.insert_one(sample_level_definition)

        repo = MongoLevelRepository(isolated_level_collection)

        level1 = repo.get(sample_level_definition["id"])
        level2 = repo.get(sample_level_definition["id"])

        # Same object = cache used
        assert level1 is level2

    def test_list_uses_cache(self, isolated_level_collection, sample_level_definition):
        isolated_level_collection.insert_one(sample_level_definition)

        repo = MongoLevelRepository(isolated_level_collection)

        levels1 = list(repo.list())
        levels2 = list(repo.list())

        # Cached object reused
        assert levels1[0] is levels2[0]
