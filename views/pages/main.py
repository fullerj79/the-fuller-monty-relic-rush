"""
views/pages/main.py

Author: Jason Fuller

Main page layout.

Route:
- /main

Responsibilities:
- Render post-login landing page
- Display instructions
- Display unified leaderboard (Top 10 overall)
- Provide resume functionality
- Provide new game difficulty selection
- Confirm destructive overwrite actions

Architectural role:
- Pure presentation layer
- No game/session logic
"""

# ------------------------------------------------------------------
# Dash UI components
# ------------------------------------------------------------------

import dash_bootstrap_components as dbc
from dash import html, dcc


def layout_main():
    """
    Construct the /main landing page layout.
    """

    return dbc.Container(
        [

            # ======================================================
            # HEADER
            # ======================================================

            html.H2("Relic Rush", className="mb-1"),
            html.Div(
                id="main-welcome",
                className="text-muted mb-4",
            ),

            # ======================================================
            # TWO-COLUMN LAYOUT
            # ======================================================

            dbc.Row(
                [

                    # ==================================================
                    # LEFT COLUMN — INFO
                    # ==================================================

                    dbc.Col(
                        [

                            # ------------------------------
                            # HOW TO PLAY
                            # ------------------------------

                            dbc.Card(
                                dbc.CardBody(
                                    [
                                        html.H4("How to Play", className="card-title"),
                                        html.Ul(
                                            [
                                                html.Li("Move using directional arrows."),
                                                html.Li("Collect all relics."),
                                                html.Li("Avoid the villain until prepared."),
                                                html.Li("Fewer moves = higher efficiency."),
                                            ],
                                            className="mb-0",
                                        ),
                                    ]
                                ),
                                className="mb-4",
                            ),

                            # ------------------------------
                            # LEADERBOARD
                            # ------------------------------

                            dbc.Card(
                                dbc.CardBody(
                                    [
                                        html.H4("Leaderboard", className="card-title"),
                                        html.Div(
                                            id="main-leaderboard",
                                            className="small",
                                        ),
                                    ]
                                )
                            ),
                        ],
                        md=6,
                    ),

                    # ==================================================
                    # RIGHT COLUMN — ACTIONS
                    # ==================================================

                    dbc.Col(
                        [

                            # ------------------------------
                            # RESUME GAME
                            # ------------------------------

                            dbc.Card(
                                dbc.CardBody(
                                    [
                                        html.H4("Resume Game", className="card-title"),
                                        html.Div(
                                            id="resume-details",
                                            className="text-muted mb-2",
                                        ),
                                        dbc.Button(
                                            "Resume",
                                            id="btn-resume-game",
                                            color="success",
                                            disabled=True,
                                            className="w-100",
                                        ),
                                    ]
                                ),
                                className="mb-4",
                            ),

                            # ------------------------------
                            # NEW GAME
                            # ------------------------------

                            dbc.Card(
                                dbc.CardBody(
                                    [
                                        html.H4("New Game", className="card-title"),
                                        html.P(
                                            "Choose a difficulty to start a new run.",
                                            className="text-muted",
                                        ),

                                        # Proper equal-width buttons
                                        dbc.Row(
                                            [
                                                dbc.Col(
                                                    dbc.Button(
                                                        "Easy",
                                                        id="btn-new-easy",
                                                        color="primary",
                                                        className="w-100",
                                                    ),
                                                    width=4,
                                                ),
                                                dbc.Col(
                                                    dbc.Button(
                                                        "Medium",
                                                        id="btn-new-medium",
                                                        color="warning",
                                                        className="w-100",
                                                    ),
                                                    width=4,
                                                ),
                                                dbc.Col(
                                                    dbc.Button(
                                                        "Hard",
                                                        id="btn-new-hard",
                                                        color="danger",
                                                        className="w-100",
                                                    ),
                                                    width=4,
                                                ),
                                            ],
                                            className="mt-2 g-2",
                                        ),

                                        html.Div(
                                            id="main-actions-msg",
                                            className="mt-3 text-muted small",
                                        ),
                                    ]
                                )
                            ),
                        ],
                        md=6,
                    ),
                ],
                className="g-4",
            ),

            # ======================================================
            # HIDDEN STATE
            # ======================================================

            dcc.Store(id="store-pending-level"),

            # ======================================================
            # CONFIRM MODAL
            # ======================================================

            dbc.Modal(
                [
                    dbc.ModalHeader(
                        dbc.ModalTitle("Start New Game?")
                    ),
                    dbc.ModalBody(
                        "You already have an active game in progress. "
                        "Starting a new game will permanently delete your current progress.\n\n"
                        "Do you want to continue?"
                    ),
                    dbc.ModalFooter(
                        [
                            dbc.Button(
                                "Cancel",
                                id="btn-cancel-new-game",
                                color="secondary",
                            ),
                            dbc.Button(
                                "Delete & Start",
                                id="btn-confirm-new-game",
                                color="danger",
                            ),
                        ]
                    ),
                ],
                id="modal-confirm-new-game",
                is_open=False,
                centered=True,
                backdrop="static",
                keyboard=False,
            ),
        ],
        className="py-4",
    )
