"""
Game controller.

Author: Jason Fuller
Date: 2/1/26

Purpose:
- Orchestrate gameplay at the application boundary (UI <-> domain <-> persistence)
- Own session lifecycle: start, restore, apply action, autosave, finalize results
- Keep callbacks thin by exposing UI-ready helper methods

Architectural role:
- Application Controller
- Coordinates domain models, rules, scoring, and repositories
- Does NOT render UI or depend on Dash

Design decisions:
- One active run per user (autosave keyed by user_email)
- Terminal states (COMPLETED / GAME_OVER) write immutable GameResult
- Abandoned runs are discarded (no history record)
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from models.domain.game_state import GameState
from models.domain.player import Player
from models.domain.status import GameStatus
from models.domain.scoring import ScoreStrategy

from models.records.game_save import GameSave
from models.records.game_result import GameResult

from models.repositories.level_repo import LevelRepository
from models.repositories.save_repo import SaveRepository
from models.repositories.history_repo import HistoryRepository


class GameController:
    """
    Application controller for a single user's gameplay session.

    Responsibilities:
    - Detect existing runs
    - Start / restore / abandon runs
    - Apply gameplay actions
    - Enforce lifecycle transitions
    - Coordinate autosave and history persistence

    This controller owns orchestration logic, not business rules.
    """

    def __init__(
        self,
        *,
        level_repo: LevelRepository,
        save_repo: SaveRepository,
        history_repo: HistoryRepository,
    ) -> None:
        self._levels = level_repo
        self._saves = save_repo
        self._history = history_repo

    # ------------------------------------------------------------------
    # Session lifecycle & detection
    # ------------------------------------------------------------------

    def has_active_run(self, *, user_email: str) -> bool:
        """
        Determine whether the user has an active, resumable run.

        Intended for UI flow decisions (resume vs start new).
        """
        return self._saves.get_active(user_email) is not None

    def restore_run(self, *, user_email: str) -> Optional[GameSave]:
        """
        Restore the user's active run, if one exists.
        """
        return self._saves.get_active(user_email)

    def start_new_run(self, *, user_email: str, level_id: str) -> GameState:
        """
        Start a new run for a user.

        Behavior:
        - Overwrites any existing active autosave
        - Initializes GameState in IN_PROGRESS
        """
        level = self._require_level(level_id)

        state = GameState(
            player=Player(location=level.start_room),
        )
        state.visit(level.start_room)
        state.message = f"Started {level.name}"

        self._autosave(user_email=user_email, level_id=level_id, state=state)
        return state

    def restart_run(self, *, user_email: str, level_id: str) -> GameState:
        """
        Explicitly abandon any existing run and start fresh.

        This is intentionally separate from start_new_run so UI intent
        (resume vs restart) is explicit and auditable.
        """
        self._saves.delete_active(user_email)
        return self.start_new_run(user_email=user_email, level_id=level_id)

    def abandon_run(self, *, user_email: str) -> None:
        """
        Abandon the current run intentionally.

        Design rule:
        - No GameResult is written
        - Autosave is simply deleted
        """
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
        """
        Apply a movement action and process consequences.

        Controller guarantees:
        - No mutations after terminal state
        - move_count is incremented centrally
        - Item hooks and rule evaluation are applied in order
        - Autosave or finalize is handled consistently
        """
        if state.status.is_terminal:
            state.message = "Game already ended."
            return state

        level = self._require_level(level_id)
        room = level.map.rooms[state.player.location]

        if direction not in room.exits:
            state.message = "You bumped into a wall."
            state.event_log.append("Bumped into a wall")
            self._autosave(user_email=user_email, level_id=level_id, state=state)
            return state

        # Perform movement
        next_room = room.exits[direction]
        state.player.location = next_room
        state.move_count += 1
        state.visit(next_room)
        state.event_log.append(f"Moved {direction} to {next_room}")
        state.message = None

        # Item hook (polymorphic)
        entered_room = level.map.rooms[next_room]
        if entered_room.item:
            entered_room.item.on_enter(state)

        # Apply rules
        level.rules.check(state, entered_room)

        return self._persist_or_finalize(
            user_email=user_email,
            level_id=level_id,
            state=state,
        )

    def pickup(self, *, user_email: str, level_id: str, state: GameState) -> GameState:
        """
        Explicit pickup action.

        Current domain behavior:
        - Relics auto-collect via Item.on_enter()
        - This method is intentionally a no-op

        Reserved for future explicit pickup mechanics.
        """
        if state.status.is_terminal:
            state.message = "Game already ended."
            return state

        state.message = "Nothing to pick up."
        self._autosave(user_email=user_email, level_id=level_id, state=state)
        return state

    # ------------------------------------------------------------------
    # Results & leaderboards
    # ------------------------------------------------------------------

    def get_leaderboard(self, *, level_id: str, limit: int = 10):
        """
        Retrieve top scores for a level.
        """
        return self._history.top_scores(level_id, limit=limit)

    def get_user_history(self, *, user_email: str):
        """
        Retrieve completed run history for a user.
        """
        return self._history.by_user(user_email)

    # ------------------------------------------------------------------
    # UI helpers
    # ------------------------------------------------------------------

    def get_level_projection(self, *, level_id: str, state: GameState):
        """
        Return a UI-safe projection of the level using its visibility policy.
        """
        level = self._require_level(level_id)
        return level.ui_projection(state)

    def can_act(self, *, state: GameState) -> bool:
        """
        Indicate whether UI actions should be enabled.
        """
        return not state.status.is_terminal

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _require_level(self, level_id: str):
        level = self._levels.get(level_id)
        if not level:
            raise ValueError(f"Unknown level_id: {level_id}")
        return level

    def _autosave(self, *, user_email: str, level_id: str, state: GameState) -> None:
        """
        Persist the user's active run.

        Identity rule:
        - One autosave per user (keyed by user_email)
        """
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
        """
        Autosave if still active; otherwise finalize into GameResult.

        Finalization sequence:
        1. Compute score via level scoring policy
        2. Write immutable GameResult
        3. Delete active autosave
        """
        if not state.status.is_terminal:
            self._autosave(user_email=user_email, level_id=level_id, state=state)
            return state

        level = self._require_level(level_id)
        score_strategy: ScoreStrategy = level.scoring
        score = score_strategy.calculate(state, level)

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

        return state
