"""
db/mongo.py

Author: Jason Fuller
Date: 2026-01-25

MongoDB connection and collection registry.

This module creates a single MongoClient and exposes collection handles
for the rest of the app (models layer) to use.
"""

import os

import certifi
from pymongo import MongoClient
from pymongo.errors import PyMongoError

MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_DB = os.getenv("MONGODB_DB")

if not MONGODB_URI:
    raise RuntimeError("Missing MONGODB_URI env var. Set it in your .env")

if not MONGODB_DB:
    raise RuntimeError("Missing MONGODB_DB env var. Set it in your .env")


def _create_client() -> MongoClient:
    """
    Create a MongoClient configured for TLS.

    Notes:
    - MongoDB Atlas enforces TLS by default for modern connection strings.
    - We explicitly enable TLS and provide a trusted CA bundle to ensure
      certificate verification succeeds across environments (local/Render).
    """
    try:
        client = MongoClient(
            MONGODB_URI,
            tls=True,
            tlsCAFile=certifi.where(),
            tlsAllowInvalidCertificates=False,
            serverSelectionTimeoutMS=15000,
            connectTimeoutMS=15000,
            socketTimeoutMS=15000,
            appName="TheFullerMontyRelicRush",
        )

        # Defensive: force an initial handshake so failures occur at startup
        # instead of during the first real request.
        client.admin.command("ping")
        return client

    except PyMongoError as e:
        raise RuntimeError(
            f"MongoDB connection failed (PyMongoError). "
            f"Check MONGODB_URI/MONGODB_DB, network access, and TLS settings. Details: {e}"
        ) from e
    except Exception as e:
        raise RuntimeError(
            f"MongoDB connection failed (unexpected error). Details: {type(e).__name__}: {e}"
        ) from e


_client = _create_client()

try:
    _db = _client[MONGODB_DB]
except Exception as e:
    raise RuntimeError(
        f"MongoDB database selection failed for '{MONGODB_DB}'. "
        f"Details: {type(e).__name__}: {e}"
    ) from e

# Collections
try:
    users_collection = _db["users"]
    levels_collection = _db["levels"]
    game_saves_collection = _db["game_saves"]
    game_results_collection = _db["game_results"]
except Exception as e:
    raise RuntimeError(
        f"MongoDB collection registry failed. "
        f"Details: {type(e).__name__}: {e}"
    ) from e
