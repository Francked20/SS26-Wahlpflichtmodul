from urllib.parse import quote

import reflex as rx
from website.engine.site import AbstractSiteBuilder
from website.engine.tasks.widget import TaskWidget
from website.engine.task_conf import PlayerCardState, AccordionState, render_task
from website.engine.challenge import *
from ..tasks.challenge_03_tasks import *
from website.unlock_settings import *
from website.auth_lib import AuthCookie, BackendRequests


class ChallengeBackendRequests(BackendRequests):
    url = "http://challenge:8000"


class MyVariantState(AuthCookie):
    index: int = 0
    n256: str = ""
    loaded: bool = False
    reveal_factor: str = ""
    capture_status: str = ""  # "", "sending", "sent", "error"

    async def load(self):
        safe_username = quote(self.get_username, safe="")
        response = await ChallengeBackendRequests.get(f"/export_cipher/variant/{safe_username}")
        if response.status_code == 200:
            data = response.json()
            self.index = data["index"]
            self.n256 = data["n256"]
            self.loaded = True

        reveal_response = await BackendRequests.get(
            "/challenges/export_cipher_reveal_factor",
            params={"day": 3, "task": 2},
            auth=self.auth_cookie,
        )
        if reveal_response.status_code == 200:
            factor = reveal_response.json().get("reveal_factor")
            if factor:
                self.reveal_factor = str(factor)

    @rx.event(background=True)
    async def trigger_capture(self):
        """Sendet die Variante an die Trainings-VM"""
        async with self:
            self.capture_status = "sending"

        response = await ChallengeBackendRequests.post(f"/export_cipher/{self.index}/start_capture")

        async with self:
            self.capture_status = "sent" if response.status_code == 200 else "error"


