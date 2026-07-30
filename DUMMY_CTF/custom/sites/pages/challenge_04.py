from urllib.parse import quote

import reflex as rx
from website.engine.site import AbstractSiteBuilder
from website.engine.tasks.widget import TaskWidget
from website.engine.task_conf import PlayerCardState, AccordionState, render_task
from website.engine.challenge import *
from ..tasks.challenge_04_tasks import *
from website.unlock_settings import *
from website.auth_lib import AuthCookie, BackendRequests


class ChallengeBackendRequests(BackendRequests):
    url = "http://challenge:8000"


class MyDhVariantState(AuthCookie):
    index: int = 0
    p: str = ""
    g: str = ""
    Ys: str = ""
    loaded: bool = False
    capture_status: str = ""  # "", "sending", "sent", "error"

    async def load(self):
        safe_username = quote(self.get_username, safe="")
        response = await ChallengeBackendRequests.get(f"/dh_export/variant/{safe_username}")
        if response.status_code == 200:
            data = response.json()
            self.index = data["index"]
            self.p = data["p"]
            self.g = data["g"]
            self.Ys = data["Ys"]
            self.loaded = True

    async def trigger_capture(self):
        """Sendet die Variante an die Trainings-VM"""
        async with self:
            self.capture_status = "sending"

        response = await ChallengeBackendRequests.post(f"/dh_export/{self.index}/start_capture")

        async with self:
            self.capture_status = "sent" if response.status_code == 200 else "error"


