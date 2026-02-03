"""
callbacks/game.py

Author: Jason Fuller
Date: 2026-01-25

Game page callbacks.

Purpose:
- Connect the Game View (UI) to the Game Controller and Game Model
- Render a 2D emoji grid showing player / relic / villain locations
- Handle movement + pickup actions
- Handle quitting the run back to /main
- Show a win/lose overlay when the run is completed

TODO:
Much of the code in here needs to pivot during enhancement 2. Some hard coded coords added
that should be in models and such.
"""

from dataclasses import asdict

import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, State, callback_context, html

from models.game import GameState, ROOMS, ITEMS, DIRECTIONS, VILLAIN_ROOM_ITEM

# Translate ROOMS to x/y coords for new grid.
ROOM_COORDS = {
    "Space Room": (1, 0),
    "Avengers Campus": (2, 0),
    "Mind Room": (3, 0),
    "Reality Room": (1, 1),
    "Power Room": (2, 1),
    "Time Room": (3, 1),
    "Soul Room": (1, 2),
    "Avengers Compound": (3, 2),
}

# Set grid size.
GRID_W = 5
GRID_H = 5

# Set icons for grid.
PLAYER_ICON = "🧑"
RELIC_ICON = "🗿"
VILLAIN_ICON = "👹"


def _tile(label, title, dim=False):
    return html.Div(
        label,
        title=title,
        style={
            "width": "44px",
            "height": "44px",
            "display": "flex",
            "alignItems": "center",
            "justifyContent": "center",
            "border": "1px solid #444",
            "borderRadius": "12px",
            "margin": "3px",
            "fontSize": "26px",
            "userSelect": "none",
            "opacity": 0.25 if dim else 1,
        },
    )


def _map_grid(state: GameState):
    """
    Render a 2D grid with the player and room contents.

    Rules:
    - Player appears in the current_room coordinate
    - Villain appears where ROOMS[room]['item'] == 'Villain'
    - Relic appears where a room contains an item that:
        * is not Villain
        * is not empty
        * is not already collected
    """
    room_by_xy = {xy: name for name, xy in ROOM_COORDS.items()}
    inv = set(state.inventory or [])

    rows = []
    for y in range(GRID_H):
        row = []
        for x in range(GRID_W):
            xy = (x, y)
            room_name = room_by_xy.get(xy)

            if not room_name:
                row.append(_tile("", f"({x},{y}) empty", dim=True))
                continue

            room = ROOMS.get(room_name, {})
            item = room.get("item", "")

            is_player = room_name == state.current_room
            is_villain = item == VILLAIN_ROOM_ITEM
            has_relic = bool(item) and item not in ("", VILLAIN_ROOM_ITEM) and item not in inv

            if is_player:
                label = PLAYER_ICON
            elif is_villain:
                label = VILLAIN_ICON
            elif has_relic:
                label = RELIC_ICON
            else:
                label = "·"

            row.append(_tile(label, f"{room_name} ({x},{y})"))
        rows.append(html.Div(row, style={"display": "flex"}))

    return html.Div(rows)


def _overlay(state: GameState):
    """
    Display an overlay when the player wins or loses.
    """
    if state.status not in ("completed", "game_over"):
        return html.Div()

    title = "YOU WIN!" if state.status == "completed" else "GAME OVER"
    subtitle = (
        "You recovered all stones before finding the villain."
        if state.status == "completed"
        else "You found the villain before collecting all stones."
    )

    return html.Div(
        [
            html.Div(
                dbc.Card(
                    dbc.CardBody(
                        [
                            html.H2(title, className="mb-2"),
                            html.P(subtitle, className="text-muted"),
                            html.Hr(),
                            dbc.Button("Back to Main", id="btn-overlay-main", color="primary", className="w-100"),
                        ]
                    ),
                    style={"maxWidth": "520px", "margin": "0 auto"},
                ),
                style={
                    "position": "fixed",
                    "top": 0,
                    "left": 0,
                    "right": 0,
                    "bottom": 0,
                    "display": "flex",
                    "alignItems": "center",
                    "justifyContent": "center",
                    "backgroundColor": "rgba(0,0,0,0.75)",
                    "zIndex": 9999,
                    "padding": "20px",
                },
            )
        ]
    )


