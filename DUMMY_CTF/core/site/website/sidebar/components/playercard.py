import os
import reflex as rx

from website.auth_lib import LoginState
from website.auth_lib import PageAuthState, AuthCookie
from website.engine.task_conf import PlayerCardState
from website.engine.challenge import CondState


__all__ = ["player_card"]


# ---------------------------------------------------------
# ROOT COMPONENT
# ---------------------------------------------------------

def player_card() -> rx.Component:
    """Generates the complete player card."""
    shadow_color = PlayerCardState.team_color

    return rx.vstack(
        player_display(),
        rx.cond(PlayerCardState.enable_badges, badges_display()),
        rx.cond(
            PlayerCardState.enable_player_levels,
            levels_display(),
            progress_display(),
        ),
        class_name="player_card",
        style={"--player-card-shadow-color": shadow_color},
    )


# ---------------------------------------------------------
# PLAYER DISPLAY (Avatar + Name + Logout + Team)
# ---------------------------------------------------------

def player_display() -> rx.Component:
    background_color = PlayerCardState.team_color

    return rx.vstack(
        rx.hstack(
            # Avatar
            rx.link(
                rx.avatar(
                    src=AuthCookie.get_avatar_path,
                    fallback="?",
                    radius="full",
                    class_name="profile_picture",
                ),
                href=f"https://{os.getenv('DOMAIN')}/stats/",
                underline="none",
                is_external=False,
            ),

            # Username
            rx.vstack(
                rx.link(
                    rx.text(AuthCookie.get_username, class_name="username"),
                    href=f"https://{os.getenv('DOMAIN')}/stats/",
                    underline="none",
                    is_external=False,
                ),
            ),

            rx.spacer(),

            # Logout Button
            rx.tooltip(
                rx.box(
                    rx.icon("log-out", class_name="logout"),
                    as_="span",
                    role="button",
                    tab_index=0,  # must be int in Reflex 0.8
                    on_click=[
                        lambda: CondState.stop_code_server(),
                        lambda: CondState.stop_kali_server(),
                        LoginState.logout,
                        PageAuthState.reset_auth,
                    ],
                ),
                content="Abmelden",
                side="top",
                align="center",
            ),

            align_items="center",
            width="100%",
        ),

        # Teamname
        rx.cond(
            PlayerCardState.team_mode,
            rx.text(
                f"⚔️ {PlayerCardState.team_name}",
                class_name="teamname",
                style={"--team-name-background-color": background_color},
                width="95%",
                text_align="center",
            ),
        ),

        spacing="2",  # Radix spacing token (≈ 8px)
        width="100%",
        align_items="start",
    )


# ---------------------------------------------------------
# BADGES
# ---------------------------------------------------------

def badges_display() -> rx.Component:
    """Displays badges with tooltips."""
    return rx.hstack(
        rx.foreach(
            PlayerCardState.badge_indices,
            lambda i: rx.cond(
                PlayerCardState.badge_tooltips_text[i] != "",
                rx.tooltip(
                    rx.box(
                        rx.text(PlayerCardState.badge_emojis_text[i]),
                        as_="span",
                        display="inline-flex",
                        align_items="center",
                        justify_content="center",
                        margin_right="0.5rem",
                        pointer_events="auto",
                    ),
                    content=PlayerCardState.badge_tooltips_text[i],
                    side="top",
                    align="center",
                ),
                rx.box(
                    rx.text(PlayerCardState.badge_emojis_text[i]),
                    as_="span",
                    display="inline-flex",
                    align_items="center",
                    justify_content="center",
                    margin_right="0.5rem",
                    pointer_events="auto",
                ),
            ),
        ),
        spacing="3",  # Radix spacing token (≈ 12px)
        justify_content="center",
        width="100%",
        class_name="player_progress",
    )


# ---------------------------------------------------------
# PROGRESS BAR (when levels disabled)
# ---------------------------------------------------------

def progress_display() -> rx.Component:
    """Progress bar for the player's progress."""
    return rx.hstack(
        rx.link(
            rx.progress(
                value=PlayerCardState.percent,
                radius="full",
                height="1.5em",
            ),
            href=f"https://{os.getenv('SCR_DOMAIN')}/",
            width="100%",
            is_external=True,
        ),
        rx.text(f"{PlayerCardState.percent}%"),
        class_name="player_progress",
        spacing="2",
    )


# ---------------------------------------------------------
# LEVELS DISPLAY (if enabled)
# ---------------------------------------------------------

def levels_display() -> rx.Component:
    """Level progress bar + meta info + optional rank."""
    level_percent = PlayerCardState.level_percent
    remaining_points = PlayerCardState.remaining_points
    current_points = PlayerCardState.current_points
    next_level_points = PlayerCardState.next_level_points

    return rx.vstack(
        # Progress bar with tooltip
        rx.tooltip(
            rx.hstack(
                rx.link(
                    rx.progress(
                        value=level_percent,
                        radius="full",
                        height="1.5em",
                    ),
                    href=f"https://{os.getenv('SCR_DOMAIN')}/",
                    width="100%",
                    is_external=True,
                ),
                rx.text(f"{level_percent}%"),
                class_name="player_progress",
                spacing="2",
            ),
            content=f"{remaining_points} Punkte bis zum nächsten Level ({current_points}/{next_level_points})",
            side="top",
            align="center",
        ),

        # Level + Points row
        rx.hstack(
            rx.tooltip(
                rx.text(f"⚡ {PlayerCardState.player_level}", class_name="level_value"),
                content="Level",
                side="top",
                align="center",
            ),
            rx.spacer(),
            rx.tooltip(
                rx.text(f"✨ {PlayerCardState.player_points}", class_name="points_value"),
                content="Punkte",
                side="top",
                align="center",
            ),
            class_name="level_row",
            width="100%",
            spacing="2",
        ),

        # Rank
        rx.cond(
            PlayerCardState.player_rank != "",
            rx.tooltip(
                rx.text(
                    f"🎖️ {PlayerCardState.player_rank}",
                    class_name="rank_value",
                    style={"text-align": "center", "width": "100%"},
                ),
                content="Rang",
                side="top",
                align="center",
            ),
        ),

        # Level-up confetti
        rx.cond(
            PlayerCardState.level_up_trigger,
            rx.box(
                on_mount=[
                    rx.call_script("""
                        if (window.confettiReady && !window.confettiOnce) {
                            window.confettiOnce = true;
                            confetti({
                                particleCount: 200,
                                spread: 90,
                                origin: { y: 0.6 }
                            });
                        }
                    """),
                    PlayerCardState.reset_confetti,
                ]
            ),
            None,
        ),
        class_name="player_levels",
        spacing="3",
        width="100%",
    )
