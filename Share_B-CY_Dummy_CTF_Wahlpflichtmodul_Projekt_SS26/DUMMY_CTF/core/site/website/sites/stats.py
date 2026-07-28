import reflex as rx
from website.auth_lib import AuthCookie, BackendRequests
import reflex_chakra as rc
from website.engine.site import AbstractSiteBuilder
from website.engine.challenge import *
from website.engine.task_conf import PlayerCardState
from urllib.parse import quote
from website.unlock_settings import *
from website.logger import create_logger
from website.engine.challenge import *
from datetime import datetime
from zoneinfo import ZoneInfo

logger = create_logger("stats")

# Damit Monatsnamen deutsch sind:
GERMAN_MONTHS = {
    1: "Jan", 2: "Feb", 3: "Mrz", 4: "Apr", 5: "Mai", 6: "Jun",
    7: "Jul", 8: "Aug", 9: "Sep", 10: "Okt", 11: "Nov", 12: "Dez"
}

GERMAN_TZ = ZoneInfo("Europe/Berlin")


def format_finish_time(ts: str) -> str:
    if not ts:
        return ""
    try:
        dt = datetime.fromisoformat(ts)
        # Falls keine tzinfo vorhanden ist → als UTC interpretieren
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=ZoneInfo("UTC"))
        # In deutsche Zeit umwandeln
        dt_local = dt.astimezone(GERMAN_TZ)
        return f"{dt_local.day:02d} {GERMAN_MONTHS[dt_local.month]} {dt_local.year % 100:02d} {dt_local.hour:02d}:{dt_local.minute:02d}:{dt_local.second:02d}"
    except Exception:
        return ts


class StatsPageState(AuthCookie, BackendRequests):
    points: int = 0
    rank: str = ""
    level: int = 0
    level_percent: int = 0
    first_solves: int = 0
    challenges: list[dict] = []
    badges: list[dict] = []

    show_finish_time: bool = False
    show_day: bool = False
    show_task: bool = False
    show_points: bool = False
    show_tries: bool = False
    show_hints: bool = False
    show_resets: bool = False
    show_first_blood: bool = False

    team: str = ""
    is_team_leader: bool = False

    @rx.var
    def badge_indices(self) -> list[int]:
        return list(range(len(self.badges)))

    @rx.var
    def badge_emojis_text(self) -> list[str]:
        return [str(b.get("emoji", "")) for b in self.badges]

    @rx.var
    def badge_tooltips_text(self) -> list[str]:
        return [str(b.get("tooltip", "")) for b in self.badges]

    async def load_all_stats(self) -> None:
        safe_username = quote(self.get_username, safe="")

        try:
            # 1. Level / Punkte / Rang laden
            resp = await self.get(f"/user/{safe_username}/level", auth=self.auth_cookie)
            data = resp.json()

            self.points = int(data.get("points", 0))
            self.rank = str(data.get("rank", "")) or ""
            self.level = int(data.get("level", 1))
            self.level_percent = int(data.get("level_percent", 0))
            self.first_solves = int(data.get("first_solves", 0))

            raw_badges = data.get("badges", []) or []

            if isinstance(raw_badges, dict):
                raw_badges = [raw_badges]

            # Fallbacks für alte Formate
            if isinstance(raw_badges, str):
                self.badges = [{"emoji": e, "tooltip": ""} for e in list(raw_badges)]
            elif raw_badges and all(isinstance(b, str) for b in raw_badges):
                self.badges = [{"emoji": e, "tooltip": ""} for e in raw_badges]
            else:
                # Erwartetes neues Format: Liste von Dicts mit emoji/tooltip
                # Stelle sicher, dass tooltip bei fehlendem Key ein leerer String ist.
                self.badges = [{"emoji": b["emoji"], "tooltip": b.get("tooltip", "")} for b in raw_badges]

            self.team = data.get("team", "") or ""
            self.is_team_leader = bool(data.get("team_leader", False))

        except Exception as e:
            logger.warning(f"[StatsPageState] load_all_stats (level) failed: {e}")

        # 2. Challenges laden
        try:
            stats_resp = await self.get(f"/user/{safe_username}/get_stats", auth=self.auth_cookie)
            stats_raw = stats_resp.json()
            challenges: list[dict] = []

            for detail in stats_raw:
                if detail.get("solved"):
                    day_display = detail.get("day_description") if detail.get("day_description") else detail.get("day")
                    task_display = detail.get("task_description") if detail.get("task_description") else detail.get("task")

                    challenges.append({
                        "day": day_display,
                        "task": task_display,
                        "tries": detail.get("tries"),
                        "resets": detail.get("resets"),
                        "hints": detail.get("hints_gotten", 0),
                        "points": f"✨ {detail.get('points_earned')}/{detail.get('points_to_get')}",
                        "finish_time": format_finish_time(detail.get("finish_time")),
                        "first_blood": "🩸" if detail.get("first_blood") else "",
                    })

            self.challenges = challenges

        except Exception as e:
            logger.warning(f"[StatsPageState] load_all_stats (get_stats) failed: {e}")

        # 3. Sichtbarkeits-Optionen laden
        try:
            opts_resp = await self.get("/admin/event/stats/options")
            opts = opts_resp.json()
            self.show_finish_time = opts.get("finish_time", False)
            self.show_day = opts.get("day", False)
            self.show_task = opts.get("task", False)
            self.show_points = opts.get("points", False)
            self.show_tries = opts.get("tries", False)
            self.show_hints = opts.get("hints", False)
            self.show_resets = opts.get("resets", False)
            self.show_first_blood = opts.get("first_blood", False)
        except Exception as e:
            logger.warning(f"[StatsPageState] load_all_stats (options) failed: {e}")

