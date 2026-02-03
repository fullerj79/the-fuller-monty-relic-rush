"""
MongoDB bootstrap utilities.

Author: Jason Fuller
Date: 2/1/26

Initializes required collections, indexes, and seed data.

WARNING:
This script modifies MongoDB collections by creating indexes
and inserting seed data. It is intended to be run manually
during development or deployment, not at runtime.
"""

from datetime import datetime, timezone
from db.mongo import (
    levels_collection,
    game_saves_collection,
    game_results_collection,
    users_collection,
)
from levels.seed_levels import LEVELS


def ensure_indexes():
    """
    Ensure all required MongoDB indexes exist.

    This function is idempotent and safe to run multiple times.
    All indexes are justified by concrete query patterns.
    """

    # ---- users ----
    users_collection.create_index(
        [("email", 1)],
        unique=True,
        name="users_email_unique",
    )

    # ---- levels ----
    levels_collection.create_index(
        [("id", 1)],
        unique=True,
        name="levels_id_unique",
    )
    levels_collection.create_index(
        [("difficulty", 1)],
        name="levels_difficulty",
    )

    # ---- game_saves ----
    game_saves_collection.create_index(
        [("user_email", 1)],
        unique=True,
        name="game_saves_user_unique",
    )
    game_saves_collection.create_index(
        [("updated_at", -1)],
        name="game_saves_updated_at",
    )

    # ---- game_results ----
    game_results_collection.create_index(
        [("level_id", 1), ("score", -1)],
        name="game_results_leaderboard",
    )
    game_results_collection.create_index(
        [("user_email", 1), ("finished_at", -1)],
        name="game_results_user_history",
    )
    game_results_collection.create_index(
        [("user_email", 1), ("level_id", 1)],
        name="game_results_user_level",
    )


def seed_levels_if_missing():
    """
    Insert seed levels if they do not already exist.

    Levels are matched by id. Existing levels are not modified.
    """
    for level in LEVELS:
        exists = levels_collection.find_one({"id": level["id"]})
        if not exists:
            doc = dict(level)
            doc["created_at"] = datetime.now(timezone.utc)
            levels_collection.insert_one(doc)


if __name__ == "__main__":
    print("Running MongoDB bootstrap...")
    ensure_indexes()
    seed_levels_if_missing()
    print("Bootstrap complete.")
