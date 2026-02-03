"""
app.py

Author: Jason Fuller
Date: 2026-01-25

Application entry point.

This is the one place we wire the whole app together at startup:
- Create the Dash app + shared layout shell
- Initialize MongoDB collections (db/mongo.py)
- Construct Models (models/) that perform DB commands
- Construct Controllers (controllers/) that coordinate application logic
- Register the router + all Dash callbacks

Why we do this here:
- MongoDB connections should be created once (not inside callbacks)
- Controllers should be long-lived and reuse the same models
- Keeps responsibilities separated and prevents circular imports

Deploy note (Render):
- Render expects `server = app.server` at module scope.
"""

from dotenv import load_dotenv
load_dotenv()
import os

import dash
from dash import dcc, html
import dash_bootstrap_components as dbc

from models.game import GameState, ROOMS
from controllers.user import UserController
from controllers.game_old import GameController

from views.router import register_router
from callbacks import register_callbacks


def create_app() -> dash.Dash:
    """
    Create and configure the Dash application.

    Returns:
        A fully wired Dash app instance ready to run.
    """
    app = dash.Dash(
        __name__,
        external_stylesheets=[dbc.themes.CYBORG],
        suppress_callback_exceptions=True,
    )
    app.title = "The Fuller Monty: Relic Rush"

    # Minimal app shell. Router swaps page content into "page".
    # Stores live here so any page/callback can access session state.
    app.layout = html.Div(
        [
            dcc.Location(id="url"),
            dcc.Store(id="store-auth", storage_type="session"),
            dcc.Store(id="store-game", storage_type="session"),
            html.Div(id="page"),
        ]
    )

    # Check .env for specialized environment. Bypasses MongoDB.
    APP_MODE = os.getenv("APP_MODE", "PROD").upper()
    if APP_MODE == "LOCAL":
        from models.repositories.user_repo import LocalUserModel
        from models.behavior.auth import hash_password

        seed_users = {
            "test@example.com": {
                "display_name": "Test User",
                "email": "test@example.com",
                "password_hash": hash_password("password"),
            }
        }

        user_model = LocalUserModel(seed_users)

    else:
        from db.mongo import users_collection
        from models.repositories.user_repo import MongoUserModel

        user_model = MongoUserModel(users_collection)


    # Build Model layer (DB access lives here)
    game_model = GameState(ROOMS)

    # Build Controller layer (auth/game flows live here)
    user_controller = UserController(user_model)
    game_controller = GameController(game_model)

    # Wire router + callbacks (UI event handlers)
    register_router(app)
    register_callbacks(app, user_controller=user_controller, game_controller=game_controller)

    return app

app = create_app()

# Render expects this name at module scope
server = app.server


if __name__ == "__main__":
    app.run(debug=True)