class Kapitel_04(AbstractSiteBuilder):
    PAGE_ID = "challenge_04"

    def _capture_panel(self) -> rx.Component:
        """Per-player DH values + Wireshark capture trigger (shown after 4.2)"""
        return rx.cond(
            MyDhVariantState.loaded,
            rx.box(
                rx.text.strong("Deine persönlichen DH-Parameter (aus deinem Capture):"),
                rx.vstack(
                    rx.hstack(rx.text.strong("p ="), rx.code(MyDhVariantState.p, size="2",
                              style={"wordBreak": "break-all"}), align_items="start"),
                    rx.hstack(rx.text.strong("g ="), rx.code(MyDhVariantState.g, size="2")),
                    rx.hstack(rx.text.strong("Ys ="), rx.code(MyDhVariantState.Ys, size="2",
                              style={"wordBreak": "break-all"}), align_items="start"),
                    spacing="1", margin_top="0.5em", align_items="start", width="100%",
                ),
                rx.text(
                    "So schneidest du deinen persönlichen Handshake selbst mit - alles "
                    "läuft lokal auf der Trainings-VM:",
                    margin_top="0.75em",
                ),
                rx.vstack(
                    rx.text(
                        "1. Öffne Wireshark auf der VM und starte einen Mitschnitt auf der "
                        "Netzwerk-Schnittstelle der VM (z.B. eth1)."
                    ),
                    rx.hstack(
                        rx.text("2. Setze den Anzeigefilter:"),
                        rx.code("tcp.port == 4434", size="2"),
                    ),
                    rx.text(
                        "3. Klicke erst DANN unten auf \"Gestartet\" - jetzt wird dein "
                        "persönlicher DHE_EXPORT-Handshake mit genau den oben gezeigten "
                        "Parametern über die Leitung geschickt und landet in deinem Mitschnitt."
                    ),
                    rx.text(
                        "4. Die für die Aufgaben nötigen Werte (p, g, Ys, Yc, "
                        "client_random, server_random) liest du direkt aus diesem Mitschnitt "
                        "ab - siehe die Anleitung in den einzelnen Aufgaben.",
                    ),
                    spacing="1", margin_top="0.5em", align_items="start", width="100%",
                ),
                rx.flex(
                    rx.button(
                        rx.cond(
                            MyDhVariantState.capture_status == "sending",
                            rx.spinner(size="2"),
                            rx.icon(tag="play"),
                        ),
                        rx.cond(
                            MyDhVariantState.capture_status == "sent",
                            "Erneut senden",
                            "Gestartet",
                        ),
                        on_click=MyDhVariantState.trigger_capture,
                        disabled=MyDhVariantState.capture_status == "sending",
                    ),
                    margin_top="0.5em",
                ),
                rx.cond(
                    MyDhVariantState.capture_status == "sent",
                    rx.callout(
                        "Handshake gesendet - in deinem laufenden Wireshark-Mitschnitt "
                        "(Filter tcp.port == 4434) siehst du jetzt die DHE_EXPORT-Konversation.",
                        icon="check", color_scheme="green", margin_top="0.5em",
                    ),
                ),
                rx.cond(
                    MyDhVariantState.capture_status == "error",
                    rx.callout(
                        "Handshake konnte nicht gesendet werden - ist die Trainings-VM erreichbar?",
                        icon="triangle-alert", color_scheme="red", margin_top="0.5em",
                    ),
                ),
                style={
                    "maxWidth": "900px", "width": "100%", "margin": "16px 0",
                    "padding": "20px", "borderRadius": "12px",
                    "background": "rgba(160, 210, 255, 0.12)",
                    "border": "1px solid rgba(255, 255, 255, 0.18)",
                },
            ),
            rx.spinner(),
        )

    def page(self) -> rx.Component:
        return rx.vstack(
            rx.heading(
                "Schwaches Diffie-Hellman (Logjam)",
                color=self.main_color, size="8",
                style={
                    "background": "linear-gradient(90deg, #04B486, #00FFFF)",
                    "WebkitBackgroundClip": "text",
                    "WebkitTextFillColor": "transparent",
                    "marginBottom": "24px",
                },
            ),
            rx.cond(
                CondState.is_ready & PlayerCardState.update_day_ready[4],
                rx.cond(
                    CondState.event_enabled,
                    rx.vstack(
                        render_task(self.PAGE_ID, 0, "Aufgabe 1: Einführung", TaskWidget(task_04_00)),

                        rx.cond(
                            PlayerCardState.tasks_solved["day_04_task_00"] | PlayerCardState.enable_test_mode,
                            rx.vstack(
                                render_task(self.PAGE_ID, 1, "Aufgabe 2: Traffic Capture", TaskWidget(task_04_01)),

                                rx.cond(
                                    PlayerCardState.tasks_solved["day_04_task_01"] | PlayerCardState.enable_test_mode,
                                    rx.vstack(
                                        render_task(self.PAGE_ID, 2, "Aufgabe 3: Machbarkeit", TaskWidget(task_04_02)),

                                        rx.cond(
                                            PlayerCardState.tasks_solved["day_04_task_02"] | PlayerCardState.enable_test_mode,
                                            rx.vstack(
                                                self._capture_panel(),

                                                render_task(self.PAGE_ID, 3, "Aufgabe 4: p-1 faktorisieren", TaskWidget(task_04_03)),

                                                rx.cond(
                                                    PlayerCardState.tasks_solved["day_04_task_03"] | PlayerCardState.enable_test_mode,
                                                    rx.vstack(
                                                        render_task(self.PAGE_ID, 4, "Aufgabe 5: Diskreter Logarithmus", TaskWidget(task_04_04)),

                                                        rx.cond(
                                                            PlayerCardState.tasks_solved["day_04_task_04"] | PlayerCardState.enable_test_mode,
                                                            rx.vstack(
                                                                render_task(self.PAGE_ID, 5, "Aufgabe 6: TLS Master Secret", TaskWidget(task_04_05)),

                                                                rx.cond(
                                                                    PlayerCardState.tasks_solved["day_04_task_05"] | PlayerCardState.enable_test_mode,
                                                                    render_task(self.PAGE_ID, 6, "Aufgabe 7: Die Flagge", TaskWidget(task_04_06)),
                                                                ),
                                                            ),
                                                        ),
                                                    ),
                                                ),
                                            ),
                                        ),
                                    ),
                                ),
                            ),
                        ),
                        width="100%",
                    ),
                    rx.vstack(
                        rx.text(
                            "Sie wollen schon loslegen? Fair Play! Bitte warten Sie, bis der "
                            "Spielleiter das Event für alle Teilnehmer startet!"
                        ),
                    ),
                ),
            ),
            on_mount=lambda: AccordionState.init(self.PAGE_ID, 7),
            width="100%",
        )

    def configure(self) -> None:
        self.url = "/challenge_04"
        self.name = "Schwaches Diffie-Hellman"
        self.group = "2_FREAK"
        self.position_priority = 10
        self.icon = "key-round"
        self.main_color = "#04B486"
        self.is_standalone = False
        self.hide_sidebar = False
        self.on_load = [
            CondState.reset_check_status,
            CondState.do_checks,
            CondState.do_check_cyberrange,
            PlayerCardState.update_day(4),
            MyDhVariantState.load,
        ]
        self.background_class = "black"
        self.auth_required = True
        self.unlock_day = unlock_always
