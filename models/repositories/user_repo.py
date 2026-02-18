"""
models/repositories/user_repo.py

Author: Jason Fuller

User repository interfaces and implementations.

Responsibilities:
- Persist and retrieve user identity records
- Provide a persistence abstraction for authentication workflows
- Use email as the stable user identifier

Architectural role:
- Repository layer (authentication & identity data)
- Boundary between persistence and authentication logic
- Consumed by UserController and auth helpers

Design notes:
- Repositories return raw user documents (dicts)
- Password hashing and verification occur outside this layer
- This layer performs no authorization or session logic

Logging:
- DEBUG: repository initialization, user lookup
- INFO: user creation events
"""

from __future__ import annotations

# ------------------------------------------------------------------
# Standard library
# ------------------------------------------------------------------

from abc import ABC, abstractmethod
from typing import Any

# ------------------------------------------------------------------
# Logging
# ------------------------------------------------------------------

from utils.logger import get_logger, LogLevel

log = get_logger("models.repositories.user_repo")


# ------------------------------------------------------------------
# Repository interface
# ------------------------------------------------------------------

class UserRepository(ABC):
    """
    Abstract repository interface for user persistence.

    Responsibilities:
    - Retrieve users by email
    - Create new users

    Non-responsibilities:
    - Password hashing or verification
    - Authentication decisions
    - Session management
    """

    @abstractmethod
    def get_by_email(self, email: str) -> dict[str, Any] | None:
        """
        Retrieve a user record by email.

        Returns:
            User document dict if found, otherwise None.
        """
        raise NotImplementedError

    @abstractmethod
    def create_user(
        self,
        display_name: str,
        email: str,
        password_hash: str,
    ) -> None:
        """
        Persist a new user record.

        Assumptions:
            - Email uniqueness is enforced by the caller or database
            - password_hash is already securely generated
        """
        raise NotImplementedError


# ------------------------------------------------------------------
# In-memory implementation
# ------------------------------------------------------------------

class LocalUserRepository(UserRepository):
    """
    In-memory implementation of UserRepository.

    Use cases:
    - Unit tests
    - Local development
    - Offline / Mongo-less environments
    """

    def __init__(self, seed_users: dict[str, dict[str, Any]] | None = None) -> None:
        self._users: dict[str, dict[str, Any]] = seed_users or {}
        log.debug(
            "Initialized LocalUserRepository",
            data={"user_count": len(self._users)},
        )

    def get_by_email(self, email: str) -> dict[str, Any] | None:
        log.debug("Looking up user (in-memory)", data={"email": email})
        return self._users.get(email)

    def create_user(
        self,
        display_name: str,
        email: str,
        password_hash: str,
    ) -> None:
        log.info(
            "Creating user (in-memory)",
            data={"email": email},
        )
        self._users[email] = {
            "display_name": display_name,
            "email": email,
            "password_hash": password_hash,
        }


# ------------------------------------------------------------------
# MongoDB implementation
# ------------------------------------------------------------------

class MongoUserRepository(UserRepository):
    """
    MongoDB-backed implementation of UserRepository.

    Design notes:
    - Uses email as the primary lookup key
    - Assumes a unique index on users.email
    - Returns raw Mongo documents
    """

    def __init__(self, users_collection) -> None:
        """
        Args:
            users_collection: Injected MongoDB collection
        """
        self._col = users_collection
        log.info("Initialized MongoUserRepository")

    def get_by_email(self, email: str) -> dict[str, Any] | None:
        log.debug("Looking up user in MongoDB", data={"email": email})
        return self._col.find_one({"email": email})

    def create_user(
        self,
        display_name: str,
        email: str,
        password_hash: str,
    ) -> None:
        log.info(
            "Creating user in MongoDB",
            data={"email": email},
        )
        self._col.insert_one(
            {
                "display_name": display_name,
                "email": email,
                "password_hash": password_hash,
            }
        )