class StatsPage(AbstractSiteBuilder):
    def page(self) -> rx.Component:
        return rx.center(
            rx.vstack(
                rx.spacer(),
                # Überschrift mit Emoji zentriert
                rx.hstack(
                    rx.heading(
                        f"Statistik von {AuthCookie.get_username}",
                        size="8",
                        style={
                            "background": "linear-gradient(90deg, #04B486, #00FFFF)",
                            "WebkitBackgroundClip": "text",
                            "WebkitTextFillColor": "transparent",
                            "marginBottom": "0px",
                        }
                    ),
                    rx.text("📊", size="8", align_self="center"),
                    align_items="center",
                    justify_content="center",
                    spacing="1",
                    width="100%",
                    style={"marginBottom": "24px"}
                ),

                rx.cond(
                    PlayerCardState.enable_player_levels,
                    # Box mit Glassmorph-Optik
                    rx.box(
                        rx.vstack(
                            rx.heading("Playercard", size="6", margin_bottom="1rem", align="left"),
                            # Stat Widgets mittig
                            rx.hstack(
                                rc.stat(
                                    rc.stat_label("⚡ Level"),
                                    rc.stat_number(StatsPageState.level),
                                    rc.stat_help_text(f"{StatsPageState.level_percent}%"),
                                    style={"minWidth": "80px", "textAlign": "center"},
                                ),
                                rc.stat(
                                    rc.stat_label("✨ Punkte"),
                                    rc.stat_number(StatsPageState.points),
                                    style={"minWidth": "80px", "textAlign": "center"},
                                ),
                                rc.stat(
                                    rc.stat_label("🩸"),
                                    rc.stat_number(StatsPageState.first_solves),
                                    style={"minWidth": "80px", "textAlign": "center"},
                                ),

                                rx.spacer(min_width="20px"),

                                # Rang nur anzeigen, wenn nicht leer
                                rx.cond(
                                    StatsPageState.rank != "",
                                    rc.stat(
                                        rc.stat_label("🎖️ Rang"),
                                        rc.stat_number(
                                            StatsPageState.rank,
                                            style={ "maxWidth": "300px", "whiteSpace": "normal", "textAlign": "center", },
                                        ),
                                        style={"minWidth": "150px"},
                                    ),
                                ),

                                rx.spacer(min_width="20px"),

                                # Team nur anzeigen, wenn gesetzt
                                rx.cond(
                                    StatsPageState.team != "",
                                    rc.stat(
                                        rc.stat_label("⚔️ Team"),
                                        rc.stat_number(
                                            StatsPageState.team,
                                            style={ "maxWidth": "300px", "whiteSpace": "normal", "textAlign": "center", },
                                        ),
                                        # kleiner Zusatztext falls Team Leader
                                        rx.cond(
                                            StatsPageState.is_team_leader,
                                            rc.stat_help_text("Team Leader"),
                                        ),
                                        style={"minWidth": "150px"},
                                    ),
                                ),
                                justify="center",
                                align_items="center",
                                spacing="9",
                                width="100%",
                            ),
                        ),
                        style={
                            "maxWidth": "1400px",
                            "width": ["100%", "95%", "85%"],
                            "margin": "0 auto",
                            "padding": "2rem",
                            "borderRadius": "12px",
                            "backgroundColor": "rgba(255, 255, 255, 0.05)",
                            "backdropFilter": "blur(10px)",
                            "border": "1px solid rgba(255, 255, 255, 0.1)",
                            "boxShadow": "0 4px 8px rgba(0, 0, 0, 0.5)",
                            "boxSizing": "border-box",
                        }
                    ),
                ),

                rx.cond(
                    PlayerCardState.enable_badges,
                    # Box mit Glassmorph-Optik
                    rx.box(
                        rx.vstack(
                            rx.heading("Abzeichen", size="6", margin_bottom="1rem", align="left"),
                            rx.hstack(
                                rx.foreach(
                                    StatsPageState.badge_indices,
                                    lambda i: rx.cond(
                                        StatsPageState.badge_tooltips_text[i] != "",
                                        rx.tooltip(
                                            rx.text(StatsPageState.badge_emojis_text[i], font_size="2rem", margin_right="0.5rem"),
                                            content=StatsPageState.badge_tooltips_text[i],
                                            side="top",
                                            align="center",
                                        ),
                                        rx.text(StatsPageState.badge_emojis_text[i], font_size="2rem", margin_right="0.5rem"),
                                    ),
                                ),
                                spacing="9",
                                justify="center",
                                width="100%",
                            ),
                        ),

                        # Stil der Box
                        style={
                            "maxWidth": "1400px",
                            "width": ["100%", "95%", "85%"],
                            "margin": "0 auto",
                            "padding": "2rem",
                            "borderRadius": "12px",
                            "backgroundColor": "rgba(255, 255, 255, 0.05)",
                            "backdropFilter": "blur(10px)",
                            "border": "1px solid rgba(255, 255, 255, 0.1)",
                            "boxShadow": "0 4px 8px rgba(0, 0, 0, 0.5)",
                            "boxSizing": "border-box",
                        }
                    ),
                ),

                # Box mit Glassmorph-Optik
                rx.box(
                    rx.vstack(
                        rx.heading("Abgeschlossene Challenges", size="6", margin_bottom="1rem", align="left"),
                        # Tabelle: Aufgabenübersicht
                        rc.table_container(
                            rc.table(
                                rc.thead(
                                    rc.tr(
                                        rx.cond(StatsPageState.show_finish_time, rc.th("Zeit")),
                                        rx.cond(StatsPageState.show_day, rc.th("Challenge")),
                                        rx.cond(StatsPageState.show_task, rc.th("Task")),
                                        rx.cond(StatsPageState.show_points, rc.th("Punkte")),
                                        rx.cond(StatsPageState.show_tries, rc.th("Versuche")),
                                        rx.cond(StatsPageState.show_hints, rc.th("Hinweise")),
                                        rx.cond(StatsPageState.show_resets, rc.th("Resets")),
                                        rx.cond(StatsPageState.show_first_blood, rc.th("First Blood")),
                                    )
                                ),
                                rc.tbody(
                                    rx.foreach(
                                        StatsPageState.challenges,
                                        lambda item: rc.tr(
                                            rx.cond(StatsPageState.show_finish_time, rc.td(item["finish_time"])),
                                            rx.cond(StatsPageState.show_day, rc.td(item["day"])),
                                            rx.cond(StatsPageState.show_task, rc.td(item["task"])),
                                            rx.cond(StatsPageState.show_points, rc.td(item["points"])),
                                            rx.cond(StatsPageState.show_tries, rc.td(item["tries"])),
                                            rx.cond(StatsPageState.show_hints, rc.td(item["hints"])),
                                            rx.cond(StatsPageState.show_resets, rc.td(item["resets"])),
                                            rx.cond(StatsPageState.show_first_blood, rc.td(item["first_blood"])),
                                        ),
                                    )
                                ),
                            ),
                            width="100%",
                            overflow_x="auto",
                        ),
                        width="100%",
                        display="flex",
                        justify_content="center",
                    ),

                    # Stil der Box
                    style={
                        "maxWidth": "1400px",
                        "width": ["100%", "95%", "85%"],
                        "margin": "0 auto",
                        "padding": "2rem",
                        "borderRadius": "12px",
                        "backgroundColor": "rgba(255, 255, 255, 0.05)",
                        "backdropFilter": "blur(10px)",
                        "border": "1px solid rgba(255, 255, 255, 0.1)",
                        "boxShadow": "0 4px 8px rgba(0, 0, 0, 0.5)",
                        "boxSizing": "border-box",
                    }


                ),
                rx.spacer(),
                width="100%",
                padding_x="16px",
            ),
            style={
                "minHeight": "100vh",
                "padding": "2rem",
                "color": "#f9fafb",
                "fontFamily": "'Inter', sans-serif",
                "boxSizing": "border-box",
                "width": "100%", # hinzugefügt
                "alignItems": "center", # optional: zentriert auch vertikal
            }
        )

    def configure(self) -> None:
        self.url = "/stats"
        self.name = "Spielerstatistik"
        self.main_color = "#04B486"
        self.is_standalone = True
        self.hide_sidebar = True
        self.on_load = [
            StatsPageState.load_all_stats,
        ]
        self.background_class = "black"
        self.auth_required = True
        self.unlock_day = unlock_always
