"""
tests/test_game_results_repo.py

Author: Jason Fuller
Date: 2/1/26

Integration tests for GameResult persistence and leaderboard ordering.
"""

from datetime import datetime, timezone

from models.domain.status import GameStatus
from models.records.game_result import GameResult

from db.mongo import game_results_collection
from models.repositories.history_repo import MongoHistoryRepository


def test_leaderboard_ordering():
    repo = MongoHistoryRepository(game_results_collection)

    repo.add(
        GameResult(
            user_email="a@test.com",
            level_id="level_1",
            score=100,
            moves=10,
            items_collected=6,
            status=GameStatus.COMPLETED,
            finished_at=datetime.now(timezone.utc),
        )
    )

    repo.add(
        GameResult(
            user_email="b@test.com",
            level_id="level_1",
            score=200,
            moves=8,
            items_collected=6,
            status=GameStatus.COMPLETED,
            finished_at=datetime.now(timezone.utc),
        )
    )

    top = repo.top_scores("level_1")

    assert len(top) == 2
    assert top[0].score == 200
    assert top[1].score == 100
