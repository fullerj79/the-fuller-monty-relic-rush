"""
models/domain/room.py

Author: Jason Fuller

Room domain model.

Responsibilities:
- Represent a single logical location within a level
- Define connectivity via directional exits
- Hold an optional, initial item definition

Architectural role:
- Domain model (static structure)
- Node in the MapGraph
- Owned by Level and MapGraph

Design notes:
- Rooms are immutable after level load
- Item state changes are driven by GameState, not Room mutation
- Rooms do not track player presence or visitation

Logging:
- None (structural data object)
"""

# ------------------------------------------------------------------
# Standard library imports
# ------------------------------------------------------------------
from dataclasses import dataclass
from typing import Optional

# ------------------------------------------------------------------
# Domain imports
# ------------------------------------------------------------------
from models.domain.item import Item

# ------------------------------------------------------------------
# Local application imports
# ------------------------------------------------------------------
from utils.logger import get_logger


logger = get_logger(__name__)


@dataclass(frozen=True)
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
    """

    name: str
    exits: dict[str, str]           # direction > room_name
    item: Optional[Item] = None
