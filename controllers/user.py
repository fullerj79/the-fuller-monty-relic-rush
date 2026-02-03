"""
controllers/user.py

Author: Jason Fuller
Date: 2026-01-25

User authentication controller (MVC).

This controller coordinates login/signup workflows for the application.
It does NOT contain database queries directly — all MongoDB reads/writes
are handled by the model layer in:

    models/user.py

Responsibilities:
- Validate user input for login/signup
- Call models/user.py for user lookup + user creation
- Call models/auth.py for password hashing + verification
- Return simple (success, message, data) results for the view layer to display

Non-responsibilities:
- Direct DB access
- UI rendering
- Session handling

Return conventions:
- signup(...) -> (success: bool, message: str)
- login(...)  -> (success: bool, message: str, user_doc: Optional[dict])
"""

from __future__ import annotations

from typing import Tuple, Optional, Dict, Any

from models.behavior.auth import hash_password, verify_password
from models.repositories.user_repo import UserModelBase


class UserController:
    """
    Coordinates user login and signup flows using UserModel + auth helpers.
    """

    def __init__(self, user_model: UserModelBase):
        """
        Args:
            user_model: The model layer object responsible for DB reads/writes.
        """
        self.user_model = user_model

    def signup(self, display_name: str, email: str, password: str) -> Tuple[bool, str]:
        """
        Create a new user account.

        Flow:
        1) Validate inputs
        2) Check if the email already exists
        3) Hash password (SALT stored + PEPPER secret)
        4) Insert user record
        """
        if not display_name or not email or not password:
            return False, "Please fill all fields."

        email_l = email.lower().strip()

        if self.user_model.get_by_email(email_l):
            return False, "That email already exists."

        pw_hash = hash_password(password)

        self.user_model.create_user(
            display_name=display_name,
            email=email_l,
            password_hash=pw_hash,
        )

        return True, "Account created. You can log in now."

    def login(self, email: str, password: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        Log a user in by verifying email + password.

        Returns:
            (success, message, user_doc)
        """
        if not email or not password:
            return False, "Enter email + password.", None

        email_l = email.lower().strip()
        user = self.user_model.get_by_email(email_l)

        if not user:
            return False, "User not found.", None

        if not verify_password(password, user.get("password_hash", "")):
            return False, "Wrong password.", None

        return True, "Logged in.", user
