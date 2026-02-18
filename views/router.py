"""
views/router.py

Author: Jason Fuller

Application routing and page composition.

Responsibilities:
- Resolve the active page based on URL pathname
- Enforce authentication gating for protected routes
- Compose page layouts with shared shell components (e.g., top_nav)

Architectural role:
- View-layer router
- Coordinates layout selection only
- Does NOT perform authentication, persistence, or business logic

Routing rules:
- /login, /signup are always accessible
- / and /main require authentication
- /game requires authentication
- Unknown routes render a 404 page

Logging:
- None (routing decisions are deterministic and UI-only)
"""

# ------------------------------------------------------------------
# Dash
# ------------------------------------------------------------------

from dash import html, Input, Output, State

# ------------------------------------------------------------------
# Views
# ------------------------------------------------------------------

from views.shell import top_nav
from views.pages.login import layout_login
from views.pages.signup import layout_signup
from views.pages.main import layout_main
from views.pages.game import layout_game


def register_router(app):
    """
    Register the main routing callback.

    This callback selects and composes the correct page layout
    based on the current URL and authentication state.
    """

    @app.callback(
        Output("page", "children"),
        Input("url", "pathname"),
        State("store-auth", "data"),
    )
    def _render(pathname: str, auth: dict | None):
        logged_in = bool(auth)

        # ----------------------------------------------------------
        # Public routes
        # ----------------------------------------------------------

        if pathname == "/login":
            return layout_login()

        if pathname == "/signup":
            return layout_signup()

        # ----------------------------------------------------------
        # Root
        # ----------------------------------------------------------

        if pathname == "/":
            if logged_in:
                return html.Div([top_nav(), layout_main()])
            return layout_login()

        # ----------------------------------------------------------
        # Auth guard
        # ----------------------------------------------------------

        if not logged_in:
            return layout_login()

        # ----------------------------------------------------------
        # Protected routes
        # ----------------------------------------------------------

        if pathname == "/main":
            return html.Div([top_nav(), layout_main()])

        if pathname == "/game":
            return html.Div([top_nav(), layout_game()])

        # ----------------------------------------------------------
        # Fallback
        # ----------------------------------------------------------

        return html.Div(
            [
                top_nav(),
                html.H2("404"),
                html.P("Page not found"),
            ]
        )
