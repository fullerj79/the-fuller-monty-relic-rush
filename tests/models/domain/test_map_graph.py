"""
tests/models/domain/test_map_graph.py

Author: Jason Fuller

MapGraph domain model tests.

Responsibilities:
- Validate neighbor resolution logic
- Ensure room connectivity mapping remains accurate

Architectural role:
- Domain layer test
- Guards graph navigation contract
- Protects movement logic used by GameController

Design notes:
- Focuses on public graph behavior
- Does not test internal storage implementation
- Ensures direction-to-room mappings remain stable
"""

from models.domain.room import Room
from models.domain.map_graph import MapGraph


# ==========================================================
# Neighbor Resolution
# ==========================================================

def test_neighbors_returns_correct_mapping():
    """
    neighbors() should return the directional exit mapping
    for the specified room.
    """
    room_a = Room("A", exits={"north": "B"})
    room_b = Room("B", exits={})

    coords = {
        "A": (0, 0),
        "B": (0, 1),
    }

    graph = MapGraph(
        rooms={"A": room_a, "B": room_b},
        coords=coords,
    )

    neighbors = graph.neighbors("A")

    assert neighbors == {"north": "B"}
