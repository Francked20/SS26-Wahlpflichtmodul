import os
import reflex as rx
from .websocket_reader import ScoreBoardState

scoreboard_title = os.getenv("SCOREBOARD_TITLE", "CTF@TCV - Scoreboard")


# ---------------------------------------------------------
#  TUG OF WAR (TEAMS)
# ---------------------------------------------------------
def tug_of_war():
    return rx.vstack(
        rx.text("⚖️", font_size="1.5em", text_align="center"),

        rx.hstack(
            rx.progress(
                value=ScoreBoardState.tug_pcts[0],
                max=100,
                size="3",
                class_name="team_progress",
                style={
                    "width": "100%",
                    "transform": "scaleX(-1)",
                    "borderTopLeftRadius": "0",
                    "borderBottomLeftRadius": "0",
                    "--progress-fill-color": ScoreBoardState.top_two_colors[0],
                    "flex": 1,
                },
            ),
            rx.progress(
                value=ScoreBoardState.tug_pcts[1],
                max=100,
                size="3",
                class_name="team_progress",
                style={
                    "width": "100%",
                    "borderTopLeftRadius": "0",
                    "borderBottomLeftRadius": "0",
                    "--progress-fill-color": ScoreBoardState.top_two_colors[1],
                    "flex": 1,
                },
            ),
            width="100%",
            spacing="0",
        ),

        rx.hstack(
            rx.text(
                f"{ScoreBoardState.top_two_teams[0]} ({ScoreBoardState.top_two_scores[0]})",
                text_align="right",
                style={"flex": 1},
            ),
            rx.text(
                f"{ScoreBoardState.top_two_teams[1]} ({ScoreBoardState.top_two_scores[1]})",
                text_align="left",
                style={"flex": 1},
            ),
            spacing="2",
            width="100%",
        ),

        spacing="1",
        align_items="center",
        width="100%",
        style={"paddingTop": "0.5em"},
    )


# ---------------------------------------------------------
#  BOTTOM TEAM BARS
# ---------------------------------------------------------
def render_bottom_team_bar(index: int):
    return rx.hstack(
        rx.text(
            f"{ScoreBoardState.bottom_teams[index]} ({ScoreBoardState.bottom_scores[index]})",
            text_align="left",
            style={"width": "12em"},
        ),
        rx.progress(
            value=ScoreBoardState.bottom_pcts[index],
            max=100,
            size="3",
            class_name="team_progress",
            style={
                "width": "100%",
                "--progress-fill-color": ScoreBoardState.bottom_colors[index],
            },
        ),
        spacing="1",
        width="100%",
        align_items="center",
    )


def bottom_team_bars():
    return rx.vstack(
        rx.foreach(
            ScoreBoardState.bottom_teams,
            lambda team, idx: render_bottom_team_bar(idx),
        ),
        spacing="1",
        width="100%",
        style={"paddingTop": "1em"},
    )


# ---------------------------------------------------------
#  TEAM SCOREBOARD
# ---------------------------------------------------------
def render_team_scoreboard(team_name, player_var, rank_var, color_var):
    return rx.vstack(
        rx.heading(f"{team_name} Scoreboard", size="5"),

        rx.hstack(
            rx.cond(
                ScoreBoardState.show_position,
                rx.text("Pos.", style={"width": "4em"}, font_weight="bold"),
            ),
            rx.cond(
                ScoreBoardState.show_name,
                rx.text("Name", style={"width": "10em"}, font_weight="bold"),
            ),
            rx.cond(
                ScoreBoardState.show_email,
                rx.text("Email", style={"width": "20em"}, font_weight="bold"),
            ),
            rx.cond(
                ScoreBoardState.show_points,
                rx.text("Punkte", style={"width": "6em"}, font_weight="bold"),
            ),
            rx.cond(
                ScoreBoardState.show_solved,
                rx.text("Erledigt", style={"width": "7em"}, font_weight="bold"),
            ),
            rx.cond(
                ScoreBoardState.show_badges,
                rx.text("Abzeichen", style={"width": "30em"}, font_weight="bold"),
            ),
            rx.cond(
                ScoreBoardState.show_first_blood,
                rx.text("First Blood", style={"width": "7em"}, font_weight="bold"),
            ),
            spacing="1",
            style={"background": color_var, "color": "white", "padding": "0.5em"},
            width="100%",
        ),

        rx.foreach(
            player_var,
            lambda p, i: rx.hstack(
                rx.cond(
                    ScoreBoardState.show_position,
                    rx.text(
                        rx.match(
                            rank_var[i],
                            (1, "🥇"),
                            (2, "🥈"),
                            (3, "🥉"),
                            f"{rank_var[i]}.",
                        ),
                        style={"width": "4em"},
                    ),
                ),
                rx.cond(
                    ScoreBoardState.show_name,
                    rx.text(p["username"], style={"width": "10em"}),
                ),
                rx.cond(
                    ScoreBoardState.show_email,
                    rx.text(p["email"], style={"width": "20em"}),
                ),
                rx.cond(
                    ScoreBoardState.show_points,
                    rx.text(p["points"], style={"width": "6em"}),
                ),
                rx.cond(
                    ScoreBoardState.show_solved,
                    rx.text(p["challenges_solved"], style={"width": "7em"}),
                ),
                rx.cond(
                    ScoreBoardState.show_badges,
                    rx.text(p["badges"], style={"width": "30em"}),
                ),
                rx.cond(
                    ScoreBoardState.show_first_blood,
                    rx.text(p["first_solves"], style={"width": "7em"}),
                ),
                spacing="1",
                style={"padding": "0.5em", "borderBottom": "1px solid lightgray"},
                width="100%",
            ),
        ),

        spacing="1",
        style={"padding": "1em", "borderRadius": "0.5em"},
        width="100%",
    )


