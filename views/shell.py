"""
views/shell.py

Author: Jason Fuller

Shared application shell components.

Responsibilities:
- Define reusable layout components shared across pages
- Provide consistent top-level navigation UI
- Render centered game banner with logout action

Architectural role:
- View-layer shared layout module
- Stateless and purely presentational
"""

# ------------------------------------------------------------------
# Dash UI
# ------------------------------------------------------------------

import dash_bootstrap_components as dbc
from dash import html


def top_nav() -> dbc.Navbar:
    """
    Render the application top navigation bar.

    Layout:
    - Large centered banner image
    - Logout button aligned to right
    """

    return dbc.Navbar(
        dbc.Container(
            [
                # --------------------------------------------------
                # Centered Banner
                # --------------------------------------------------

                html.Div(
                    html.Img(
                        src="/assets/logo_rectangle.png",
                        style={
                            "height": "200px",
                            "width": "auto",
                            "display": "block",
                            "margin": "0 auto",
                        },
                    ),
                    style={
                        "width": "100%",
                        "textAlign": "center",
                    },
                ),

                # --------------------------------------------------
                # Logout Button (Right-aligned)
                # --------------------------------------------------

                dbc.Button(
                    "Logout",
                    id="btn-logout",
                    color="secondary",
                    outline=True,
                    size="sm",
                    style={
                        "position": "absolute",
                        "right": "20px",
                        "top": "50%",
                        "transform": "translateY(-50%)",
                    },
                ),
            ],
            fluid=True,
            style={"position": "relative"},
        ),
        color="dark",
        dark=True,
        className="mb-3",
    )
