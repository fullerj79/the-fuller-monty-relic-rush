"""
views/pages/game.py

Author: Jason Fuller
Date: 2026-01-25

Game page layout (2D view).

Route:
- /game

Purpose:
- Render the 2D map/grid view ("game-grid")
- Show hint text, event log, and player status panels
- Provide movement controls + room actions (pickup)
- Support overlay results (win/lose) and periodic tick updates

Notes:
- This file defines layout only.
- Callbacks populate/update:
  - game-grid, game-hint, event-log
  - game-status, game-collection, game-controls
  - room-info, btn-pickup disabled state, pickup-msg
  - result-overlay
"""

import dash_bootstrap_components as dbc
from dash import html, dcc


def layout_game():
    return dbc.Container(
        [
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    html.H4("Map", className="card-title"),
                                    html.Div(id="game-grid", className="mt-2"),
                                    html.Div(id="game-hint", className="mt-3"),
                                    html.Hr(),
                                    html.H6("Event Log"),
                                    html.Div(id="event-log", className="small"),
                                ]
                            )
                        ),
                        md=8,
                    ),
                    dbc.Col(
                        [
                            dbc.Card(
                                dbc.CardBody(
                                    [
                                        html.H5("Status", className="card-title"),
                                        html.Div(id="game-status"),
                                        html.Hr(),
                                        html.Div(id="game-collection"),
                                        html.Hr(),
                                        html.Div(id="game-controls"),
                                    ]
                                )
                            ),
                            html.Div(style={"height": "12px"}),
                            dbc.Card(
                                dbc.CardBody(
                                    [
                                        html.H5("Options", className="card-title"),
                                        dbc.Button(
                                            "Quit",
                                            id="btn-quit",
                                            color="danger",
                                            className="w-100",
                                        ),
                                        html.Div(id="game-options-msg", className="mt-2"),
                                    ]
                                )
                            ),
                        ],
                        md=4,
                    ),
                ],
                className="gy-3",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    html.H5("Move", className="card-title"),
                                    html.Div(
                                        [
                                            dbc.Row(
                                                [
                                                    dbc.Col(width=4),
                                                    dbc.Col(
                                                        dbc.Button("North", id="move-up", className="w-100"),
                                                        width=4,
                                                    ),
                                                    dbc.Col(width=4),
                                                ],
                                                className="mb-2",
                                            ),
                                            dbc.Row(
                                                [
                                                    dbc.Col(
                                                        dbc.Button("West", id="move-left", className="w-100"),
                                                        width=4,
                                                    ),
                                                    dbc.Col(width=4),
                                                    dbc.Col(
                                                        dbc.Button("East", id="move-right", className="w-100"),
                                                        width=4,
                                                    ),
                                                ],
                                                className="mb-2",
                                            ),
                                            dbc.Row(
                                                [
                                                    dbc.Col(width=4),
                                                    dbc.Col(
                                                        dbc.Button("South", id="move-down", className="w-100"),
                                                        width=4,
                                                    ),
                                                    dbc.Col(width=4),
                                                ]
                                            ),
                                        ]
                                    ),
                                ]
                            )
                        ),
                        md=8,
                    ),
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    html.H5("Room", className="card-title"),
                                    html.Div(id="room-info"),
                                    dbc.Button(
                                        "Pick up relic",
                                        id="btn-pickup",
                                        color="success",
                                        className="mt-2",
                                        disabled=True,
                                    ),
                                    html.Div(id="pickup-msg", className="mt-2"),
                                ]
                            )
                        ),
                        md=4,
                    ),
                ],
                className="gy-3 mt-2",
            ),
            html.Div(id="result-overlay"),
        ],
        className="py-3",
        fluid=True,
    )
