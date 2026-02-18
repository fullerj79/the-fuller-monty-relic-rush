"""
views/pages/signup.py

Author: Jason Fuller

Signup page layout.

Route:
- /signup

Responsibilities:
- Render account creation form
- Display signup feedback messages
- Trigger delayed redirect back to login after successful signup

Architectural role:
- View layer (presentation only)
- Supplies static layout consumed by Dash callbacks
- Does NOT perform validation, persistence, or routing logic

Design notes:
- All form submission logic is handled in callbacks
- Redirect timer is enabled by callbacks after successful signup
- Component IDs form a strict contract with controller logic

Logging:
- None (pure layout definition)
"""

# ------------------------------------------------------------------
# Dash UI components
# ------------------------------------------------------------------

import dash_bootstrap_components as dbc
from dash import html, dcc


def layout_signup():
    """
    Construct the /signup page layout.
    """
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
                                html.Div(
                                    id="signup-msg",
                                    className="mt-2",
                                ),

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
