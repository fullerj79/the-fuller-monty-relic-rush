"""
tests/controllers/test_game_controller.py

Author: Jason Fuller

Consolidated GameController tests.

Responsibilities:
- Validate orchestration logic inside GameController
- Verify integration behavior with real repositories
- Validate finalization and leaderboard behavior
- Confirm edge-case handling and guard logic
- Validate pure unit behavior with mocked dependencies

Architectural role:
- Controller layer tests
- Covers both:
    - Integration tests (real repositories + seeded levels)
    - Unit tests (mocked repositories and level objects)

Design notes:
- Integration tests rely on seeded level definitions
- Uses repository fixtures defined in conftest.py
- Unit tests isolate GameController behavior using MagicMock
- Ensures controller remains persistence-agnostic

Test strategy:
- Happy-path scenarios
- Terminal and invalid-state guards
- Persistence side effects (save + history)
- Leaderboard sorting and limit enforcement
- Mock-driven behavior validation
"""

import pytest
from datetime import datetime, timezone
from unittest.mock import MagicMock

from controllers.game import GameController
from models.domain.game_state import GameState
from models.domain.status import GameStatus
from models.domain.item import Villain
from models.records.game_result import GameResult


# ==========================================================
# Helpers
# ==========================================================

def _get_any_level(level_repo):
    """
    Retrieve a real seeded level from the repository.

    Ensures integration tests operate against actual
    level definitions rather than mocks.
    """
    levels = list(level_repo.list())
    assert levels, "No seeded levels found"
    return levels[0]


# ==========================================================
# Integration Tests (Real Repositories)
# ==========================================================

class TestGameControllerIntegration:
    """
    Integration tests using real repository implementations.

    Validates end-to-end controller behavior including:
    - Save repository interaction
    - History persistence
    - Level loading
    """

    def test_restore_run_returns_none_if_no_active(self, game_controller):
        result = game_controller.restore_run(user_email="no@user.com")
        assert result is None

    def test_restart_run_deletes_existing_save(self, game_controller, level_repo, save_repo):
        level = _get_any_level(level_repo)

        state = game_controller.start_new_run(
            user_email="a@test.com",
            level_id=level.id,
        )

        assert save_repo.get_active("a@test.com") is not None

        new_state = game_controller.restart_run(
            user_email="a@test.com",
            level_id=level.id,
        )

        assert save_repo.get_active("a@test.com") is not None
        assert new_state.move_count == 0

    def test_abandon_run_removes_save(self, game_controller, level_repo, save_repo):
        level = _get_any_level(level_repo)

        game_controller.start_new_run(
            user_email="b@test.com",
            level_id=level.id,
        )

        assert save_repo.get_active("b@test.com") is not None

        game_controller.abandon_run(user_email="b@test.com")

        assert save_repo.get_active("b@test.com") is None

    def test_invalid_level_id_raises(self, game_controller):
        with pytest.raises(ValueError):
            game_controller.start_new_run(
                user_email="x@test.com",
                level_id="not_real",
            )

    def test_move_blocked_if_terminal(self, game_controller, level_repo):
        level = _get_any_level(level_repo)

        state = game_controller.start_new_run(
            user_email="term@test.com",
            level_id=level.id,
        )

        state.status = GameStatus.GAME_OVER

        new_state = game_controller.move(
            user_email="term@test.com",
            level_id=level.id,
            state=state,
            direction="north",
        )

        assert new_state.message == "Game already ended."

    def test_get_user_history_empty(self, game_controller):
        history = game_controller.get_user_history(user_email="none@test.com")
        assert isinstance(history, list)

    def test_get_leaderboard_returns_list(self, game_controller, level_repo):
        level = _get_any_level(level_repo)

        results = game_controller.get_leaderboard(
            level_id=level.id,
            limit=5,
        )

        assert isinstance(results, list)


# ==========================================================
# Edge / Internal Tests
# ==========================================================

class TestGameControllerEdges:
    """
    Tests internal guard logic and defensive behavior.
    """

    def test_require_level_invalid(self, game_controller):
        with pytest.raises(ValueError):
            game_controller._require_level("does_not_exist")

    def test_abandon_run_no_existing(self, game_controller):
        # Should not raise even if no save exists
        game_controller.abandon_run(user_email="test@test.com")
        assert True


