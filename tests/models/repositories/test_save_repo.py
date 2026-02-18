"""
tests/models/repositories/test_save_repo.py

Author: Jason Fuller

SaveRepository tests.

Responsibilities:
- Validate upsert behavior
- Validate overwrite semantics
- Validate retrieval behavior
- Validate deletion behavior
- Ensure not-found handling is consistent

Architectural role:
- Repository layer test
- Guards persistence boundary for active game sessions
- Ensures serialization/deserialization integrity
- Protects overwrite semantics (one active save per user)

Design notes:
- Uses save_repo fixture to test both InMemory and Mongo implementations
- Tests shared repository contract, not implementation details
- Ensures idempotent delete behavior
"""

from models.domain.game_state import GameState
from models.records.game_save import GameSave


# ==========================================================
# Helpers
# ==========================================================

def _make_state(level_id: str = "level1"):
    """
    Create a minimal valid GameState for save tests.
    """
    return GameState.start(
        level_id=level_id,
        start_room="X",
    )


# ==========================================================
# Shared Repository Contract (InMemory + Mongo)
# ==========================================================

class TestSaveRepository:
    """
    Validates shared SaveRepository behavior across implementations.
    """

    def test_upsert_and_get(self, save_repo):
        """
        upsert_active should persist a save,
        and get_active should reconstruct it correctly.
        """
        state = _make_state()

        save = GameSave(
            user_email="x@test.com",
            level_id="level1",
            state=state,
        )

        save_repo.upsert_active(save)

        retrieved = save_repo.get_active("x@test.com")

        assert retrieved is not None
        assert retrieved.user_email == "x@test.com"
        assert retrieved.level_id == "level1"
        assert retrieved.state.level_id == "level1"

    def test_upsert_overwrites_existing(self, save_repo):
        """
        A second upsert for the same user should overwrite
        the previous active save.
        """
        state = _make_state()

        save1 = GameSave(
            user_email="a@test.com",
            level_id="level1",
            state=state,
        )

        save_repo.upsert_active(save1)

        save2 = GameSave(
            user_email="a@test.com",
            level_id="level2",
            state=state,
        )

        save_repo.upsert_active(save2)

        retrieved = save_repo.get_active("a@test.com")

        assert retrieved is not None
        assert retrieved.level_id == "level2"

    def test_delete_removes_save(self, save_repo):
        """
        delete_active should remove an existing save.
        """
        state = _make_state()

        save = GameSave(
            user_email="y@test.com",
            level_id="level1",
            state=state,
        )

        save_repo.upsert_active(save)

        assert save_repo.get_active("y@test.com") is not None

        save_repo.delete_active("y@test.com")

        assert save_repo.get_active("y@test.com") is None

    def test_delete_nonexistent_save_does_not_raise(self, save_repo):
        """
        delete_active should be idempotent and safe
        when no save exists.
        """
        save_repo.delete_active("ghost@test.com")

    def test_get_active_not_found_returns_none(self, save_repo):
        """
        get_active should return None when no save exists.
        """
        assert save_repo.get_active("missing@test.com") is None
