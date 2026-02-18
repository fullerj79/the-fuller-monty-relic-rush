"""
models/domain/player.py

Author: Jason Fuller

Player domain model.

Responsibilities:
- Represent the player entity within a single game session
- Track player-owned, mutable positional state

Architectural role:
- Domain model (runtime entity)
- Owned by GameState
- Mutated by the GameController

Design notes:
- Player is intentionally lightweight
- Contains no gameplay rules or validation logic
- Inventory and progress are tracked by GameState
- Exists only within the scope of a single session

Logging:
- None (mutations are logged by owning systems)
"""

# ------------------------------------------------------------------
# Standard library imports
# ------------------------------------------------------------------
from dataclasses import dataclass


@dataclass
class Player:
    """
    Represents the player within a game session.

    Structure:
    - location: current room identifier

    Invariants:
    - location always refers to a valid room in the active Level
    """

    location: str
