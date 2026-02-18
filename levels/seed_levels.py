"""
levels/seed_levels.py

Author: Jason Fuller

Authoritative level seed data.

Responsibilities:
- Define canonical level layouts for initial database seeding
- Serve as the single source of truth for level structure and rules

Notes:
- This module contains static data only
- It should not perform I/O or database operations directly
- Data is consumed by bootstrap utilities and repositories

Logging:
- DEBUG: module load confirmation and level count
"""

# ------------------------------------------------------------------
# Local application imports
# ------------------------------------------------------------------
from utils.logger import get_logger


logger = get_logger(__name__)


LEVELS = [
    {
        "id": "level_easy",
        "name": "Relic Rush - Easy",
        "difficulty": "easy",
        "start_room": "Avengers Campus",
        "rooms": {
            "Space Room": {
                "exits": {
                    "south": "Reality Room",
                    "east": "Avengers Campus",
                },
                "item": {"type": "relic", "name": "Blue Stone"},
            },
            "Avengers Campus": {
                "exits": {
                    "south": "Power Room",
                    "east": "Mind Room",
                    "west": "Space Room",
                },
                "item": None,
            },
            "Mind Room": {
                "exits": {
                    "south": "Time Room",
                    "west": "Avengers Campus",
                },
                "item": {"type": "relic", "name": "Yellow Stone"},
            },
            "Reality Room": {
                "exits": {
                    "north": "Space Room",
                    "south": "Soul Room",
                    "east": "Power Room",
                },
                "item": {"type": "relic", "name": "Red Stone"},
            },
            "Power Room": {
                "exits": {
                    "north": "Avengers Campus",
                    "east": "Time Room",
                    "west": "Reality Room",
                },
                "item": {"type": "relic", "name": "Purple Stone"},
            },
            "Time Room": {
                "exits": {
                    "north": "Mind Room",
                    "south": "Avengers Compound",
                    "west": "Power Room",
                },
                "item": {"type": "relic", "name": "Green Stone"},
            },
            "Soul Room": {
                "exits": {
                    "north": "Reality Room",
                },
                "item": {"type": "relic", "name": "Orange Stone"},
            },
            "Avengers Compound": {
                "exits": {
                    "north": "Time Room",
                },
                "item": {"type": "villain", "name": "Villain"},
            },
        },
        "coords": {
            "Space Room": [1, 0],
            "Avengers Campus": [2, 0],
            "Mind Room": [3, 0],
            "Reality Room": [1, 1],
            "Power Room": [2, 1],
            "Time Room": [3, 1],
            "Soul Room": [1, 2],
            "Avengers Compound": [3, 2],
        },
        "rules": {
            "required_items": [
                "Blue Stone",
                "Yellow Stone",
                "Red Stone",
                "Purple Stone",
                "Green Stone",
                "Orange Stone",
            ]
        },
        "version": 1,
    },
    {
        "id": "level_medium",
        "name": "Relic Rush - Medium",
        "difficulty": "medium",
        "start_room": "Avengers Campus",
        "rooms": {
            "Space Room": {
                "exits": {
                    "south": "Reality Room",
                    "east": "Avengers Campus",
                },
                "item": {"type": "relic", "name": "Blue Stone"},
            },
            "Avengers Campus": {
                "exits": {
                    "south": "Power Room",
                    "east": "Mind Room",
                    "west": "Space Room",
                },
                "item": None,
            },
            "Mind Room": {
                "exits": {
                    "south": "Time Room",
                    "west": "Avengers Campus",
                },
                "item": {"type": "relic", "name": "Yellow Stone"},
            },
            "Reality Room": {
                "exits": {
                    "north": "Space Room",
                    "south": "Soul Room",
                    "east": "Power Room",
                },
                "item": {"type": "relic", "name": "Red Stone"},
            },
            "Power Room": {
                "exits": {
                    "north": "Avengers Campus",
                    "east": "Time Room",
                    "west": "Reality Room",
                },
                "item": {"type": "relic", "name": "Purple Stone"},
            },
            "Time Room": {
                "exits": {
                    "north": "Mind Room",
                    "south": "Avengers Compound",
                    "west": "Power Room",
                },
                "item": {"type": "relic", "name": "Green Stone"},
            },
            "Soul Room": {
                "exits": {
                    "north": "Reality Room",
                },
                "item": {"type": "relic", "name": "Orange Stone"},
            },
            "Avengers Compound": {
                "exits": {
                    "north": "Time Room",
                },
                "item": {"type": "villain", "name": "Villain"},
            },
        },
        "coords": {
            "Space Room": [1, 0],
            "Avengers Campus": [2, 0],
            "Mind Room": [3, 0],
            "Reality Room": [1, 1],
            "Power Room": [2, 1],
            "Time Room": [3, 1],
            "Soul Room": [1, 2],
            "Avengers Compound": [3, 2],
        },
        "rules": {
            "required_items": [
                "Blue Stone",
                "Yellow Stone",
                "Red Stone",
                "Purple Stone",
                "Green Stone",
                "Orange Stone",
            ]
        },
        "version": 1,
    },
    {
        "id": "level_hard",
        "name": "Relic Rush - Hard",
        "difficulty": "hard",
        "start_room": "Avengers Campus",
        "rooms": {
            "Space Room": {
                "exits": {
                    "south": "Reality Room",
                    "east": "Avengers Campus",
                },
                "item": {"type": "relic", "name": "Blue Stone"},
            },
            "Avengers Campus": {
                "exits": {
                    "south": "Power Room",
                    "east": "Mind Room",
                    "west": "Space Room",
                },
                "item": None,
            },
            "Mind Room": {
                "exits": {
                    "south": "Time Room",
                    "west": "Avengers Campus",
                },
                "item": {"type": "relic", "name": "Yellow Stone"},
            },
            "Reality Room": {
                "exits": {
                    "north": "Space Room",
                    "south": "Soul Room",
                    "east": "Power Room",
                },
                "item": {"type": "relic", "name": "Red Stone"},
            },
            "Power Room": {
                "exits": {
                    "north": "Avengers Campus",
                    "east": "Time Room",
                    "west": "Reality Room",
                },
                "item": {"type": "relic", "name": "Purple Stone"},
            },
            "Time Room": {
                "exits": {
                    "north": "Mind Room",
                    "south": "Avengers Compound",
                    "west": "Power Room",
                },
                "item": {"type": "relic", "name": "Green Stone"},
            },
            "Soul Room": {
                "exits": {
                    "north": "Reality Room",
                },
                "item": {"type": "relic", "name": "Orange Stone"},
            },
            "Avengers Compound": {
                "exits": {
                    "north": "Time Room",
                },
                "item": {"type": "villain", "name": "Villain"},
            },
        },
        "coords": {
            "Space Room": [1, 0],
            "Avengers Campus": [2, 0],
            "Mind Room": [3, 0],
            "Reality Room": [1, 1],
            "Power Room": [2, 1],
            "Time Room": [3, 1],
            "Soul Room": [1, 2],
            "Avengers Compound": [3, 2],
        },
        "rules": {
            "required_items": [
                "Blue Stone",
                "Yellow Stone",
                "Red Stone",
                "Purple Stone",
                "Green Stone",
                "Orange Stone",
            ]
        },
        "version": 1,
    },
]


logger.debug(
    "Level seed data loaded",
    level_count=len(LEVELS),
    level_ids=[level["id"] for level in LEVELS],
)