def register_game_callbacks(app, game_controller):
    """
    Register game callbacks.

    Args:
        app: Dash app instance
        game_controller: GameController instance created in app.py
    """

    @app.callback(
        Output("store-game", "data", allow_duplicate=True),
        Input("move-up", "n_clicks"),
        Input("move-down", "n_clicks"),
        Input("move-left", "n_clicks"),
        Input("move-right", "n_clicks"),
        State("store-game", "data"),
        prevent_initial_call=True,
    )
    def move_player(nu, nd, nl, nr, game_data):
        if not game_data:
            return dash.no_update

        trig = callback_context.triggered[0]["prop_id"].split(".")[0]
        direction = {
            "move-up": "North",
            "move-down": "South",
            "move-left": "West",
            "move-right": "East",
        }.get(trig)

        if not direction:
            return dash.no_update

        state = GameState.from_dict(game_data)
        state = game_controller.move(state, direction)
        return asdict(state)

    @app.callback(
        Output("store-game", "data", allow_duplicate=True),
        Output("pickup-msg", "children"),
        Input("btn-pickup", "n_clicks"),
        State("store-game", "data"),
        prevent_initial_call=True,
    )
    def pickup(n_clicks_pickup, game_data):
        if not game_data or not n_clicks_pickup:
            return dash.no_update, dash.no_update

        state = GameState.from_dict(game_data)
        state = game_controller.pickup(state)

        color = "success" if "Collected" in (state.message or "") else "secondary"
        return asdict(state), dbc.Alert(state.message, color=color)

    @app.callback(
        Output("store-game", "data", allow_duplicate=True),
        Output("game-options-msg", "children"),
        Output("url", "pathname", allow_duplicate=True),
        Input("btn-quit", "n_clicks"),
        prevent_initial_call=True,
    )
    def quit_game(n_clicks_quit):
        if not n_clicks_quit:
            return dash.no_update, dash.no_update, dash.no_update
        return None, dbc.Alert("Quit to main screen.", color="secondary"), "/main"

    @app.callback(
        Output("url", "pathname", allow_duplicate=True),
        Output("store-game", "data", allow_duplicate=True),
        Input("btn-overlay-main", "n_clicks"),
        prevent_initial_call=True,
    )
    def overlay_back_to_main(n_clicks):
        if not n_clicks:
            return dash.no_update, dash.no_update
        return "/main", None

    @app.callback(
        Output("game-grid", "children"),
        Output("game-status", "children"),
        Output("game-collection", "children"),
        Output("game-controls", "children"),
        Output("game-hint", "children"),
        Output("room-info", "children"),
        Output("btn-pickup", "disabled"),
        Output("event-log", "children"),
        Output("result-overlay", "children"),
        Input("store-game", "data"),
    )
    def render_game(game_data):
        if not game_data:
            return (
                dbc.Alert("No game loaded. Go back to Main.", color="warning"),
                "",
                "",
                "",
                "",
                "",
                True,
                "",
                html.Div(),
            )

        state = GameState.from_dict(game_data)

        room = ROOMS[state.current_room]
        exits = [d for d in DIRECTIONS if d in room]
        item_here = room.get("item", "") or "None"

        grid = _map_grid(state)

        status = html.Div(
            [
                html.Div([html.Strong("Room: "), state.current_room]),
                html.Div([html.Strong("State: "), state.status]),
                html.Div([html.Strong("Message: "), state.message or "None"]),
            ]
        )

        got = set(state.inventory or [])
        coll = html.Div(
            [
                html.Strong("Stones:"),
                html.Ul(
                    [
                        html.Li(f"{'☑' if stone in got else '☐'}  {stone}")
                        for stone in sorted(ITEMS)
                    ]
                ),
            ]
        )

        controls = html.Div(
            [
                html.Div([html.Strong("Exits: "), ", ".join(exits) if exits else "None"]),
                html.Small("Move between rooms and collect stones.", className="text-muted"),
            ]
        )

        hint = dbc.Alert(
            "The villain is here." if item_here == VILLAIN_ROOM_ITEM else "Explore and collect stones.",
            color="danger" if item_here == VILLAIN_ROOM_ITEM else "secondary",
        )

        roominfo = html.Div(
            [
                html.Div([html.Strong("Room: "), state.current_room]),
                html.Div([html.Strong("Item: "), item_here]),
            ]
        )

        can_pickup_item = (
            item_here not in ("None", "", VILLAIN_ROOM_ITEM)
            and item_here not in (state.inventory or [])
        )

        event_feed = html.Ul([html.Li(m) for m in (state.event_log or [])[-10:]])
        overlay = _overlay(state)

        return (
            grid,
            status,
            coll,
            controls,
            hint,
            roominfo,
            (not can_pickup_item),
            event_feed,
            overlay,
        )
