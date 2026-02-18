"""
views/pages/game.py

Author: Jason Fuller

Game page layout (2D view).

Route:
- /game

Responsibilities:
- Render primary gameplay surface
- Display status, relic checklist, and leaderboard
- Provide save/quit action
- Maintain clean responsive layout

Architectural role:
- Pure presentation layer
- No state mutation or controller logic
"""

# ------------------------------------------------------------------
# Dash UI components
# ------------------------------------------------------------------

import dash_bootstrap_components as dbc
from dash import html


# ------------------------------------------------------------------
# UI helpers
# ------------------------------------------------------------------

def _arrow_button(label, btn_id):
    return dbc.Button(
        label,
        id=btn_id,
        color="secondary",
        outline=True,
        style={
            "width": "72px",
            "height": "72px",
            "fontSize": "28px",
            "padding": "0",
        },
    )


# ------------------------------------------------------------------
# Layout
# ------------------------------------------------------------------

def layout_game():
    return dbc.Container(
        [

            # ======================================================
            # MAIN GAME ROW (65% GAME / 35% STATUS PANEL)
            # ======================================================

            dbc.Row(
                [

                    # ==================================================
                    # LEFT COLUMN — MAIN GAME (65%)
                    # ==================================================

                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody(
                                [

                                    # --------------------------
                                    # MAP
                                    # --------------------------

                                    html.H5("Map", className="mb-2"),
                                    html.Div(
                                        id="game-grid",
                                        className="mb-4",
                                    ),

                                    # --------------------------
                                    # MOVEMENT (CENTERED)
                                    # --------------------------

                                    html.Div(
                                        [

                                            html.Div(
                                                _arrow_button("⬆️", "move-up"),
                                                className="text-center mb-2",
                                            ),

                                            html.Div(
                                                [
                                                    _arrow_button("⬅️", "move-left"),
                                                    html.Div(style={"width": "16px"}),
                                                    _arrow_button("➡️", "move-right"),
                                                ],
                                                style={
                                                    "display": "flex",
                                                    "justifyContent": "center",
                                                    "marginBottom": "8px",
                                                },
                                            ),

                                            html.Div(
                                                _arrow_button("⬇️", "move-down"),
                                                className="text-center",
                                            ),
                                        ],
                                        style={
                                            "display": "flex",
                                            "flexDirection": "column",
                                            "alignItems": "center",
                                        },
                                        className="mb-3",
                                    ),

                                    html.Div(
                                        "Use arrows to explore rooms.",
                                        className="text-muted small text-center",
                                    ),

                                    html.Hr(className="my-3"),

                                    # --------------------------
                                    # ACTIVITY LOG
                                    # --------------------------

                                    html.H6("Activity Log", className="mb-2"),
                                    html.Div(
                                        id="event-log",
                                        className="small",
                                        style={
                                            "maxHeight": "180px",
                                            "overflowY": "auto",
                                        },
                                    ),
                                ]
                            ),
                            style={
                                "border": "2px solid #444",
                            },
                        ),
                        md=8,
                    ),

                    # ==================================================
                    # RIGHT COLUMN — STATUS PANEL (35%)
                    # ==================================================

                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody(
                                [

                                    # --------------------------
                                    # OBJECTIVE
                                    # --------------------------

                                    html.H6("Objective", className="mb-1"),
                                    html.Div(
                                        "Collect all relics before confronting the villain. "
                                        "Fewer moves improve efficiency.",
                                        className="small text-muted mb-3",
                                    ),

                                    html.Hr(className="my-3"),

                                    # --------------------------
                                    # STATUS
                                    # --------------------------

                                    html.H6("Status", className="mb-2"),
                                    html.Div(
                                        id="game-status",
                                        className="small mb-3",
                                    ),

                                    html.Hr(className="my-3"),

                                    # --------------------------
                                    # RELICS
                                    # --------------------------

                                    html.H6("Relics", className="mb-2"),
                                    html.Div(
                                        id="game-collection",
                                        className="small mb-3",
                                    ),

                                    html.Hr(className="my-3"),

                                    # --------------------------
                                    # LEADERBOARD
                                    # --------------------------

                                    html.H6("Leaderboard", className="mb-2"),
                                    html.Div(
                                        id="game-leaderboards",
                                        className="small text-muted mb-3",
                                    ),

                                    html.Hr(className="my-3"),

                                    # --------------------------
                                    # SAVE / QUIT
                                    # --------------------------

                                    dbc.Button(
                                        "Save / Quit",
                                        id="btn-quit",
                                        color="danger",
                                        className="w-100",
                                    ),

                                    html.Div(
                                        id="game-options-msg",
                                        className="mt-2 small text-muted",
                                    ),
                                ]
                            )
                        ),
                        md=4,
                    ),
                ],
                className="g-3",
            ),

            # ======================================================
            # RESULT OVERLAY
            # ======================================================

            html.Div(id="result-overlay"),
        ],
        fluid=True,
        className="py-3",
    )
