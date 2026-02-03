"""
views/pages/main.py

Author: Jason Fuller
Date: 2026-01-25

Main page layout.

This page is the landing screen after a successful login. It displays a welcome
message for the logged-in user and provides the starting action to begin a new
game session.

The user's name is populated by a callback using the logged-in session data
(e.g., store-auth) and written into the "main-welcome" div.
"""

import dash_bootstrap_components as dbc
from dash import html


def layout_main():
    return dbc.Container(
        [
            html.H2("Welcome", className="mb-2"),
            html.Div(id="main-welcome", className="text-muted mb-3"),
            dbc.Card(
                dbc.CardBody(
                    [
                        html.H4("Play", className="card-title"),
                        dbc.Button(
                            "New Game",
                            id="btn-new",
                            color="primary",
                        ),
                        html.Div(id="main-actions-msg", className="mt-3"),
                    ]
                )
            ),
        ],
        className="py-4",
    )
