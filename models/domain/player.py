"""
Player domain model.

Author: Jason Fuller
Date: 2/1/26

This module defines the Player class, which represents the player entity
within a single game session. Player tracks only player-owned, mutable
state such as location and inventory.

Architectural role:
- Domain model (runtime entity)
- Owned by GameState
- Mutated by the game controller

Player is intentionally lightweight. All gameplay rules, scoring, and
validation logic live outside this class.
"""

from dataclasses import dataclass, field


@dataclass
class Player:
    """
    Represents the player within a game session.

    Structure:
    - location: current room identifier
    - inventory: set of collected item identifiers

    Invariants:
    - location always refers to a valid room in the active Level
    - inventory contains unique item identifiers only

    Design notes:
    - Player is mutable and session-scoped.
    - Player does not know about rooms, maps, or exits.
    - Player does not enforce movement or rule logic.

    This class does NOT:
    - perform movement
    - validate room transitions
    - determine win/loss conditions
    - calculate scores
    - interact with persistence or UI layers
    """

    location: str
    inventory: set[str] = field(default_factory=set)
