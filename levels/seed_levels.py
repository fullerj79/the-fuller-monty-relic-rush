"""
Authoritative level seed data.

Author: Jason Fuller
Date: 2/1/26

This module defines the canonical built-in level definitions.
These are derived directly from the original ROOMS structure.
"""

LEVELS = [
    {
        "id": "level_1",
        "name": "Relic Rush",
        "difficulty": "medium",
        "start_room": "Space Room",

        "rooms": {
            "Space Room": {
                "exits": {
                    "South": "Reality Room",
                    "East": "Avengers Campus",
                },
                "item": {"type": "relic", "name": "Blue Stone"},
            },
            "Avengers Campus": {
                "exits": {
                    "South": "Power Room",
                    "East": "Mind Room",
                    "West": "Space Room",
                },
                "item": None,
            },
            "Mind Room": {
                "exits": {
                    "South": "Time Room",
                    "West": "Avengers Campus",
                },
                "item": {"type": "relic", "name": "Yellow Stone"},
            },
            "Reality Room": {
                "exits": {
                    "North": "Space Room",
                    "South": "Soul Room",
                    "East": "Power Room",
                },
                "item": {"type": "relic", "name": "Red Stone"},
            },
            "Power Room": {
                "exits": {
                    "North": "Avengers Campus",
                    "East": "Time Room",
                    "West": "Reality Room",
                },
                "item": {"type": "relic", "name": "Purple Stone"},
            },
            "Time Room": {
                "exits": {
                    "North": "Mind Room",
                    "South": "Avengers Compound",
                    "West": "Power Room",
                },
                "item": {"type": "relic", "name": "Green Stone"},
            },
            "Soul Room": {
                "exits": {
                    "North": "Reality Room",
                },
                "item": {"type": "relic", "name": "Orange Stone"},
            },
            "Avengers Compound": {
                "exits": {
                    "North": "Time Room",
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
    }
]
