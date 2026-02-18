"""
controllers/game.py

Author: Jason Fuller

Game controller.

Responsibilities:
- Orchestrate gameplay at the application boundary (UI <-> domain <-> persistence)
- Own the game session lifecycle (start, restore, act, autosave, finalize)
- Expose UI-friendly helper methods to keep callbacks thin

Logging:
- DEBUG: state transitions, branching decisions, persistence actions
- INFO: session lifecycle milestones, scoring, finalization
- WARN: invalid or blocked actions, abandoned sessions
- ERROR: corrupted state or unknown level identifiers
"""

from __future__ import annotations

# ------------------------------------------------------------------
# Standard library imports
# ------------------------------------------------------------------
from datetime import datetime, timezone
from typing import Optional

# ------------------------------------------------------------------
# Domain models
# ------------------------------------------------------------------
from models.domain.game_state import GameState
from models.domain.scoring import ScoreStrategy

# ------------------------------------------------------------------
# Persistence records
# ------------------------------------------------------------------
from models.records.game_result import GameResult
from models.records.game_save import GameSave
from models.records.serialization import gamestate_to_dict

# ------------------------------------------------------------------
# Repositories
# ------------------------------------------------------------------
from models.repositories.history_repo import HistoryRepository
from models.repositories.level_repo import LevelRepository
from models.repositories.save_repo import SaveRepository

# ------------------------------------------------------------------
# Local application imports
# ------------------------------------------------------------------
from utils.logger import get_logger


logger = get_logger(__name__)