# ==========================================================
# Finalization + Leaderboard Integration
# ==========================================================

class TestGameControllerFinalize:
    """
    Tests terminal-state behavior including:
    - Result persistence
    - Save cleanup
    - Leaderboard ranking logic
    """

    def test_finalize_persists_result_and_deletes_save(
        self,
        game_controller,
        level_repo,
        save_repo,
        history_repo,
    ):
        level = _get_any_level(level_repo)

        state = game_controller.start_new_run(
            user_email="finish@test.com",
            level_id=level.id,
        )

        state.collected_items = set(level.rules.required_items)

        villain_room = None
        neighbor_room_name = None
        direction_to_villain = None

        for room in level.map.rooms.values():
            if isinstance(room.item, Villain):
                villain_room = room
                break

        assert villain_room is not None

        for room in level.map.rooms.values():
            for direction, target in room.exits.items():
                if target == villain_room.name:
                    neighbor_room_name = room.name
                    direction_to_villain = direction
                    break
            if neighbor_room_name:
                break

        assert neighbor_room_name is not None

        state.player.location = neighbor_room_name

        new_state = game_controller.move(
            user_email="finish@test.com",
            level_id=level.id,
            state=state,
            direction=direction_to_villain,
        )

        assert new_state.status == GameStatus.COMPLETED
        assert save_repo.get_active("finish@test.com") is None

        results = history_repo.by_user("finish@test.com")
        assert len(results) == 1
        assert results[0].status == GameStatus.COMPLETED

    def test_leaderboard_limit_and_sort(
        self,
        game_controller,
        level_repo,
        history_repo,
    ):
        level = _get_any_level(level_repo)
        now = datetime.now(timezone.utc)

        history_repo.add(
            GameResult(
                user_email="a@test.com",
                level_id=level.id,
                status=GameStatus.COMPLETED,
                score=10,
                moves=5,
                items_collected=1,
                finished_at=now,
                snapshot={},
            )
        )

        history_repo.add(
            GameResult(
                user_email="b@test.com",
                level_id=level.id,
                status=GameStatus.COMPLETED,
                score=50,
                moves=3,
                items_collected=2,
                finished_at=now,
                snapshot={},
            )
        )

        results = game_controller.get_leaderboard(
            level_id=level.id,
            limit=1,
        )

        assert len(results) == 1
        assert results[0].score == 50


# ==========================================================
# Pure Unit Tests (Mocked Dependencies)
# ==========================================================

class TestGameControllerUnit:
    """
    Pure unit tests using mocked dependencies.

    Ensures controller behavior is correct in isolation
    from persistence and domain complexity.
    """

    @pytest.fixture
    def mock_level(self):
        level = MagicMock()
        level.id = "level_easy"
        level.start_room = "A"
        level.name = "Easy"
        level.map.rooms = {"A": MagicMock(exits={})}
        level.rules.check = MagicMock()
        level.scoring.calculate = MagicMock(return_value=123)
        level.optimal_moves = 5
        level.ui_projection.return_value = {}
        return level

    @pytest.fixture
    def controller(self, mock_level):
        level_repo = MagicMock()
        level_repo.get.return_value = mock_level

        save_repo = MagicMock()
        history_repo = MagicMock()

        return GameController(
            level_repo=level_repo,
            save_repo=save_repo,
            history_repo=history_repo,
        )

    def test_start_new_run(self, controller):
        state = controller.start_new_run(
            user_email="user@test.com",
            level_id="level_easy",
        )

        assert isinstance(state, GameState)
        assert state.player.location == "A"
        assert state.status == GameStatus.IN_PROGRESS

    def test_has_active_run(self, controller):
        controller._saves.get_active.return_value = object()
        assert controller.has_active_run(user_email="user@test.com") is True

        controller._saves.get_active.return_value = None
        assert controller.has_active_run(user_email="user@test.com") is False

    def test_finalize_on_win(self, controller):
        state = GameState.start(level_id="level_easy", start_room="A")
        state.status = GameStatus.COMPLETED

        controller._persist_or_finalize(
            user_email="user@test.com",
            level_id="level_easy",
            state=state,
        )

        controller._history.add.assert_called_once()
        controller._saves.delete_active.assert_called_once()
