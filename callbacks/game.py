"""
callbacks/game.py

Author: Jason Fuller

Game page callbacks.

Responsibilities:
- Connect the Game View to the GameController
- Render UI using controller-provided projections
- Handle user actions and navigation
- Display relic checklist (excluding villain)
- Render leaderboard results (with display names)
- Show final score + efficiency in finish modal
- Finalize and abandon sessions cleanly

Architectural Notes:
- UI never manipulates GameState directly
- Controller is authoritative for all state transitions
- store-game contains serialized GameState only
- Callbacks remain thin and orchestration-focused
"""

# ------------------------------------------------------------------
# Third-party imports
# ------------------------------------------------------------------

import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, State, callback_context, html

# ------------------------------------------------------------------
# Local application imports
# ------------------------------------------------------------------

from models.domain.game_state import GameState
from models.domain.status import GameStatus
from models.records.serialization import gamestate_from_dict, gamestate_to_dict
from utils.logger import get_logger


logger = get_logger(__name__)

# ------------------------------------------------------------------
# UI Rendering Helpers
# ------------------------------------------------------------------

ICONS = {
    "player": "🧑",
    "relic": "🗿",
    "villain": "👹",
    "empty": "·",
    "hidden": "",
}


def _tile(label: str, title: str, dim: bool = False):
    """
    Fully responsive square tile.
    Emoji scales proportionally with tile size.
    """

    return html.Div(
        label,
        title=title,
        style={
            "aspectRatio": "1 / 1",
            "width": "100%",
            "display": "flex",
            "alignItems": "center",
            "justifyContent": "center",
            "border": "1px solid #444",
            "borderRadius": "12px",
            "userSelect": "none",
            "opacity": 0.25 if dim else 1,

            # Emoji scales with viewport but is capped
            "fontSize": "clamp(32px, 6vw, 72px)",
        },
    )


def _map_grid(projection: dict):
    """
    Render only actual room coordinate bounds.
    Prevents phantom columns when grid origin != (0,0).

    Uses CSS Grid so tiles scale responsively.
    Max width capped at 500px.
    """

    rooms = projection["rooms"]

    room_by_xy = {
        (cell["x"], cell["y"]): (room_name, cell)
        for room_name, cell in rooms.items()
    }

    if not room_by_xy:
        return html.Div()

    xs = [x for (x, _) in room_by_xy.keys()]
    ys = [y for (_, y) in room_by_xy.keys()]

    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)

    columns = max_x - min_x + 1

    cells = []

    for y in range(min_y, max_y + 1):
        for x in range(min_x, max_x + 1):

            entry = room_by_xy.get((x, y))

            if not entry:
                cells.append(_tile("", f"({x},{y})", dim=True))
                continue

            room_name, cell = entry
            icon = ICONS.get(cell["render"], ICONS["empty"])
            dim = cell["render"] == "hidden"
            cells.append(_tile(icon, room_name, dim=dim))

    return html.Div(
        cells,
        style={
            "display": "grid",
            "gridTemplateColumns": f"repeat({columns}, 1fr)",
            "gap": "6px",
            "width": "100%",
            "maxWidth": "500px",
            "margin": "0 auto",
        },
    )


