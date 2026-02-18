"""
app.py

Author: Jason Fuller

Application entry point.

This module wires the entire application together at startup:
- Creates the Dash app and shared layout shell
- Initializes persistence backends (MongoDB or local/in-memory)
- Constructs repositories and controllers
- Registers the router and all callbacks

Architectural role:
- Application composition root
- Dependency injection hub
- Startup-only configuration and wiring

Design notes:
- MongoDB connections are created once at startup
- Controllers are long-lived and injected into callbacks
- No gameplay logic or domain mutation occurs here
- Prevents circular imports by centralizing composition

Logging:
- None directly
- Downstream controllers, repositories, and domain layers
  perform all structured logging

Deploy note (Render.com):
- Render expects 'server = app.server' at module scope
"""

# ------------------------------------------------------------------
# Environment
# ------------------------------------------------------------------

from dotenv import load_dotenv

load_dotenv()

import os

# ------------------------------------------------------------------
# Dash
# ------------------------------------------------------------------

import dash
from dash import dcc, html
import dash_bootstrap_components as dbc

# ------------------------------------------------------------------
# Controllers
# ------------------------------------------------------------------

from controllers.user import UserController
from controllers.game import GameController

# ------------------------------------------------------------------
# Routing & callbacks
# ------------------------------------------------------------------

from views.router import register_router
from callbacks import register_callbacks


# ------------------------------------------------------------------
# Application factory
# ------------------------------------------------------------------

def create_app() -> dash.Dash:
    """
    Create and configure the Dash application.

    Returns:
        dash.Dash: Fully wired application instance.
    """
    app = dash.Dash(
        __name__,
        external_stylesheets=[dbc.themes.CYBORG],
        suppress_callback_exceptions=True,
    )
    app.title = "The Fuller Monty: Relic Rush"

    # ------------------------------------------------------------------
    # Shared app layout shell
    # ------------------------------------------------------------------

    app.layout = html.Div(
        [
            dcc.Location(id="url"),
            dcc.Store(id="store-auth", storage_type="session"),
            dcc.Store(id="store-game", storage_type="session"),
            dcc.Store(id="store-level", storage_type="session"),
            html.Div(id="page"),
        ]
    )

    # ------------------------------------------------------------------
    # Environment configuration
    # ------------------------------------------------------------------

    app_mode = os.getenv("APP_MODE", "PROD").upper()

    # ------------------------------------------------------------------
    # User persistence
    # ------------------------------------------------------------------

    if app_mode == "LOCAL":
        from models.repositories.user_repo import LocalUserRepository
        from models.behavior.auth import hash_password

        seed_users = {
            "test@example.com": {
                "display_name": "Test User",
                "email": "test@example.com",
                "password_hash": hash_password("password"),
            }
        }

        user_repo = LocalUserRepository(seed_users)

    else:
        from db.mongo import users_collection
        from models.repositories.user_repo import MongoUserRepository

        user_repo = MongoUserRepository(users_collection)

    # ------------------------------------------------------------------
    # Game persistence
    # ------------------------------------------------------------------

    if app_mode == "LOCAL":
        from models.repositories.level_repo import InMemoryLevelRepository
        from models.repositories.save_repo import InMemorySaveRepository
        from models.repositories.history_repo import InMemoryHistoryRepository
        from levels.seed_levels import LEVELS

        level_repo = InMemoryLevelRepository(LEVELS)
        save_repo = InMemorySaveRepository()
        history_repo = InMemoryHistoryRepository()

    else:
        from db.mongo import (
            levels_collection,
            game_saves_collection,
            game_results_collection,
        )
        from models.repositories.level_repo import MongoLevelRepository
        from models.repositories.save_repo import MongoSaveRepository
        from models.repositories.history_repo import MongoHistoryRepository

        level_repo = MongoLevelRepository(levels_collection)
        save_repo = MongoSaveRepository(game_saves_collection)
        history_repo = MongoHistoryRepository(game_results_collection)

    # ------------------------------------------------------------------
    # Controllers
    # ------------------------------------------------------------------

    user_controller = UserController(user_repo)

    game_controller = GameController(
        level_repo=level_repo,
        save_repo=save_repo,
        history_repo=history_repo,
    )

    # ------------------------------------------------------------------
    # Routing + callbacks
    # ------------------------------------------------------------------

    register_router(app)
    register_callbacks(
        app,
        user_controller=user_controller,
        game_controller=game_controller,
    )

    return app


# ------------------------------------------------------------------
# Entrypoint
# ------------------------------------------------------------------

app = create_app()

# Render.com expects this name at module scope
server = app.server

if __name__ == "__main__":
    app.run(debug=True)
