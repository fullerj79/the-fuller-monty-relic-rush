"""
db/mongo.py

Author: Jason Fuller

MongoDB connection and collection registry.

Responsibilities:
- Create and configure a single MongoClient instance
- Validate required MongoDB environment configuration
- Expose collection handles for the models layer

Logging:
- INFO: connection lifecycle milestones
- DEBUG: configuration checks and registry steps
- ERROR: connection or configuration failures (abort startup)
"""

# ------------------------------------------------------------------
# Standard library imports
# ------------------------------------------------------------------
import os

# ------------------------------------------------------------------
# Third-party imports
# ------------------------------------------------------------------
import certifi
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from dotenv import load_dotenv

# ------------------------------------------------------------------
# Local application imports
# ------------------------------------------------------------------
from utils.logger import get_logger


logger = get_logger(__name__)

# Ensure environment is loaded for *all* entrypoints (app, CLI, tests)
load_dotenv()


# ------------------------------------------------------------------
# Environment resolution
# ------------------------------------------------------------------

def _get_config() -> tuple[str, str]:
    """
    Resolve and validate MongoDB environment configuration.

    Returns:
        (mongodb_uri, mongodb_db)

    Raises:
        RuntimeError if required configuration is missing.
    """
    uri = os.getenv("MONGODB_URI")
    db = os.getenv("MONGODB_DB")

    logger.debug(
        "Validating MongoDB environment configuration",
        has_uri=bool(uri),
        has_db=bool(db),
    )

    if not uri:
        logger.error("Missing MONGODB_URI environment variable")
        raise RuntimeError("Missing MONGODB_URI env var. Set it in your .env")

    if not db:
        logger.error("Missing MONGODB_DB environment variable")
        raise RuntimeError("Missing MONGODB_DB env var. Set it in your .env")

    return uri, db


# ------------------------------------------------------------------
# MongoDB client
# ------------------------------------------------------------------

def _create_client() -> MongoClient:
    """
    Create and validate a MongoClient configured for TLS.

    Notes:
    - MongoDB Atlas enforces TLS by default.
    - A trusted CA bundle is explicitly provided for portability.
    """
    uri, _ = _get_config()

    logger.info("Creating MongoDB client")

    try:
        client = MongoClient(
            uri,
            tls=True,
            tlsCAFile=certifi.where(),
            tlsAllowInvalidCertificates=False,
            serverSelectionTimeoutMS=15000,
            connectTimeoutMS=15000,
            socketTimeoutMS=15000,
            appName="TheFullerMontyRelicRush",
        )

        logger.debug("MongoDB client created; performing initial ping")

        # Force handshake so failures occur at startup
        client.admin.command("ping")

        logger.info("MongoDB connection established successfully")
        return client

    except PyMongoError as exc:
        logger.error(
            "MongoDB connection failed (PyMongoError)",
            error=str(exc),
        )
        raise RuntimeError(
            "MongoDB connection failed (PyMongoError). "
            "Check MONGODB_URI/MONGODB_DB, network access, and TLS settings."
        ) from exc

    except Exception as exc:
        logger.error(
            "MongoDB connection failed (unexpected error)",
            error=str(exc),
            error_type=type(exc).__name__,
        )
        raise RuntimeError(
            "MongoDB connection failed (unexpected error)."
        ) from exc


# ------------------------------------------------------------------
# Database selection
# ------------------------------------------------------------------

_client = _create_client()
_, _db_name = _get_config()

try:
    logger.debug("Selecting MongoDB database", database=_db_name)
    _db = _client[_db_name]
except Exception as exc:
    logger.error(
        "MongoDB database selection failed",
        database=_db_name,
        error=str(exc),
    )
    raise RuntimeError(
        f"MongoDB database selection failed for '{_db_name}'."
    ) from exc


# ------------------------------------------------------------------
# Collection registry
# ------------------------------------------------------------------

try:
    logger.debug("Registering MongoDB collections")

    users_collection = _db["users"]
    levels_collection = _db["levels"]
    game_saves_collection = _db["game_saves"]
    game_results_collection = _db["game_results"]

    logger.info("MongoDB collections registered successfully")

except Exception as exc:
    logger.error(
        "MongoDB collection registry failed",
        error=str(exc),
        error_type=type(exc).__name__,
    )
    raise RuntimeError("MongoDB collection registry failed.") from exc
