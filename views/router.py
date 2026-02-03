from dash import html, Input, Output, State

from views.shell import top_nav
from views.pages.login import layout_login
from views.pages.signup import layout_signup
from views.pages.main import layout_main
from views.pages.game import layout_game


def register_router(app):
    @app.callback(
        Output("page", "children"),
        Input("url", "pathname"),
        State("store-auth", "data"),
    )
    def _render(pathname: str, auth: dict | None):
        if auth:
            logged_in = True
        else:
            logged_in = False

        if pathname == "/login":
                return layout_login()

        if pathname == "/signup":
                return layout_signup()

        if pathname == "/":
            if logged_in:
                return html.Div([top_nav(), layout_main()])
            else:
                return layout_login()

        if not logged_in:
            return layout_login()

        if pathname == "/main":
            return html.Div([top_nav(), layout_main()])

        if pathname == "/game":
            return html.Div([top_nav(), layout_game()])

        return html.Div([top_nav(), html.H2("404"), html.P("Page not found")])
