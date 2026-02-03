"""
Level composition and configuration.

Author: Jason Fuller
Date: 2/1/26

This module defines the Level class, which represents an immutable,
fully-validated game configuration. A Level encapsulates all static
information required to run a game session, including map topology,
rules, visibility behavior, scoring behavior, and difficulty metadata.

Architectural role:
- Domain model (static configuration)
- Constructed once at load time (e.g., from database or file)
- Shared safely across multiple game sessions
- Consumed by controllers, UI projection, scoring, and validation logic

A Level is intentionally immutable after construction. Any mutation of
Level data at runtime would invalidate guarantees around solvability,
optimal move calculation, scoring fairness, and replayability.
"""

from dataclasses import dataclass
from models.domain.map_graph import MapGraph
from models.domain.rules import LevelRules
from models.behavior.visibility import VisibilityPolicy
from models.domain.scoring import ScoreStrategy
from models.domain.difficulty import Difficulty


@dataclass(frozen=True)
class Level:
    """
    Represents a single playable level definition.

    Structure:
    - id: unique identifier for persistence and lookup
    - name: human-readable display name
    - difficulty: difficulty classification (e.g., easy, medium, hard)
    - start_room: room identifier where the player begins
    - map: immutable graph of rooms and spatial layout
    - rules: rule set governing win/loss conditions
    - visibility: strategy defining what the player can see
    - scoring: strategy defining how completed sessions are scored
    - optimal_moves: cached minimum moves required to win (computed once)

    Invariants:
    - This object is immutable after construction.
    - map, rules, visibility, and scoring are assumed to be fully validated.
    - optimal_moves, if present, corresponds to this exact level layout.
    - start_room is guaranteed to exist in map.rooms.

    This class does NOT:
    - track player progress
    - perform movement
    - enforce rules at runtime
    - render UI
    - persist state

    All runtime changes occur in GameState. Level serves as a trusted,
    static reference for all sessions playing this level.
    """

    id: str
    name: str
    difficulty: Difficulty
    start_room: str

    map: MapGraph
    rules: LevelRules
    visibility: VisibilityPolicy
    scoring: ScoreStrategy

    optimal_moves: int | None = None

    def ui_projection(self, state):
        """
        Produce a UI-safe projection of this level for the given game state.

        This method delegates visibility decisions to the configured
        VisibilityPolicy, allowing difficulty-specific rendering rules
        (e.g., fog-of-war, hidden items, hidden villain).

        Side effects:
        - None

        Assumptions:
        - state corresponds to a session running this level
        - visibility policy is compatible with the level configuration

        Returns:
        - LevelUIProjection instance suitable for consumption by the UI
        """
        return self.visibility.project(self, state)
