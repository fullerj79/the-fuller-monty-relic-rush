"""
Room domain model.

Author: Jason Fuller
Date: 2/1/26

This module defines the Room class, which represents a single logical
location within a level. Rooms are nodes in a MapGraph and define
connectivity via directional exits.

Architectural role:
- Domain model (static structure)
- Represents logical locations and their connections
- Owned by MapGraph and Level

Rooms are treated as immutable structural definitions after level load.
While a room may conceptually contain an item, item state changes are
driven by GameState, not by mutating the Room itself at runtime.
"""

from dataclasses import dataclass
from typing import Dict, Optional
from models.domain.item import Item


@dataclass
class Room:
    """
    Represents a single room in a level.

    Structure:
    - name: unique room identifier
    - exits: mapping of direction → neighboring room_id
    - item: optional item initially present in the room

    Invariants:
    - exits reference only valid room identifiers in the same level
    - exits define logical connectivity, not spatial adjacency
    - room identity is stable for the lifetime of the level

    Design notes:
    - Rooms do not know their own coordinates.
    - Rooms do not track player presence or visitation.
    - Rooms do not enforce movement or rule logic.

    This class does NOT:
    - mutate exits at runtime
    - track whether its item has been collected
    - implement visibility or rendering behavior
    """

    name: str
    exits: Dict[str, str]           # direction → room_name
    item: Optional[Item] = None
