"""
tests/controllers/test_user_controller.py

Author: Jason Fuller

Unit tests for UserController.

Responsibilities:
- Validate user signup workflows
- Validate login authentication behavior
- Verify duplicate detection and validation rules
- Confirm display name lookup behavior

Architectural role:
- Controller layer tests
- Validates orchestration between:
    - UserController
    - UserRepository (LocalUserRepository)
    - Authentication behavior (hashing + verification)

Design notes:
- Uses in-memory repository for isolation
- Does not require database or external services
- Focuses on behavioral correctness, not persistence details

Test strategy:
- Happy-path validation
- Failure cases (missing fields, duplicates, wrong password)
- Non-existent user lookups
"""

import pytest

from controllers.user import UserController
from models.repositories.user_repo import LocalUserRepository


# ------------------------------------------------------------------
# Fixtures
# ------------------------------------------------------------------

@pytest.fixture
def controller():
    """
    Provides a fresh UserController backed by an in-memory repository.

    Each test gets an isolated user store.
    """
    repo = LocalUserRepository({})
    return UserController(repo)


# ------------------------------------------------------------------
# Signup Tests
# ------------------------------------------------------------------

def test_signup_success(controller):
    """
    A valid signup should succeed and return a success message.
    """
    ok, msg = controller.signup(
        display_name="Test User",
        email="test@test.com",
        password="password123",
    )

    assert ok
    assert "Account created" in msg


def test_signup_missing_fields(controller):
    """
    Signup should fail if required fields are missing.
    """
    ok, msg = controller.signup("", "x@test.com", "pass")
    assert not ok


def test_signup_duplicate(controller):
    """
    Signing up with an existing email should fail.
    """
    controller.signup("User", "dup@test.com", "pass")

    ok, msg = controller.signup("User2", "dup@test.com", "pass")
    assert not ok


# ------------------------------------------------------------------
# Login Tests
# ------------------------------------------------------------------

def test_login_success(controller):
    """
    Login should succeed with correct credentials.
    """
    controller.signup("User", "login@test.com", "password")

    ok, msg, user = controller.login(
        email="login@test.com",
        password="password",
    )

    assert ok
    assert user is not None


def test_login_wrong_password(controller):
    """
    Login should fail if password is incorrect.
    """
    controller.signup("User", "login2@test.com", "password")

    ok, msg, user = controller.login(
        email="login2@test.com",
        password="wrong",
    )

    assert not ok
    assert user is None


# ------------------------------------------------------------------
# Display Name Lookup
# ------------------------------------------------------------------

def test_get_display_name(controller):
    """
    get_display_name should return the stored display name
    for an existing user.
    """
    controller.signup("Display Name", "name@test.com", "password")

    name = controller.get_display_name("name@test.com")
    assert name == "Display Name"


def test_get_display_name_missing(controller):
    """
    get_display_name should return None if the user does not exist.
    """
    name = controller.get_display_name("nope@test.com")
    assert name is None
