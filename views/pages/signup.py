"""
views/pages/signup.py

Author: Jason Fuller
Date: 2026-01-25

Signup page layout.

This view renders the account creation form and includes a redirect timer that
is enabled by callbacks on successful signup. The timer gives the user a moment
to read the success message before routing them back to the login page.
"""

import dash_bootstrap_components as dbc
from dash import html, dcc


def layout_signup():
    return dbc.Container(
        [
            html.H2("Welcome", className="mb-1"),
            html.P("Create a new account to start playing."),
            dbc.Row(
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            [
                                html.H4("Create account", className="card-title"),
                                dbc.Input(
                                    id="signup-name",
                                    placeholder="Display name",
                                    type="text",
                                    className="mb-2",
                                ),
                                dbc.Input(
                                    id="signup-email",
                                    placeholder="Email",
                                    type="email",
                                    className="mb-2",
                                ),
                                dbc.Input(
                                    id="signup-pass",
                                    placeholder="Password",
                                    type="password",
                                    className="mb-2",
                                ),
                                dbc.Button(
                                    "Create account",
                                    id="btn-signup",
                                    color="success",
                                    className="w-100",
                                ),
                                html.Div(id="signup-msg", className="mt-2"),

                                # Used to delay redirect after successful signup
                                dcc.Interval(
                                    id="signup-redirect-timer",
                                    interval=2000,  # 2 seconds
                                    n_intervals=0,
                                    disabled=True,
                                ),

                                html.Hr(),
                                html.Div(
                                    [
                                        html.Span("Already have an account? "),
                                        dcc.Link("Log in", href="/login"),
                                    ],
                                    className="text-center",
                                ),
                            ]
                        )
                    ),
                    md=6,
                    lg=5,
                ),
                justify="center",
                className="gy-3",
            ),
        ],
        className="py-4",
    )
