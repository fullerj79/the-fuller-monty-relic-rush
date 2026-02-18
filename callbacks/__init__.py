"""
callbacks/__init__.py

Author: Jason Fuller

Callback registration hub.

Responsibilities:
- Centralize callback registration for the Dash app
- Expose a single entry point for wiring UI callbacks
- Keep app.py free of callback module knowledge

Notes:
- New callback modules should be registered here
- This scales cleanly as auth, game, admin, etc. grow

Logging:
- INFO: callback registration lifecycle
"""

# ------------------------------------------------------------------
# Local application imports
# ------------------------------------------------------------------
from callbacks.auth import register_auth_callbacks
from callbacks.game import register_game_callbacks
from callbacks.main import register_main_callbacks
from utils.logger import get_logger


logger = get_logger(__name__)


def register_callbacks(app, user_controller, game_controller):
    """
    Register all callbacks for the app.

    Args:
        app: Dash app instance.
        user_controller: Injected controller that handles login/signup logic.
        game_controller: Injected controller that handles game logic.
    """
    logger.info("Registering application callbacks")

    register_auth_callbacks(app, user_controller)
    register_main_callbacks(app, game_controller, user_controller)
    register_game_callbacks(app, game_controller, user_controller)

    logger.info("All callbacks registered successfully")
