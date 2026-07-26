"""
Kapitel 02 — Sub-page: Challenge 9 (ElGamal, wiederverwendeter Nonce).

Akt III, Teil 1. Chained unlock: content gated on Challenge 8's flag
(day_02_task_27).
"""

import reflex as rx
from website.engine.site import AbstractSiteBuilder
from website.engine.tasks.widget import TaskWidget
from website.engine.task_conf import PlayerCardState, AccordionState, render_task
from website.engine.challenge import *
from website.unlock_settings import *

from ..tasks.kap02_c910_tasks import task_02_28, task_02_29, task_02_30
from .kap02_shared import stories, theory
from .kap02_shared.variant import DhVariantState, index_banner, download_button


class Kapitel_02_Challenge_9(AbstractSiteBuilder):
    PAGE_ID = "challenge_02"

    def _content(self) -> rx.Component:
        c = self.main_color
        return rx.vstack(
            stories.challenge_9(),
            theory.challenge_9_technik(c),
            index_banner(c),
            download_button("Challenge 9 — Capture herunterladen", DhVariantState.cap_9),
            render_task(self.PAGE_ID, 28, "Verständnisfrage", TaskWidget(task_02_28)),
            render_task(self.PAGE_ID, 29, "Aufgabe: Das verräterische Zeichen", TaskWidget(task_02_29)),
            rx.cond(
                PlayerCardState.tasks_solved["day_02_task_29"] | PlayerCardState.enable_test_mode,
                render_task(self.PAGE_ID, 30, "Aufgabe: Die Flagge", TaskWidget(task_02_30)),
            ),
            rx.cond(
                PlayerCardState.tasks_solved["day_02_task_30"] | PlayerCardState.enable_test_mode,
                rx.box(
                    rx.markdown(
                        "**Stark!** Sie haben gesehen, wie ein einziger "
                        "wiederverwendeter Zufallswert ein sicheres "
                        "Verschlüsselungsverfahren aushebelt. Im **Finale** "
                        "(Challenge 10) treffen Sie denselben Fehler in der Welt "
                        "der digitalen Signaturen — mit noch dramatischeren Folgen: "
                        "der komplette private Schlüssel fällt."
                    ),
                    style={"maxWidth": "1200px", "width": "100%", "margin": "16px auto",
                           "padding": "18px", "borderRadius": "12px",
                           "background": "rgba(4,180,134,0.10)",
                           "border": f"1px solid {c}", "boxSizing": "border-box"},
                ),
            ),
            spacing="4", width="100%", align_items="stretch",
        )

    def _locked(self) -> rx.Component:
        return rx.box(
            rx.vstack(
                rx.icon("lock", size=40, color="#EF9F27"),
                rx.text("Diese Challenge ist noch gesperrt.",
                        font_size="1.3em", font_weight="500"),
                rx.text("Lösen Sie zuerst Challenge 8, um diese Challenge "
                        "freizuschalten.", color="gray"),
                spacing="3", align_items="center",
            ),
            style={"maxWidth": "800px", "width": "100%", "margin": "60px auto",
                   "padding": "40px", "borderRadius": "16px",
                   "background": "rgba(239,159,39,0.06)",
                   "border": "1px solid rgba(239,159,39,0.3)",
                   "textAlign": "center", "boxSizing": "border-box"},
        )

    def page(self) -> rx.Component:
        return rx.vstack(
            rx.hstack(
                rx.heading("Challenge 9 — Zweimal derselbe Würfel", color=self.main_color, size="8",
                           style={"background": "linear-gradient(90deg, #04B486, #00FFFF)",
                                  "WebkitBackgroundClip": "text",
                                  "WebkitTextFillColor": "transparent"}),
                rx.text("🎲", size="8", align_self="center"),
                align_items="center", width="100%", spacing="2",
                style={"marginBottom": "24px"},
            ),
            rx.cond(
                CondState.is_ready & PlayerCardState.update_day_ready[2],
                rx.cond(
                    CondState.event_enabled,
                    rx.cond(
                        PlayerCardState.tasks_solved["day_01_task_09"] | PlayerCardState.enable_test_mode,
                        rx.cond(
                            PlayerCardState.tasks_solved["day_02_task_27"] | PlayerCardState.enable_test_mode,
                            self._content(),
                            self._locked(),
                        ),
                        rx.vstack(rx.text(
                            "Es müssen zuerst alle Aufgaben des vorherigen Kapitels "
                            "gelöst werden, um dieses Kapitel freizuschalten!")),
                    ),
                    rx.vstack(rx.text(
                        "Bitte warten Sie, bis der Spielleiter das Event startet!")),
                ),
                rx.vstack(rx.spinner()),
            ),
            on_mount=lambda: AccordionState.init(self.PAGE_ID, 34),
        )

    def configure(self) -> None:
        self.url = "/challenge_02_c9"
        self.name = "Challenge 9 — Zweimal derselbe Würfel"
        self.icon = "dice-5"
        self.main_color = "#04B486"
        self.group = "kapitel_02"
        self.position_priority = 10
        self.on_load = [
            CondState.reset_check_status,
            CondState.do_checks,
            PlayerCardState.update_day(2),
        ]
        self.background_class = "black"
        self.auth_required = True
        self.unlock_day = unlock_always
