"""
tests/test_user_model.py

Author: Jason Fuller
Date: 2/1/26

Integration tests for Mongo-backed user persistence.
"""

from models.repositories.user_repo import MongoUserRepository
from models.behavior.auth import hash_password
from db.mongo import users_collection


def test_user_create_and_lookup():
    model = MongoUserRepository(users_collection)

    model.create_user(
        display_name="Test User",
        email="test@example.com",
        password_hash=hash_password("secret"),
    )

    user = model.get_by_email("test@example.com")

    assert user is not None
    assert user["display_name"] == "Test User"
    assert user["email"] == "test@example.com"
