"""
tests/models/repositories/test_history_repo.py

Author: Jason Fuller

HistoryRepository tests.

Responsibilities:
- Validate InMemoryHistoryRepository behavior
- Validate MongoHistoryRepository behavior
- Ensure sorting, filtering, and limit semantics
- Verify domain model reconstruction from persistence
- Confirm integration contract via history_repo fixture

Architectural role:
- Repository layer test
- Guards persistence boundary correctness
- Ensures leaderboard integrity and user history ordering

Design notes:
- Tests shared contract across implementations
- Protects domain object round-trip integrity
- Ensures backend-agnostic behavior consistency
"""

from datetime import datetime, timezone

from models.repositories.history_repo import (
    InMemoryHistoryRepository,
    MongoHistoryRepository,
)
from models.records.game_result import GameResult
from models.domain.status import GameStatus


# ==========================================================
# Helpers
# ==========================================================

def make_result(
    user: str,
    level: str,
    score: int,
    finished_at: datetime | None = None,
) -> GameResult:
    """
    Create a valid GameResult for repository testing.

    Notes:
    - Defaults finished_at to current UTC time
    - Uses COMPLETED status for leaderboard eligibility
    """
    return GameResult(
        user_email=user,
        level_id=level,
        status=GameStatus.COMPLETED,
        score=score,
        moves=5,
        items_collected=3,
        finished_at=finished_at or datetime.now(timezone.utc),
        snapshot={},
    )


# ==========================================================
# Shared Integration Tests (history_repo fixture)
# ==========================================================

class TestHistoryRepositoryIntegration:
    """
    Validates shared repository contract through fixture abstraction.
    """

    def test_add_and_query(self, history_repo):
        result = make_result("z@test.com", "level1", 123)

        history_repo.add(result)

        top = history_repo.top_scores("level1", limit=5)
        assert isinstance(top, list)

        user_history = history_repo.by_user("z@test.com")
        assert isinstance(user_history, list)


# ==========================================================
# InMemoryHistoryRepository
# ==========================================================

class TestInMemoryHistoryRepository:
    """
    Pure in-memory repository behavior tests.
    """

    def test_empty_results(self):
        repo = InMemoryHistoryRepository()

        assert repo.by_user("nobody@test.com") == []
        assert repo.top_scores("level1") == []

    def test_by_user_filters_correctly(self):
        repo = InMemoryHistoryRepository()

        repo.add(make_result("a@test.com", "level1", 10))
        repo.add(make_result("b@test.com", "level1", 20))
        repo.add(make_result("a@test.com", "level2", 30))

        results = repo.by_user("a@test.com")

        assert len(results) == 2
        assert all(r.user_email == "a@test.com" for r in results)

    def test_top_scores_sorted_and_limited(self):
        repo = InMemoryHistoryRepository()

        repo.add(make_result("a@test.com", "level1", 10))
        repo.add(make_result("b@test.com", "level1", 50))
        repo.add(make_result("c@test.com", "level1", 30))

        results = repo.top_scores("level1", limit=2)

        assert len(results) == 2
        assert results[0].score == 50
        assert results[1].score == 30

    def test_limit_larger_than_results(self):
        repo = InMemoryHistoryRepository()

        repo.add(make_result("a@test.com", "level1", 10))

        results = repo.top_scores("level1", limit=10)

        assert len(results) == 1


# ==========================================================
# MongoHistoryRepository
# ==========================================================

class TestMongoHistoryRepository:
    """
    MongoDB-backed repository tests.

    Ensures:
    - Correct persistence behavior
    - Proper sorting semantics
    - Model reconstruction from stored documents
    """

    def test_empty_results(self, isolated_history_collection):
        repo = MongoHistoryRepository(isolated_history_collection)

        assert repo.by_user("nobody@test.com") == []
        assert repo.top_scores("level1") == []

    def test_by_user_sorts_and_returns_models(self, isolated_history_collection):
        repo = MongoHistoryRepository(isolated_history_collection)

        repo.add(make_result("a@test.com", "level1", 10))
        repo.add(make_result("a@test.com", "level1", 20))

        results = repo.by_user("a@test.com")

        assert len(results) == 2
        assert results[0].finished_at >= results[1].finished_at
        assert all(isinstance(r, GameResult) for r in results)

    def test_top_scores_sorted_and_limited(self, isolated_history_collection):
        repo = MongoHistoryRepository(isolated_history_collection)

        repo.add(make_result("a@test.com", "level1", 10))
        repo.add(make_result("b@test.com", "level1", 50))
        repo.add(make_result("c@test.com", "level1", 30))
        repo.add(make_result("d@test.com", "level2", 999))  # Different level

        results = repo.top_scores("level1", limit=2)

        assert len(results) == 2
        assert results[0].score == 50
        assert results[1].score == 30

    def test_limit_larger_than_results(self, isolated_history_collection):
        repo = MongoHistoryRepository(isolated_history_collection)

        repo.add(make_result("a@test.com", "level1", 10))

        results = repo.top_scores("level1", limit=10)

        assert len(results) == 1
