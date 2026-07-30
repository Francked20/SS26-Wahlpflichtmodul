"""Kapitel 02 - Sub-page: Challenge 4 (Der schwache Erzeuger)"""

import reflex as rx
from website.engine.site import AbstractSiteBuilder
from website.engine.tasks.widget import TaskWidget
from website.engine.task_conf import PlayerCardState, AccordionState, render_task
from website.engine.challenge import *
from website.unlock_settings import *

from ..tasks.kap02_c45_tasks import task_02_13, task_02_14, task_02_15
from .kap02_shared import stories, theory
from .kap02_shared.variant import DhVariantState, index_banner, download_button
from .kap02_shared.muster import muster_panel
from .kap02_shared.kap02_muster_codes import MUSTER_C4


class Kapitel_02_Challenge_4(AbstractSiteBuilder):
    PAGE_ID = "challenge_02"

    def _content(self) -> rx.Component:
        c = self.main_color
        return rx.vstack(
            stories.challenge_4(),
            theory.challenge_4_technik(c),
            index_banner(c),
            download_button("Challenge 4: Capture herunterladen", DhVariantState.cap_4),
            # Muster-Löser + SageCell
            muster_panel(c, MUSTER_C4),
            render_task(self.PAGE_ID, 13, "Verständnisfrage", TaskWidget(task_02_13)),
            render_task(self.PAGE_ID, 14, "Aufgabe: Die Ordnung von g", TaskWidget(task_02_14)),
            rx.cond(
                PlayerCardState.tasks_solved["day_02_task_14"] | PlayerCardState.enable_test_mode,
                render_task(self.PAGE_ID, 15, "Aufgabe: Die Flagge", TaskWidget(task_02_15)),
            ),
            rx.cond(
                PlayerCardState.tasks_solved["day_02_task_15"] | PlayerCardState.enable_test_mode,
                rx.box(
                    rx.markdown(
                        "**Stark!** Challenge 4 gelöst. "
                        "**Challenge 5: Logjam** ist jetzt freigeschaltet."
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
                rx.text("Lösen Sie zuerst Challenge 3, um diese Challenge "
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
                rx.heading("Challenge 4: Der schwache Erzeuger", color=self.main_color, size="8",
                           style={"background": "linear-gradient(90deg, #04B486, #00FFFF)",
                                  "WebkitBackgroundClip": "text",
                                  "WebkitTextFillColor": "transparent"}),
                rx.text("🗝️", size="8", align_self="center"),
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
                            PlayerCardState.tasks_solved["day_02_task_12"] | PlayerCardState.enable_test_mode,
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
        self.url = "/challenge_02_c4"
        self.name = "Challenge 4: Der schwache Erzeuger"
        self.icon = "key"
        self.main_color = "#04B486"
        self.group = "1_ROAD TO DIFFIE-HELLMAN"
        self.position_priority = 60
        self.on_load = [
            CondState.reset_check_status,
            CondState.do_checks,
            PlayerCardState.update_day(2),
        ]
        self.background_class = "black"
        self.auth_required = True
        self.unlock_day = unlock_always