def _overlay(state: GameState, level_id: str, game_controller):
    """
    End-of-game overlay with score + efficiency summary.
    """

    if not state.status.is_terminal:
        return html.Div()

    is_win = state.status == GameStatus.COMPLETED

    try:
        level = game_controller._require_level(level_id)
        scoring = level.scoring
        optimal_moves = getattr(level, "optimal_moves", None)
        final_score = scoring.calculate(state, level)

    except Exception as e:
        logger.error("Overlay score calculation failed", error=str(e))
        final_score = "—"
        optimal_moves = None

    moves_used = state.move_count

    efficiency_display = "—"

    if is_win and optimal_moves and optimal_moves > 0:
        efficiency = (optimal_moves / moves_used) * 100
        efficiency = min(efficiency, 100.0)

        if round(efficiency, 1) == 100.0:
            efficiency_display = "PERFECT!"
        else:
            efficiency_display = f"{efficiency:.1f}%"

    title = "🏆 YOU WIN!" if is_win else "💀 GAME OVER"
    subtitle = (
        "You recovered all required relics."
        if is_win
        else "You encountered the villain too early."
    )

    return html.Div(
        dbc.Card(
            dbc.CardBody(
                [
                    html.H2(title),
                    html.P(subtitle),
                    html.Hr(),
                    html.Div(
                        [
                            html.H4(f"Score: {final_score}"),
                            html.Div(f"Moves Used: {moves_used}"),
                            html.Div(f"Optimal Moves: {optimal_moves or '—'}"),
                            html.Div(f"Efficiency: {efficiency_display}"),
                        ],
                        className="mb-3",
                    ),
                    dbc.Button(
                        "Back to Main",
                        id="btn-overlay-main",
                        className="w-100",
                    ),
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
        },
    )


# ------------------------------------------------------------------
# Callback Registration
# ------------------------------------------------------------------


def register_game_callbacks(app, game_controller, user_controller):
    logger.info("Registering game callbacks")

    # ==============================================================
    # MOVE PLAYER
    # ==============================================================

    @app.callback(
        Output("store-game", "data", allow_duplicate=True),
        Input("move-up", "n_clicks"),
        Input("move-down", "n_clicks"),
        Input("move-left", "n_clicks"),
        Input("move-right", "n_clicks"),
        State("store-game", "data"),
        State("store-auth", "data"),
        State("store-level", "data"),
        prevent_initial_call=True,
    )
    def move_player(up, down, left, right, game_data, auth, level_id):

        triggered_id = callback_context.triggered_id

        if not auth or not level_id:
            return dash.no_update

        direction_map = {
            "move-up": "north",
            "move-down": "south",
            "move-left": "west",
            "move-right": "east",
        }

        direction = direction_map.get(triggered_id)
        if not direction:
            return dash.no_update

        value = callback_context.triggered[0]["value"]
        if value in (None, 0):
            return dash.no_update

        save = game_controller.restore_run(user_email=auth["email"])
        state = save.state if save else gamestate_from_dict(game_data)

        state = game_controller.move(
            user_email=auth["email"],
            level_id=level_id,
            state=state,
            direction=direction,
        )

        return gamestate_to_dict(state)

    # ==============================================================
    # RENDER GAME
    # ==============================================================

    @app.callback(
        Output("game-grid", "children"),
        Output("event-log", "children"),
        Output("game-status", "children"),
        Output("game-collection", "children"),
        Output("game-leaderboards", "children"),
        Output("result-overlay", "children"),
        Input("store-game", "data"),
        State("store-level", "data"),
    )
    def render_game(game_data, level_id):

        if not game_data:
            return "", "", "", "", "", html.Div()

        state = gamestate_from_dict(game_data)

        projection = game_controller.get_level_projection(
            level_id=level_id,
            state=state,
        )

        grid = _map_grid(projection)

        log_items = html.Ul(
            [html.Li(m) for m in state.event_log[-10:]],
            className="mb-0",
        )

        status = html.Div(
            [
                html.Div(f"Moves: {state.move_count}"),
                html.Div(f"Status: {state.status.value.replace('_', ' ').title()}"),
            ],
            className="small",
        )

        # Relic checklist

        try:
            level = game_controller._require_level(level_id)

            relic_names = []
            for room in level.map.rooms.values():
                item = room.item
                if not item:
                    continue
                if item.__class__.__name__.lower() == "villain":
                    continue
                relic_names.append(item.name)

            relic_names = sorted(set(relic_names))

            checklist = []
            for relic in relic_names:
                collected = relic in state.collected_items
                icon = "🟢" if collected else "⚪"
                checklist.append(html.Div(f"{icon} 🗿 {relic}"))

            inventory = html.Div(checklist)

        except Exception as e:
            logger.error("Relic rendering failed", error=str(e))
            inventory = html.Div("Relics unavailable.", className="text-muted")

        # Leaderboard

        try:
            top_scores = game_controller.get_leaderboard(
                level_id=level_id,
                limit=5,
            )

            if not top_scores:
                leaderboard = html.Div("No scores yet.", className="text-muted")
            else:

                name_cache = {}

                def resolve_name(email: str) -> str:
                    if email in name_cache:
                        return name_cache[email]
                    try:
                        name = user_controller.get_display_name(email)
                    except Exception:
                        name = None
                    resolved = name.strip() if name else "<unknown>"
                    name_cache[email] = resolved
                    return resolved

                leaderboard = html.Ul(
                    [
                        html.Li(
                            f"{resolve_name(r.user_email)} — "
                            f"{r.score} pts ({r.moves} moves)"
                        )
                        for r in top_scores
                    ],
                    className="mb-0",
                )

        except Exception as e:
            logger.error("Leaderboard rendering failed", error=str(e))
            leaderboard = html.Div("Leaderboard unavailable.", className="text-muted")

        overlay = _overlay(state, level_id, game_controller)

        return (
            grid,
            log_items,
            status,
            inventory,
            leaderboard,
            overlay,
        )

    # ==============================================================
    # QUIT > MAIN
    # ==============================================================

    @app.callback(
        Output("url", "pathname", allow_duplicate=True),
        Output("store-game", "data", allow_duplicate=True),
        Output("store-level", "data", allow_duplicate=True),
        Input("btn-quit", "n_clicks"),
        prevent_initial_call=True,
    )
    def quit_game(n_clicks):
        if not n_clicks:
            return dash.no_update, dash.no_update, dash.no_update

        logger.info("Quit game requested")
        return "/main", None, None

    # ==============================================================
    # OVERLAY > MAIN
    # ==============================================================

    @app.callback(
        Output("url", "pathname", allow_duplicate=True),
        Output("store-game", "data", allow_duplicate=True),
        Output("store-level", "data", allow_duplicate=True),
        Input("btn-overlay-main", "n_clicks"),
        prevent_initial_call=True,
    )
    def back_to_main(n_clicks):
        if not n_clicks:
            return dash.no_update, dash.no_update, dash.no_update

        logger.info("Navigating back to main screen (overlay)")
        return "/main", None, None
