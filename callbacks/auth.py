"""
callbacks/auth.py

Author: Jason Fuller
Date: 2026-01-25

This module wires UI events (button clicks + form inputs) to the MVC controller:

    controllers/user.py   -> UserController (login/signup workflow)
    models/user.py        -> UserModel (DB reads/writes)
    models/auth.py        -> hash_password / verify_password (SALT+PEPPER hashing)

Responsibilities:
- Handle Dash callback triggers for:
    - login
    - signup
    - logout
- Update client-side stores (store-auth, store-game)
- Redirect user via url.pathname

Non-responsibilities:
- Database queries (kept inside models/user.py)
- Password hashing/verification details (kept inside models/auth.py)
- Business rules beyond basic UI validation (kept inside controllers/user.py)

Note:
- 'user_controller' is created once in app.py and passed into this module.
  This keeps MongoDB initialization out of callbacks and avoids circular imports.
"""

import dash_bootstrap_components as dbc
from dash import Input, Output, State, no_update


def register_auth_callbacks(app, user_controller):
    """
    Register authentication-related callbacks.

    Args:
        app: Dash app instance
        user_controller: UserController instance (constructed in app.py)
    """

    @app.callback(
        Output("store-auth", "data"),
        Output("login-msg", "children"),
        Output("login-redirect-timer", "disabled"),
        Input("btn-login", "n_clicks"),
        Input("login-pass", "n_submit"),
        State("login-email", "value"),
        State("login-pass", "value"),
        prevent_initial_call=True,
    )
    def do_login(n_clicks, n_submit, email, password):
        if not n_clicks and not n_submit:
            return no_update, no_update, no_update

        ok, msg, user = user_controller.login(email, password)

        if not ok:
            # Stay on /login and show error
            return no_update, dbc.Alert(msg, color="danger"), True

        # Store session identity + show success + enable redirect timer
        success = dbc.Alert("Login successful. Redirecting...", color="success")
        return {"email": user["email"], "display_name": user.get("display_name", "")}, success, False

    @app.callback(
        Output("url", "pathname", allow_duplicate=True),
        Output("login-redirect-timer", "disabled", allow_duplicate=True),
        Input("login-redirect-timer", "n_intervals"),
        State("login-redirect-timer", "disabled"),
        prevent_initial_call=True,
    )
    def redirect_after_login(n_intervals, disabled):
        # Only redirect when the timer is enabled
        if disabled:
            return no_update, no_update

        # Disable timer again and redirect to main page
        return "/main", True

    @app.callback(
        Output("signup-msg", "children"),
        Output("signup-redirect-timer", "disabled"),
        Input("btn-signup", "n_clicks"),
        Input("signup-pass", "n_submit"),
        State("signup-name", "value"),
        State("signup-email", "value"),
        State("signup-pass", "value"),
        prevent_initial_call=True,
    )
    def do_signup(n_clicks, n_submit, name, email, password):
        if not n_clicks and not n_submit:
            return no_update, no_update

        ok, msg = user_controller.signup(name, email, password)

        if not ok:
            return dbc.Alert(msg, color="danger"), True

        # Show success message, then redirect to login after a delay
        success = dbc.Alert("Account created successfully. Redirecting to login...", color="success")
        return success, False

    @app.callback(
        Output("url", "pathname", allow_duplicate=True),
        Output("signup-redirect-timer", "disabled", allow_duplicate=True),
        Input("signup-redirect-timer", "n_intervals"),
        State("signup-redirect-timer", "disabled"),
        prevent_initial_call=True,
    )
    def redirect_after_signup(n_intervals, disabled):
        # Only redirect when the timer is enabled
        if disabled:
            return no_update, no_update

        # Disable timer again and redirect to login page
        return "/login", True

    @app.callback(
        Output("store-auth", "data", allow_duplicate=True),
        Output("store-game", "data", allow_duplicate=True),
        Output("url", "pathname", allow_duplicate=True),
        Input("btn-logout", "n_clicks"),
        prevent_initial_call=True,
    )
    def do_logout(n_clicks):
        if not n_clicks:
            return no_update, no_update, no_update

        # Logout is a session reset: clear auth + any user-scoped state (store-game)
        return None, None, "/login"
