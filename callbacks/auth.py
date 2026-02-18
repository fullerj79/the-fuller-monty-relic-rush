"""
callbacks/auth.py

Author: Jason Fuller

Authentication-related callbacks.

Responsibilities:
- Handle Dash callback triggers for login, signup, and logout
- Coordinate UI state with UserController authentication workflows
- Update client-side stores (store-auth, store-game)
- Redirect users via url.pathname

Non-responsibilities:
- Database queries (models/user.py)
- Password hashing or verification (models/auth.py)
- Authentication business rules (controllers/user.py)

Notes:
- user_controller is constructed once in app.py and injected here
- This avoids DB initialization in callbacks and circular imports

Logging:
- DEBUG: callback invocation, branch decisions, redirect flow
- INFO: successful login, signup, logout events
- WARN: failed authentication or invalid session attempts
- ERROR: unexpected callback failures (should be rare)
"""

# ------------------------------------------------------------------
# Third-party imports
# ------------------------------------------------------------------
import dash_bootstrap_components as dbc
from dash import Input, Output, State, no_update

# ------------------------------------------------------------------
# Local application imports
# ------------------------------------------------------------------
from utils.logger import get_logger


logger = get_logger(__name__)


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
        logger.debug(
            "Login callback triggered",
            via_click=bool(n_clicks),
            via_submit=bool(n_submit),
            has_email=bool(email),
            has_password=bool(password),
        )

        if not n_clicks and not n_submit:
            return no_update, no_update, no_update

        ok, msg, user = user_controller.login(email, password)

        if not ok:
            logger.warn(
                "Login failed",
                has_email=bool(email),
            )
            # Stay on /login and show error
            return no_update, dbc.Alert(msg, color="danger"), True

        logger.info(
            "Login successful",
            user_email=user.get("email"),
        )

        success = dbc.Alert(
            "Login successful. Redirecting...",
            color="success",
        )

        return (
            {
                "email": user["email"],
                "display_name": user.get("display_name", ""),
            },
            success,
            False,
        )

    @app.callback(
        Output("url", "pathname", allow_duplicate=True),
        Output("login-redirect-timer", "disabled", allow_duplicate=True),
        Input("login-redirect-timer", "n_intervals"),
        State("login-redirect-timer", "disabled"),
        prevent_initial_call=True,
    )
    def redirect_after_login(n_intervals, disabled):
        logger.debug(
            "Login redirect timer fired",
            n_intervals=n_intervals,
            disabled=disabled,
        )

        if disabled:
            return no_update, no_update

        logger.info("Redirecting user to main page after login")
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
        logger.debug(
            "Signup callback triggered",
            via_click=bool(n_clicks),
            via_submit=bool(n_submit),
            has_name=bool(name),
            has_email=bool(email),
            has_password=bool(password),
        )

        if not n_clicks and not n_submit:
            return no_update, no_update

        ok, msg = user_controller.signup(name, email, password)

        if not ok:
            logger.warn(
                "Signup failed",
                has_email=bool(email),
            )
            return dbc.Alert(msg, color="danger"), True

        logger.info(
            "Signup successful",
            user_email=email,
        )

        success = dbc.Alert(
            "Account created successfully. Redirecting to login...",
            color="success",
        )

        return success, False

    @app.callback(
        Output("url", "pathname", allow_duplicate=True),
        Output("signup-redirect-timer", "disabled", allow_duplicate=True),
        Input("signup-redirect-timer", "n_intervals"),
        State("signup-redirect-timer", "disabled"),
        prevent_initial_call=True,
    )
    def redirect_after_signup(n_intervals, disabled):
        logger.debug(
            "Signup redirect timer fired",
            n_intervals=n_intervals,
            disabled=disabled,
        )

        if disabled:
            return no_update, no_update

        logger.info("Redirecting user to login page after signup")
        return "/login", True

    @app.callback(
        Output("store-auth", "data", allow_duplicate=True),
        Output("store-game", "data", allow_duplicate=True),
        Output("url", "pathname", allow_duplicate=True),
        Input("btn-logout", "n_clicks"),
        prevent_initial_call=True,
    )
    def do_logout(n_clicks):
        logger.debug(
            "Logout callback triggered",
            n_clicks=n_clicks,
        )

        if not n_clicks:
            return no_update, no_update, no_update

        logger.info("User logged out")

        # Logout is a session reset: clear auth + any user-scoped state
        return None, None, "/login"