class Kapitel_03(AbstractSiteBuilder):
    PAGE_ID = "challenge_03"

    def page(self) -> rx.Component:
        return rx.vstack(
            rx.heading(
                "Export Ciphers & FREAK",
                color=self.main_color,
                size="8",
                style={
                    "background": "linear-gradient(90deg, #04B486, #00FFFF)",
                    "WebkitBackgroundClip": "text",
                    "WebkitTextFillColor": "transparent",
                    "marginBottom": "24px",
                },
            ),
            rx.cond(
                CondState.is_ready & PlayerCardState.update_day_ready[3],
                rx.cond(
                    CondState.event_enabled,
                    rx.vstack(
                        render_task(self.PAGE_ID, 0, "Aufgabe 1: Einführung", TaskWidget(task_03_00)),

                        rx.cond(
                            PlayerCardState.tasks_solved["day_03_task_00"] | PlayerCardState.enable_test_mode,
                            rx.vstack(
                                rx.cond(
                                    MyVariantState.loaded,
                                    rx.box(
                                        rx.text.strong("Deine persönliche 256-Bit-Zahl N:"),
                                        rx.code(MyVariantState.n256, size="2", style={"wordBreak": "break-all"}),
                                        rx.text(
                                            "Starte jetzt deinen eigenen Paket-Mitschnitt (Wireshark) auf der "
                                            "Trainings-VM. Klicke danach auf \"Gestartet\" - erst dann wird dein "
                                            "persönlicher TLS-Handshake mit diesem N über die Leitung geschickt, "
                                            "damit du eine ganz normale TLS-Konversation selbst mitschneidest.",
                                            margin_top="0.5em",
                                        ),
                                        rx.flex(
                                            rx.button(
                                                rx.cond(
                                                    MyVariantState.capture_status == "sending",
                                                    rx.spinner(size="2"),
                                                    rx.icon(tag="play"),
                                                ),
                                                rx.cond(
                                                    MyVariantState.capture_status == "sent",
                                                    "Erneut senden",
                                                    "Gestartet",
                                                ),
                                                on_click=MyVariantState.trigger_capture,
                                                disabled=MyVariantState.capture_status == "sending",
                                            ),
                                            margin_top="0.5em",
                                        ),
                                        rx.cond(
                                            MyVariantState.capture_status == "sent",
                                            rx.callout(
                                                "Handshake gesendet - schau in deinem Mitschnitt nach der Konversation!",
                                                icon="check",
                                                color_scheme="green",
                                                margin_top="0.5em",
                                            ),
                                        ),
                                        rx.cond(
                                            MyVariantState.capture_status == "error",
                                            rx.callout(
                                                "Handshake konnte nicht gesendet werden - ist die Trainings-VM erreichbar?",
                                                icon="triangle-alert",
                                                color_scheme="red",
                                                margin_top="0.5em",
                                            ),
                                        ),
                                        style={
                                            "maxWidth": "1200px",
                                            "width": "100%",
                                            "margin": "16px auto",
                                            "padding": "18px",
                                            "borderRadius": "12px",
                                            "color": "#F2F2F2",
                                            "background": "rgba(255, 255, 255, 0.04)",
                                            "border": f"1px solid {self.main_color}55",
                                            "borderLeft": f"4px solid {self.main_color}",
                                        },
                                    ),
                                    rx.spinner(),
                                ),

                                render_task(self.PAGE_ID, 1, "Aufgabe 2: Traffic Capture", TaskWidget(task_03_01)),

                                rx.cond(
                                    PlayerCardState.tasks_solved["day_03_task_01"] | PlayerCardState.enable_test_mode,
                                    rx.vstack(
                                        render_task(self.PAGE_ID, 2, "Aufgabe 3: 256-Bit faktorisieren", TaskWidget(task_03_02)),

                                        rx.cond(
                                            PlayerCardState.tasks_solved["day_03_task_02"] | PlayerCardState.enable_test_mode,
                                            rx.vstack(
                                                rx.cond(
                                                    MyVariantState.reveal_factor != "",
                                                    rx.callout(
                                                        f"Dein freigeschalteter Faktor des 512-Bit-N (aus Aufgabe 3): {MyVariantState.reveal_factor}",
                                                        icon="key",
                                                        color_scheme="amber",
                                                        width="100%",
                                                    ),
                                                ),
                                                render_task(self.PAGE_ID, 3, "Aufgabe 4: Zweiter Faktor", TaskWidget(task_03_03)),

                                                rx.cond(
                                                    PlayerCardState.tasks_solved["day_03_task_03"] | PlayerCardState.enable_test_mode,
                                                    rx.vstack(
                                                        render_task(self.PAGE_ID, 4, "Aufgabe 5: Pre-Master-Secret entschlüsseln", TaskWidget(task_03_04)),

                                                        rx.cond(
                                                            PlayerCardState.tasks_solved["day_03_task_04"] | PlayerCardState.enable_test_mode,
                                                            rx.vstack(
                                                                render_task(self.PAGE_ID, 5, "Aufgabe 6: TLS Master Secret", TaskWidget(task_03_05)),

                                                                rx.cond(
                                                                    PlayerCardState.tasks_solved["day_03_task_05"] | PlayerCardState.enable_test_mode,
                                                                    render_task(self.PAGE_ID, 6, "Aufgabe 7: Die Flagge", TaskWidget(task_03_06)),
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
                            "Sie wollen schon loslegen? Fair Play! Bitte warten Sie, bis der Spielleiter das Event für alle Teilnehmer startet!"
                        ),
                    ),
                ),
                rx.vstack(rx.spinner()),
            ),
            on_mount=lambda: AccordionState.init(self.PAGE_ID, 7),
            width="100%",
        )

    def configure(self) -> None:
        self.url = "/challenge_03"
        self.name = "Export Ciphers"
        self.group = "2_FREAK"
        self.position_priority = 20
        self.icon = "shield-alert"
        self.main_color = "#04B486"
        self.is_standalone = False
        self.hide_sidebar = False
        self.on_load = [
            CondState.reset_check_status,
            CondState.do_checks,
            CondState.do_check_cyberrange,
            PlayerCardState.update_day(3),
            MyVariantState.load,
        ]
        self.background_class = "black"
        self.auth_required = True
        self.unlock_day = unlock_always