def all_team_scoreboards():
    return rx.vstack(
        rx.foreach(
            ScoreBoardState.team_configs,
            lambda cfg: render_team_scoreboard(
                cfg["team"],
                ScoreBoardState.sorted_map_filtered[cfg["team"]],
                ScoreBoardState.rank_map_filtered[cfg["team"]],
                cfg["color"],
            ),
        ),
        spacing="2",
        style={"padding": "1em"},
        width="100%",
    )


# ---------------------------------------------------------
#  TUG OF WAR (PLAYERS)
# ---------------------------------------------------------
def tug_of_war_players():
    return rx.vstack(
        rx.text("⚖️", font_size="1.5em", text_align="center"),

        rx.hstack(
            rx.progress(
                value=ScoreBoardState.top_two_pcts[0],
                max=100,
                size="3",
                class_name="team_progress",
                style={
                    "width": "100%",
                    "transform": "scaleX(-1)",
                    "borderTopLeftRadius": "0",
                    "borderBottomLeftRadius": "0",
                    "--progress-fill-color": "gold",
                    "flex": 1,
                },
            ),
            rx.progress(
                value=ScoreBoardState.top_two_pcts[1],
                max=100,
                size="3",
                class_name="team_progress",
                style={
                    "width": "100%",
                    "borderTopLeftRadius": "0",
                    "borderBottomLeftRadius": "0",
                    "--progress-fill-color": "silver",
                    "flex": 1,
                },
            ),
            width="100%",
            spacing="0",
        ),

        rx.hstack(
            rx.text(
                f"{ScoreBoardState.top_two_players[0]} ({ScoreBoardState.top_two_player_scores[0]})",
                text_align="right",
                style={"flex": 1},
            ),
            rx.text(
                f"{ScoreBoardState.top_two_players[1]} ({ScoreBoardState.top_two_player_scores[1]})",
                text_align="left",
                style={"flex": 1},
            ),
            spacing="2",
            width="100%",
        ),

        spacing="1",
        align_items="center",
        width="100%",
        style={"paddingTop": "0.5em"},
    )


# ---------------------------------------------------------
#  BOTTOM PLAYER BARS
# ---------------------------------------------------------
def render_bottom_player_bar(index: int):
    return rx.hstack(
        rx.text(
            f"{ScoreBoardState.solo_bottom_players[index]} ({ScoreBoardState.solo_bottom_scores[index]})",
            text_align="left",
            style={"width": "12em"},
        ),
        rx.progress(
            value=ScoreBoardState.solo_bottom_pcts[index],
            max=100,
            size="3",
            class_name="team_progress",
            style={
                "width": "100%",
                "--progress-fill-color": "#CD7F32",
            },
        ),
        spacing="1",
        width="100%",
        align_items="center",
    )


def bottom_player_bars():
    return rx.vstack(
        rx.foreach(
            ScoreBoardState.solo_bottom_players,
            lambda player, idx: render_bottom_player_bar(idx),
        ),
        spacing="1",
        width="100%",
        style={"paddingTop": "1em"},
    )


