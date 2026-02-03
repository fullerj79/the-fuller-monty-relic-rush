"""
callbacks/__init__.py

Author: Jason Fuller
Date: 2026-01-25

Callback registration hub.

This module centralizes callback registration so app.py only needs to call
one function. This helps keep the app wiring clean as more callback modules
are added (auth, game, admin, etc.).
"""

from callbacks.auth import register_auth_callbacks
from callbacks.main import register_main_callbacks
from callbacks.game import register_game_callbacks


def register_callbacks(app, user_controller, game_controller):
    """
    Register all callbacks for the app.

    Args:
        app: Dash app instance.
        user_controller: Injected controller that handles login/signup logic.
    """
    register_auth_callbacks(app, user_controller)
    register_main_callbacks(app)
    register_game_callbacks(app, game_controller)
