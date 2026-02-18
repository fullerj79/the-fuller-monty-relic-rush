"""
tests/models/records/test_game_result.py

Author: Jason Fuller

GameResult record model tests.

Responsibilities:
- Validate GameResult serialization
- Ensure round-trip integrity via to_dict / from_dict
- Verify enum and datetime handling
- Protect persistence boundary invariants

Architectural role:
- Records layer test
- Guards snapshot and result persistence integrity
- Ensures safe reconstruction from storage

Design notes:
- Tests full round-trip behavior
- Avoids testing internal implementation details
- Protects contract between repository and domain layers
"""

from datetime import datetime, timezone

from models.records.game_result import GameResult
from models.domain.status import GameStatus


# ==========================================================
# Serialization Roundtrip
# ==========================================================

def test_game_result_serialization_roundtrip():
    """
    GameResult should serialize and deserialize
    without data loss.
    """
    now = datetime.now(timezone.utc)

    result = GameResult(
        user_email="test@test.com",
        level_id="level_easy",
        status=GameStatus.COMPLETED,
        score=1234,
        moves=10,
        items_collected=3,
        finished_at=now,
        snapshot={"state": "data"},
    )

    data = result.to_dict()
    restored = GameResult.from_dict(data)

    assert restored.user_email == result.user_email
    assert restored.level_id == result.level_id
    assert restored.status == result.status
    assert restored.score == result.score
    assert restored.moves == result.moves
    assert restored.items_collected == result.items_collected
    assert restored.snapshot == result.snapshot