# ---------------------------------------------------------
#  SOLO SCOREBOARD
# ---------------------------------------------------------
def render_solo_scoreboard():
    return rx.vstack(
        rx.heading("Spieler-Scoreboard", size="5"),

        rx.hstack(
            rx.cond(
                ScoreBoardState.show_position,
                rx.text("Pos.", style={"width": "4em"}, font_weight="bold"),
            ),
            rx.cond(
                ScoreBoardState.show_name,
                rx.text("Name", style={"width": "10em"}, font_weight="bold"),
            ),
            rx.cond(
                ScoreBoardState.show_email,
                rx.text("Email", style={"width": "20em"}, font_weight="bold"),
            ),
            rx.cond(
                ScoreBoardState.show_points,
                rx.text("Punkte", style={"width": "6em"}, font_weight="bold"),
            ),
            rx.cond(
                ScoreBoardState.show_solved,
                rx.text("Erledigt", style={"width": "7em"}, font_weight="bold"),
            ),
            rx.cond(
                ScoreBoardState.show_badges,
                rx.text("Abzeichen", style={"width": "30em"}, font_weight="bold"),
            ),
            rx.cond(
                ScoreBoardState.show_first_blood,
                rx.text("First Blood", style={"width": "7em"}, font_weight="bold"),
            ),
            spacing="1",
            style={"background": "#8C6239", "color": "white", "padding": "0.5em"},
            width="100%",
        ),

        rx.foreach(
            ScoreBoardState.solo_sorted_filtered,
            lambda p, i: rx.hstack(
                rx.cond(
                    ScoreBoardState.show_position,
                    rx.text(
                        rx.match(
                            ScoreBoardState.solo_ranks_filtered[i],
                            (1, "🥇"),
                            (2, "🥈"),
                            (3, "🥉"),
                            f"{ScoreBoardState.solo_ranks_filtered[i]}.",
                        ),
                        style={"width": "4em"},
                    ),
                ),
                rx.cond(
                    ScoreBoardState.show_name,
                    rx.text(p["username"], style={"width": "10em"}),
                ),
                rx.cond(
                    ScoreBoardState.show_email,
                    rx.text(p["email"], style={"width": "20em"}),
                ),
                rx.cond(
                    ScoreBoardState.show_points,
                    rx.text(p["points"], style={"width": "6em"}),
                ),
                rx.cond(
                    ScoreBoardState.show_solved,
                    rx.text(p["challenges_solved"], style={"width": "7em"}),
                ),
                rx.cond(
                    ScoreBoardState.show_badges,
                    rx.text(p["badges"], style={"width": "30em"}),
                ),
                rx.cond(
                    ScoreBoardState.show_first_blood,
                    rx.text(p["first_solves"], style={"width": "7em"}),
                ),
                spacing="1",
                style={"padding": "0.5em", "borderBottom": "1px solid lightgray"},
                width="100%",
            ),
        ),

        spacing="1",
        style={"padding": "1em", "borderRadius": "0.5em"},
        width="100%",
    )


# ---------------------------------------------------------
#  MAIN TABLE
# ---------------------------------------------------------
def main_table() -> rx.Component:
    return rx.vstack(
        rx.center(
            rx.text(
                f"{scoreboard_title}",
                style={
                    "background": "linear-gradient(90deg, #04B486, #00FFFF)",
                    "WebkitBackgroundClip": "text",
                    "WebkitTextFillColor": "transparent",
                    "marginBottom": "20px",
                    "fontSize": "2.5em",
                    "fontWeight": "bold",
                    "textAlign": "center",
                },
            ),
            width="100%",
        ),

        rx.cond(
            ScoreBoardState.is_ready,
            rx.cond(
                ScoreBoardState.team_event_mode,

                # TEAM MODE
                rx.vstack(
                    rx.cond(
                        ScoreBoardState.show_tug_of_war,
                        rx.box(
                            rx.heading("Tauziehen der besten Teams", size="7"),
                            tug_of_war(),
                            width="100%",
                            spacing="1",
                            style={"padding": "1em"},
                        ),
                    ),
                    rx.cond(
                        ScoreBoardState.show_further_progress_bars
                        & ScoreBoardState.more_than_two_teams,
                        rx.box(
                            rx.heading("weitere Teams im Vergleich zum besten Team", size="7"),
                            bottom_team_bars(),
                            width="100%",
                            spacing="1",
                            style={"padding": "1em"},
                        ),
                    ),
                    rx.cond(
                        ScoreBoardState.show_scoreboards,
                        rx.box(
                            rx.heading("Team Scoreboards", size="7"),
                            all_team_scoreboards(),
                            width="100%",
                            spacing="1",
                            style={"padding": "1em"},
                        ),
                    ),
                    rx.spacer(),
                    width="100%",
                ),

                # SOLO MODE
                rx.vstack(
                    rx.cond(
                        ScoreBoardState.show_tug_of_war,
                        rx.box(
                            rx.heading("Tauziehen der besten Spieler", size="7"),
                            tug_of_war_players(),
                            width="100%",
                            spacing="1",
                            style={"padding": "1em"},
                        ),
                    ),
                    rx.cond(
                        ScoreBoardState.show_further_progress_bars
                        & ScoreBoardState.solo_bottom_players,
                        rx.box(
                            rx.heading("Weitere Spieler im Vergleich zum besten Spieler", size="7"),
                            bottom_player_bars(),
                            width="100%",
                            spacing="1",
                            style={"padding": "1em"},
                        ),
                    ),
                    rx.cond(
                        ScoreBoardState.show_scoreboards,
                        render_solo_scoreboard(),
                    ),
                    spacing="2",
                    width="100%",
                ),
            ),
        ),

        spacing="2",
        width="100%",
        style={"padding": "2em"},
    )
