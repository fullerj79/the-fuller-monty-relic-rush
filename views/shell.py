import dash_bootstrap_components as dbc


def top_nav() -> dbc.Navbar:
    return dbc.Navbar(
        dbc.Container(
            [
                dbc.NavbarBrand("The Fuller Monty: Relic Rush", className="fw-bold"),
                dbc.Nav(
                    [
                        dbc.NavItem(
                            dbc.Button(
                                "Logout",
                                id="btn-logout",
                                color="secondary",
                                outline=True,
                                size="sm",
                            )
                        )
                    ],
                    className="ms-auto",
                    navbar=True,
                ),
            ]
        ),
        color="dark",
        dark=True,
        className="mb-3",
    )
