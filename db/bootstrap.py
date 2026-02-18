"""
db/bootstrap.py

MongoDB bootstrap utilities.

Author: Jason Fuller

Initializes required MongoDB collections, indexes, and seed data.

Responsibilities:
- Ensure required MongoDB indexes exist
- Insert initial seed data for levels
- Provide a safe, idempotent bootstrap entry point

WARNING:
This script mutates MongoDB state by creating indexes and inserting data.
It is intended to be run manually during development or deployment,
not during application runtime.

Logging:
- INFO: bootstrap lifecycle, index creation, seed insertions
- DEBUG: idempotent checks and skipped operations
- WARN: unexpected but non-fatal conditions
- ERROR: failures during bootstrap (should abort execution)
"""

# ------------------------------------------------------------------
# Standard library imports
# ------------------------------------------------------------------
from datetime import datetime, timezone

# ------------------------------------------------------------------
# Local application imports
# ------------------------------------------------------------------
from db.mongo import (
    game_results_collection,
    game_saves_collection,
    levels_collection,
    users_collection,
)
from levels.seed_levels import LEVELS
from utils.logger import get_logger


logger = get_logger(__name__)


def ensure_indexes():
    """
    Ensure all required MongoDB indexes exist.

    This function is idempotent and safe to run multiple times.
    All indexes are justified by concrete query patterns.
    """
    logger.info("Ensuring MongoDB indexes")

    # ---- users ----
    logger.debug("Ensuring users indexes")
    users_collection.create_index(
        [("email", 1)],
        unique=True,
        name="users_email_unique",
    )

    # ---- levels ----
    logger.debug("Ensuring levels indexes")
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
    logger.debug("Ensuring game_saves indexes")
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
    logger.debug("Ensuring game_results indexes")
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

    logger.info("MongoDB index verification complete")


def seed_levels_if_missing():
    """
    Insert seed levels if they do not already exist.

    Levels are matched by id. Existing levels are not modified.
    """
    logger.info("Seeding levels if missing")

    inserted = 0
    skipped = 0

    for level in LEVELS:
        level_id = level.get("id")

        exists = levels_collection.find_one({"id": level_id})
        if exists:
            logger.debug(
                "Level already exists; skipping seed",
                level_id=level_id,
            )
            skipped += 1
            continue

        doc = dict(level)
        doc["created_at"] = datetime.now(timezone.utc)

        levels_collection.insert_one(doc)

        logger.info(
            "Seeded new level",
            level_id=level_id,
        )
        inserted += 1

    logger.info(
        "Level seeding complete",
        inserted=inserted,
        skipped=skipped,
    )


if __name__ == "__main__":
    logger.info("Starting MongoDB bootstrap")

    try:
        ensure_indexes()
        seed_levels_if_missing()
    except Exception as exc:
        logger.error(
            "MongoDB bootstrap failed",
            error=str(exc),
        )
        raise

    logger.info("MongoDB bootstrap complete")
