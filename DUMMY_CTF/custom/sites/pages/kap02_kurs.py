"""
Kapitel 02 — Sub-page: Kurs (Grundlagen).

Always accessible. Teaches the DH basics (groups, DLP, handshake) with a spy
story intro and split Wahr/Falsch comprehension questions. This is the entry
point of the chapter; solving its questions is not required to start Challenge 1,
but it is the recommended starting point.

Sidebar grouping: all Kapitel-02 sub-pages share group="kapitel_02" and are
ordered by position_priority (higher = higher in the list).
"""

import reflex as rx
from website.engine.site import AbstractSiteBuilder
from website.engine.tasks.widget import TaskWidget
from website.engine.task_conf import PlayerCardState, AccordionState, render_task
from website.engine.challenge import *
from website.unlock_settings import *

from ..tasks.kap02_c1_tasks import (
    task_02_00, task_02_01, task_02_02, task_02_03,
)
from .kap02_shared import stories, theory


class Kapitel_02_Kurs(AbstractSiteBuilder):
    PAGE_ID = "challenge_02"   # shared task-day namespace (day_02_task_XX)

    def _content(self) -> rx.Component:
        c = self.main_color
        return rx.vstack(
            # narrative intro to the whole chapter
            stories.dh_intro(),
            # theory: groups
            theory.groups(c),
            # concept checks (split Wahr/Falsch)
            render_task(self.PAGE_ID, 0, "Verständnisfrage 1", TaskWidget(task_02_00)),
            render_task(self.PAGE_ID, 1, "Verständnisfrage 2", TaskWidget(task_02_01)),
            # theory: DLP
            theory.dlp(c),
            render_task(self.PAGE_ID, 2, "Verständnisfrage 3", TaskWidget(task_02_02)),
            render_task(self.PAGE_ID, 3, "Verständnisfrage 4", TaskWidget(task_02_03)),
            # theory: handshake (with SVG)
            theory.handshake(c),
            # pointer to the first challenge
            rx.box(
                rx.markdown(
                    "**Bereit?** Wechseln Sie in der Seitenleiste zu "
                    "**Challenge 1** und bergen Sie Ihre erste Flagge."
                ),
                style={"maxWidth": "1200px", "width": "100%", "margin": "16px auto",
                       "padding": "18px", "borderRadius": "12px",
                       "background": "rgba(4,180,134,0.08)",
                       "border": f"1px solid {c}", "boxSizing": "border-box"},
            ),
            spacing="4", width="100%", align_items="stretch",
        )

    def page(self) -> rx.Component:
        return rx.vstack(
            rx.hstack(
                rx.heading("Kurs: Grundlagen", color=self.main_color, size="8",
                           style={"background": "linear-gradient(90deg, #04B486, #00FFFF)",
                                  "WebkitBackgroundClip": "text",
                                  "WebkitTextFillColor": "transparent"}),
                rx.text("📘", size="8", align_self="center"),
                align_items="center", width="100%", spacing="2",
                style={"marginBottom": "24px"},
            ),
            rx.cond(
                CondState.is_ready & PlayerCardState.update_day_ready[2],
                rx.cond(
                    CondState.event_enabled,
                    rx.cond(
                        PlayerCardState.tasks_solved["day_01_task_09"] | PlayerCardState.enable_test_mode,
                        self._content(),
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
        self.url = "/challenge_02_kurs"
        self.name = "Kurs: Grundlagen"
        self.icon = "book-open"
        self.main_color = "#04B486"
        self.group = "kapitel_02"
        self.position_priority = 100   # highest = top of the group
        self.on_load = [
            CondState.reset_check_status,
            CondState.do_checks,
            PlayerCardState.update_day(2),
        ]
        self.background_class = "black"
        self.auth_required = True
        self.unlock_day = unlock_always
