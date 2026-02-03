"""
User repository interfaces and implementations.

Author: Jason Fuller
Date: 2/1/26

This module defines the UserRepository abstraction and provides
concrete implementations for user persistence across different
storage backends.

Architectural role:
- Repository layer (authentication & identity data)
- Abstracts persistence from authentication logic
- Uses email as the stable user identifier

Design notes:
- Repositories return raw user documents (dicts)
- Password handling (hashing/verification) occurs elsewhere
- This layer performs no authorization logic
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any


# ============================================================================
# Repository interface
# ============================================================================

class UserRepository(ABC):
    """
    Abstract repository interface for user persistence.

    Implementations:
    - LocalUserRepository
    - MongoUserRepository

    Responsibilities:
    - Retrieve users by email
    - Create new users

    Non-responsibilities:
    - Password hashing
    - Authentication decisions
    - Session management
    """

    @abstractmethod
    def get_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a user record by email.

        Returns:
        - User document dict if found
        - None if no such user exists
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


# ============================================================================
# In-memory implementation
# ============================================================================

class LocalUserRepository(UserRepository):
    """
    In-memory implementation of UserRepository.

    Use cases:
    - Unit tests
    - Local development
    - Offline / Mongo-less environments

    Implementation notes:
    - Users are keyed by email
    - Data is lost when the process exits
    """

    def __init__(self, seed_users: Dict[str, Dict[str, Any]] | None = None) -> None:
        # key: email → value: user dict
        self._users: Dict[str, Dict[str, Any]] = seed_users or {}

    def get_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        return self._users.get(email)

    def create_user(
        self,
        display_name: str,
        email: str,
        password_hash: str,
    ) -> None:
        self._users[email] = {
            "display_name": display_name,
            "email": email,
            "password_hash": password_hash,
        }


# ============================================================================
# MongoDB implementation
# ============================================================================

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
        Inject the MongoDB collection to keep this repository
        decoupled from global state and testable.
        """
        self._col = users_collection

    def get_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        return self._col.find_one({"email": email})

    def create_user(
        self,
        display_name: str,
        email: str,
        password_hash: str,
    ) -> None:
        self._col.insert_one(
            {
                "display_name": display_name,
                "email": email,
                "password_hash": password_hash,
            }
        )
