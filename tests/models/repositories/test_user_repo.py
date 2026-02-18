"""
tests/models/repositories/test_user_repo.py

Author: Jason Fuller

UserRepository tests.

Responsibilities:
- Validate user creation
- Validate user lookup by email
- Ensure password hash storage is preserved
- Guard Mongo persistence boundary behavior

Architectural role:
- Repository layer test
- Verifies Mongo-backed user persistence
- Protects user identity and authentication storage contract

Design notes:
- Integration-style test (real Mongo collection)
- Focuses on repository contract, not controller logic
- Ensures created users can be reliably retrieved
"""

from models.repositories.user_repo import MongoUserRepository
from models.behavior.auth import hash_password
from db.mongo import users_collection


# ==========================================================
# MongoUserRepository Integration
# ==========================================================

class TestMongoUserRepository:
    """
    Integration tests for Mongo-backed user persistence.
    """

    def test_user_create_and_lookup(self):
        """
        create_user should persist a new user,
        and get_by_email should retrieve it correctly.
        """
        repo = MongoUserRepository(users_collection)

        repo.create_user(
            display_name="Test User",
            email="test@example.com",
            password_hash=hash_password("secret"),
        )

        user = repo.get_by_email("test@example.com")

        assert user is not None
        assert user["display_name"] == "Test User"
        assert user["email"] == "test@example.com"
