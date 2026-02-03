import dash_bootstrap_components as dbc
from dash import html, dcc


def layout_login():
    return dbc.Container(
        [
            html.H2("Welcome", className="mb-1"),
            html.P("Log in or create a new account to start playing."),
            dbc.Row(
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            [
                                html.H4("Log in", className="card-title"),
                                dbc.Input(
                                    id="login-email",
                                    placeholder="Email",
                                    type="email",
                                    className="mb-2",
                                ),
                                dbc.Input(
                                    id="login-pass",
                                    placeholder="Password",
                                    type="password",
                                    className="mb-2",
                                ),
                                dbc.Button(
                                    "Log in",
                                    id="btn-login",
                                    color="primary",
                                    className="w-100",
                                ),
                                html.Div(id="login-msg", className="mt-2"),

                                # Used to delay redirect after successful login
                                dcc.Interval(
                                    id="login-redirect-timer",
                                    interval=2000,   # 2 seconds
                                    n_intervals=0,
                                    disabled=True,
                                ),

                                html.Hr(),
                                html.Div(
                                    [
                                        html.Span("Need an account? "),
                                        dcc.Link("Create one", href="/signup"),
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
