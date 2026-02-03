"""
callbacks/main.py

Author: Jason Fuller
Date: 2026-01-25

Main page callbacks.

This module:
- Populates the main landing page welcome message using the current
  authenticated user stored in `store-auth`.
- Starts a new game session when the user clicks "New Game"
  and routes the user to /game.
"""

from datetime import datetime, timezone
from uuid import uuid4

from dash import Input, Output, State, no_update


def register_main_callbacks(app):
    """
    Register callbacks for the main page.

    Args:
        app: Dash app instance
    """

    @app.callback(
        Output("main-welcome", "children"),
        Input("store-auth", "data"),
    )
    def render_main_welcome(auth_data):
        if not auth_data:
            return no_update

        name = (auth_data.get("display_name") or "").strip()
        if not name:
            return "Welcome"

        return f"Welcome, {name}"

    @app.callback(
        Output("store-game", "data"),
        Output("url", "pathname"),
        Output("main-actions-msg", "children"),
        Input("btn-new", "n_clicks"),
        State("store-auth", "data"),
        prevent_initial_call=True,
    )
    def start_new_game(n_clicks, auth_data):
        """
        Create a new game session in session storage and redirect to /game.
        """
        if not n_clicks:
            return no_update, no_update, no_update

        if not auth_data:
            return no_update, "/login", "You must be logged in to start a new game."

        user_id = auth_data.get("user_id") or auth_data.get("_id") or auth_data.get("id")
        display_name = (auth_data.get("display_name") or "").strip() or "Player"

        game_session = {
            "game_id": str(uuid4()),
            "user_id": user_id,
            "player_name": display_name,
            "started_at": datetime.now(timezone.utc).isoformat(),
            "state": {
                "level": 1,
                "score": 0,
            },
        }

        return game_session, "/game", ""