class GameController:
    """
    Application controller for a single user's gameplay session.
    """

    def __init__(
        self,
        *,
        level_repo: LevelRepository,
        save_repo: SaveRepository,
        history_repo: HistoryRepository,
    ) -> None:
        logger.info("Initializing GameController")

        self._levels = level_repo
        self._saves = save_repo
        self._history = history_repo

    # ------------------------------------------------------------------
    # Session lifecycle
    # ------------------------------------------------------------------

    def has_active_run(self, *, user_email: str) -> bool:
        logger.debug(
            "Checking for active run",
            user_email=user_email,
        )

        active = self._saves.get_active(user_email) is not None

        logger.debug(
            "Active run evaluated",
            active=active,
        )

        return active

    def restore_run(self, *, user_email: str) -> Optional[GameSave]:
        logger.info(
            "Restoring active run",
            user_email=user_email,
        )

        save = self._saves.get_active(user_email)

        logger.debug(
            "Restore result",
            found=bool(save),
        )

        return save

    def start_new_run(self, *, user_email: str, level_id: str) -> GameState:
        logger.info(
            "Starting new run",
            user_email=user_email,
            level_id=level_id,
        )

        level = self._require_level(level_id)

        state = GameState.start(
            level_id=level_id,
            start_room=level.start_room,
        )

        state.message = f"Started {level.name}"
        state.event_log.append(f"Started level {level.name}")

        logger.debug(
            "Initial GameState created",
            player_room=state.player.location,
        )

        self._autosave(
            user_email=user_email,
            level_id=level_id,
            state=state,
        )

        return state

    def restart_run(self, *, user_email: str, level_id: str) -> GameState:
        logger.warn(
            "Restarting active run",
            user_email=user_email,
            level_id=level_id,
        )

        self._saves.delete_active(user_email)

        return self.start_new_run(
            user_email=user_email,
            level_id=level_id,
        )

    def abandon_run(self, *, user_email: str) -> None:
        logger.warn(
            "Abandoning active run",
            user_email=user_email,
        )

        self._saves.delete_active(user_email)

    # ------------------------------------------------------------------
    # Gameplay actions
    # ------------------------------------------------------------------

    def move(
        self,
        *,
        user_email: str,
        level_id: str,
        state: GameState,
        direction: str,
    ) -> GameState:
        logger.info(
            "Move requested",
            user_email=user_email,
            level_id=level_id,
            direction=direction,
            player_room=state.player.location,
            move_count=state.move_count,
        )

        if state.status.is_terminal:
            logger.warn(
                "Move blocked: game already terminal",
                status=state.status,
            )
            state.message = "Game already ended."
            return state

        level = self._require_level(level_id)
        room = level.map.rooms[state.player.location]

        if direction not in room.exits:
            logger.warn(
                "Invalid move (wall)",
                room=state.player.location,
                direction=direction,
                exits=list(room.exits.keys()),
            )

            state.move_count += 1

            state.message = "You bumped into a wall."
            state.event_log.append("Bumped into a wall")

            self._autosave(
                user_email=user_email,
                level_id=level_id,
                state=state,
            )

            return state

        next_room = room.exits[direction]

        logger.debug(
            "Move validated",
            from_room=state.player.location,
            to_room=next_room,
        )

        state.player.location = next_room
        state.move_count += 1
        state.visit(next_room)
        state.event_log.append(f"Moved {direction} to {next_room}")
        state.message = None

        entered_room = level.map.rooms[next_room]

        logger.debug(
            "Entered room",
            room=next_room,
            has_item=bool(entered_room.item),
        )

        if entered_room.item:
            logger.debug(
                "Triggering item.on_enter",
                item=entered_room.item,
            )
            entered_room.item.on_enter(state)

        logger.debug("Running level rules check")
        level.rules.check(state, entered_room)

        logger.debug(
            "Post-move GameState",
            player_room=state.player.location,
            move_count=state.move_count,
        )

        return self._persist_or_finalize(
            user_email=user_email,
            level_id=level_id,
            state=state,
        )

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def get_level_projection(self, *, level_id: str, state: GameState) -> dict:
        """
        Produce a UI-safe level projection for the given game state.

        This method exists to keep callbacks decoupled from domain models.
        """
        logger.debug(
            "Generating level projection",
            level_id=level_id,
            player_room=state.player.location,
        )

        level = self._require_level(level_id)
        return level.ui_projection(state)

    def get_leaderboard(self, *, level_id: str, limit: int = 10):
        logger.info(
            "Fetching leaderboard",
            level_id=level_id,
            limit=limit,
        )

        results = self._history.top_scores(level_id, limit=limit)

        logger.debug(
            "Leaderboard fetched",
            level_id=level_id,
            result_count=len(results),
        )

        return results

    def get_user_history(self, *, user_email: str):
        logger.info(
            "Fetching user history",
            user_email=user_email,
        )
        return self._history.by_user(user_email)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _require_level(self, level_id: str):
        logger.debug(
            "Resolving level",
            level_id=level_id,
        )

        level = self._levels.get(level_id)
        if not level:
            logger.error(
                "Unknown level_id",
                level_id=level_id,
            )
            raise ValueError(f"Unknown level_id: {level_id}")

        return level

    def _autosave(self, *, user_email: str, level_id: str, state: GameState) -> None:
        state.updated_at = datetime.now(timezone.utc)

        logger.debug(
            "Autosaving state",
            user_email=user_email,
            level_id=level_id,
            player_room=state.player.location,
            move_count=state.move_count,
        )

        save = GameSave(
            user_email=user_email,
            level_id=level_id,
            state=state,
        )

        self._saves.upsert_active(save)

    def _persist_or_finalize(
        self,
        *,
        user_email: str,
        level_id: str,
        state: GameState,
    ) -> GameState:
        if not state.status.is_terminal:
            self._autosave(
                user_email=user_email,
                level_id=level_id,
                state=state,
            )
            return state

        state.updated_at = datetime.now(timezone.utc)

        logger.info(
            "Finalizing game",
            status=state.status,
        )

        level = self._require_level(level_id)
        score_strategy: ScoreStrategy = level.scoring
        score = score_strategy.calculate(state, level)

        logger.info(
            "Score calculated",
            score=score,
            moves=state.move_count,
            items=len(state.collected_items),
        )

        result = GameResult(
            user_email=user_email,
            level_id=level_id,
            status=state.status,
            score=score,
            moves=state.move_count,
            items_collected=len(state.collected_items),
            finished_at=datetime.now(timezone.utc),
            snapshot={
                "final_room": state.player.location,
                "inventory": sorted(state.collected_items),
                "encountered_villain": state.encountered_villain,
                "optimal_moves": level.optimal_moves,
            },
        )

        self._history.add(result)
        self._saves.delete_active(user_email)

        logger.info(
            "Game finalized and persisted",
            result=result,
        )

        return state
