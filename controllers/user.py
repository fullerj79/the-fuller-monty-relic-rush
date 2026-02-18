"""
controllers/user.py

Author: Jason Fuller

User authentication controller

Responsibilities:
- Validate user input for login and signup
- Coordinate with UserRepository for user lookup and creation
- Delegate password hashing and verification to auth helpers
- Return simple (success, message, data) tuples for the view layer

Non-responsibilities:
- Direct database access
- UI rendering
- Session management

Return conventions:
- signup(...) -> (success: bool, message: str)
- login(...)  -> (success: bool, message: str, user_doc: Optional[dict])

Logging:
- DEBUG: validation flow and branch decisions
- INFO: successful login and signup events
- WARN: failed authentication or invalid input
- ERROR: unexpected controller failures (should be rare)
"""

from __future__ import annotations

# ------------------------------------------------------------------
# Standard library imports
# ------------------------------------------------------------------
from typing import Any, Dict, Optional, Tuple

# ------------------------------------------------------------------
# Domain / model helpers
# ------------------------------------------------------------------
from models.behavior.auth import hash_password, verify_password
from models.repositories.user_repo import UserRepository

# ------------------------------------------------------------------
# Local application imports
# ------------------------------------------------------------------
from utils.logger import get_logger


logger = get_logger(__name__)


class UserController:
    """
    Coordinates user login and signup flows using UserRepository and auth helpers.
    """

    def __init__(self, user_model: UserRepository):
        """
        Args:
            user_model: Repository responsible for user persistence.
        """
        logger.info("Initializing UserController")
        self.user_model = user_model

    def signup(self, display_name: str, email: str, password: str) -> Tuple[bool, str]:
        """
        Create a new user account.

        Flow:
        1) Validate inputs
        2) Check for existing email
        3) Hash password
        4) Insert user record
        """
        logger.debug(
            "Signup requested",
            has_display_name=bool(display_name),
            has_email=bool(email),
            has_password=bool(password),
        )

        if not display_name or not email or not password:
            logger.warn("Signup failed: missing required fields")
            return False, "Please fill all fields."

        email_l = email.lower().strip()

        logger.debug(
            "Checking for existing user",
            email=email_l,
        )

        if self.user_model.get_by_email(email_l):
            logger.warn(
                "Signup failed: email already exists",
                email=email_l,
            )
            return False, "That email already exists."

        pw_hash = hash_password(password)

        logger.debug("Password hashed successfully")

        self.user_model.create_user(
            display_name=display_name,
            email=email_l,
            password_hash=pw_hash,
        )

        logger.info(
            "Signup successful",
            email=email_l,
        )

        return True, "Account created. You can log in now."

    def login(
        self,
        email: str,
        password: str,
    ) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        Log a user in by verifying email and password.

        Returns:
            (success, message, user_doc)
        """
        logger.debug(
            "Login requested",
            has_email=bool(email),
            has_password=bool(password),
        )

        if not email or not password:
            logger.warn("Login failed: missing credentials")
            return False, "Enter email + password.", None

        email_l = email.lower().strip()

        logger.debug(
            "Looking up user by email",
            email=email_l,
        )

        user = self.user_model.get_by_email(email_l)

        if not user:
            logger.warn(
                "Login failed: user not found",
                email=email_l,
            )
            return False, "User not found.", None

        if not verify_password(password, user.get("password_hash", "")):
            logger.warn(
                "Login failed: invalid password",
                email=email_l,
            )
            return False, "Wrong password.", None

        logger.info(
            "Login successful",
            email=email_l,
        )

        return True, "Logged in.", user


    def get_display_name(self, email: str) -> str | None:
        """
        Resolve display name for a user.

        Returns:
            str | None:
                - display name if found
                - None if user not found or no display name set
        """

        if not email:
            return None

        email_l = email.lower().strip()

        logger.debug(
            "Resolving display name",
            email=email_l,
        )

        try:
            user = self.user_model.get_by_email(email_l)
        except Exception as e:
            logger.error(
                "Display name lookup failed",
                email=email_l,
                error=str(e),
            )
            return None

        if not user:
            logger.warn(
                "Display name lookup: user not found",
                email=email_l,
            )
            return None

        name = (user.get("display_name") or "").strip()

        if not name:
            logger.debug(
                "Display name lookup: empty display name",
                email=email_l,
            )
            return None

        return name
