"""
callbacks/main.py

Author: Jason Fuller

Main page callbacks.

Responsibilities:
- Populate landing page welcome state
- Detect active saved sessions
- Resume existing games
- Start new games safely
- Confirm destructive overwrite actions
- Render unified global leaderboard (Top 10 overall)
- Resolve display names via UserController
- Redirect users appropriately

Architectural Notes:
- Leaderboard is aggregated across all difficulties
- Harder levels naturally rank higher due to score weighting
- Display names are resolved dynamically via user lookup
- Emails are never shown in leaderboard output
"""

# ------------------------------------------------------------------
# Third-party imports
# ------------------------------------------------------------------

from dash import Input, Output, State, no_update, callback_context
from dash import html

# ------------------------------------------------------------------
# Local application imports
# ------------------------------------------------------------------

from models.records.serialization import gamestate_to_dict
from utils.logger import get_logger


logger = get_logger(__name__)


def register_main_callbacks(app, game_controller, user_controller):
    """
    Register callbacks for the main page.
    """

    # ==============================================================
    # WELCOME + RESUME + UNIFIED LEADERBOARD
    # ==============================================================

    @app.callback(
        Output("main-welcome", "children"),
        Output("btn-resume-game", "disabled"),
        Output("resume-details", "children"),
        Output("main-leaderboard", "children"),
        Input("store-auth", "data"),
    )
    def render_main(auth_data):

        if not auth_data:
            return no_update, True, "", ""

        display_name = (auth_data.get("display_name") or "").strip()
        user_email = auth_data.get("email")
        welcome = f"Welcome, {display_name}" if display_name else "Welcome"

        # ----------------------------------------------------------
        # Resume State
        # ----------------------------------------------------------

        if not user_email:
            return welcome, True, "", ""

        if game_controller.has_active_run(user_email=user_email):
            save = game_controller.restore_run(user_email=user_email)
            resume_disabled = False
            resume_details = (
                f"Level: {save.level_id} · Moves: {save.state.move_count}"
            )
        else:
            resume_disabled = True
            resume_details = "No active game to resume."

        # ----------------------------------------------------------
        # Unified Leaderboard (Top 10 Overall)
        # ----------------------------------------------------------

        try:
            level_ids = [
                "level_easy",
                "level_medium",
                "level_hard",
            ]

            combined_results = []

            for level_id in level_ids:
                results = game_controller.get_leaderboard(
                    level_id=level_id,
                    limit=10,
                )
                combined_results.extend(results)

            # Sort descending by score
            combined_results.sort(key=lambda r: r.score, reverse=True)

            top_results = combined_results[:10]

            if not top_results:
                leaderboard = html.Div(
                    "No scores yet.",
                    className="text-muted small",
                )
            else:

                # Cache display name lookups per render
                name_cache = {}

                def resolve_name(email: str) -> str:
                    if email in name_cache:
                        return name_cache[email]

                    try:
                        name = user_controller.get_display_name(email)
                    except Exception as e:
                        logger.error(
                            "Display name lookup failed",
                            email=email,
                            error=str(e),
                        )
                        name = None

                    resolved = name.strip() if name else "<unknown>"
                    name_cache[email] = resolved
                    return resolved

                leaderboard = html.Ol(
                    [
                        html.Li(
                            f"{resolve_name(r.user_email)} — "
                            f"{r.score} pts "
                            f"({r.level_id.replace('level_', '').title()}, "
                            f"{r.moves} moves)"
                        )
                        for r in top_results
                    ],
                    className="small mb-0",
                )

        except Exception as e:
            logger.error("Leaderboard load failed", error=str(e))
            leaderboard = html.Div(
                "Leaderboard unavailable.",
                className="text-muted small",
            )

        return (
            welcome,
            resume_disabled,
            resume_details,
            leaderboard,
        )

    # ==============================================================
    # RESUME GAME
    # ==============================================================

    @app.callback(
        Output("store-game", "data", allow_duplicate=True),
        Output("store-level", "data", allow_duplicate=True),
        Output("url", "pathname", allow_duplicate=True),
        Output("main-actions-msg", "children", allow_duplicate=True),
        Input("btn-resume-game", "n_clicks"),
        State("store-auth", "data"),
        prevent_initial_call=True,
    )
    def resume_game(n_clicks, auth_data):

        if not n_clicks:
            return no_update, no_update, no_update, no_update

        if not auth_data:
            return no_update, no_update, "/login", "Invalid session."

        user_email = auth_data.get("email")
        if not user_email:
            return no_update, no_update, "/login", "Invalid session."

        save = game_controller.restore_run(user_email=user_email)
        if not save:
            return no_update, no_update, no_update, "No active game to resume."

        logger.info("Resuming game", user_email=user_email)

        return (
            gamestate_to_dict(save.state),
            save.level_id,
            "/game",
            "",
        )

    # ==============================================================
    # NEW GAME HANDLER
    # ==============================================================

    @app.callback(
        Output("modal-confirm-new-game", "is_open"),
        Output("store-pending-level", "data"),
        Output("store-game", "data"),
        Output("store-level", "data"),
        Output("url", "pathname"),
        Input("btn-new-easy", "n_clicks"),
        Input("btn-new-medium", "n_clicks"),
        Input("btn-new-hard", "n_clicks"),
        State("store-auth", "data"),
        prevent_initial_call=True,
    )
    def handle_new_game(n_easy, n_medium, n_hard, auth_data):

        ctx = callback_context

        if not ctx.triggered:
            return no_update, no_update, no_update, no_update, no_update

        trigger_id = ctx.triggered_id

        if not trigger_id or not auth_data:
            return no_update, no_update, no_update, no_update, no_update

        user_email = auth_data.get("email")
        if not user_email:
            return no_update, no_update, no_update, no_update, "/login"

        level_map = {
            "btn-new-easy": ("level_easy", n_easy),
            "btn-new-medium": ("level_medium", n_medium),
            "btn-new-hard": ("level_hard", n_hard),
        }

        entry = level_map.get(trigger_id)

        if not entry:
            return no_update, no_update, no_update, no_update, no_update

        level_id, click_value = entry

        if click_value in (None, 0):
            return no_update, no_update, no_update, no_update, no_update

        if game_controller.has_active_run(user_email=user_email):
            return True, level_id, no_update, no_update, no_update

        state = game_controller.start_new_run(
            user_email=user_email,
            level_id=level_id,
        )

        return (
            False,
            None,
            gamestate_to_dict(state),
            level_id,
            "/game",
        )

    # ==============================================================
    # CONFIRM OVERWRITE
    # ==============================================================

    @app.callback(
        Output("store-game", "data", allow_duplicate=True),
        Output("store-level", "data", allow_duplicate=True),
        Output("url", "pathname", allow_duplicate=True),
        Output("modal-confirm-new-game", "is_open", allow_duplicate=True),
        Input("btn-confirm-new-game", "n_clicks"),
        State("store-pending-level", "data"),
        State("store-auth", "data"),
        prevent_initial_call=True,
    )
    def confirm_new_game(n_clicks, pending_level, auth_data):

        if not n_clicks or not pending_level or not auth_data:
            return no_update, no_update, no_update, no_update

        user_email = auth_data.get("email")
        if not user_email:
            return no_update, no_update, "/login", False

        state = game_controller.restart_run(
            user_email=user_email,
            level_id=pending_level,
        )

        return (
            gamestate_to_dict(state),
            pending_level,
            "/game",
            False,
        )

    # ==============================================================
    # CANCEL NEW GAME
    # ==============================================================

    @app.callback(
        Output("modal-confirm-new-game", "is_open", allow_duplicate=True),
        Input("btn-cancel-new-game", "n_clicks"),
        prevent_initial_call=True,
    )
    def cancel_new_game(n_clicks):
        if not n_clicks:
            return no_update
        return False
