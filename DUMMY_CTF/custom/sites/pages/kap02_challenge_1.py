"""Reflex page for Kapitel 02 - Challenge 1 ("Das Zahlenschloss").

Renders the story intro, theory, the player's personal capture download, and the
two tasks; gating each section on the previous one being solved and revealing a
pointer to Challenge 2 on success.
"""

import reflex as rx
from website.engine.site import AbstractSiteBuilder
from website.engine.tasks.widget import TaskWidget
from website.engine.task_conf import PlayerCardState, AccordionState, render_task
from website.engine.challenge import *
from website.unlock_settings import *

from ..tasks.kap02_c1_tasks import task_02_04, task_02_05
from .kap02_shared import stories, theory
from .kap02_shared.variant import DhVariantState, index_banner, download_button


class Kapitel_02_Challenge_1(AbstractSiteBuilder):
    PAGE_ID = "challenge_02"

    def _content(self) -> rx.Component:
        """The unlocked challenge body: story, theory, capture, and tasks."""
        c = self.main_color
        return rx.vstack(
            # spy story intro
            stories.challenge_1(),
            # technical theory
            theory.challenge_1_technik(c),
            # personal capture
            index_banner(c),
            download_button("Challenge 1: Capture herunterladen", DhVariantState.cap_1),
            # tasks
            render_task(self.PAGE_ID, 4, "Aufgabe: Die Capture", TaskWidget(task_02_04)),
            rx.cond(
                PlayerCardState.tasks_solved["day_02_task_04"] | PlayerCardState.enable_test_mode,
                render_task(self.PAGE_ID, 5, "Aufgabe: Die Flagge", TaskWidget(task_02_05)),
            ),
            # success -> reveal the pointer to the next challenge once task 5 is solved
            rx.cond(
                PlayerCardState.tasks_solved["day_02_task_05"] | PlayerCardState.enable_test_mode,
                rx.box(
                    rx.markdown(
                        "**Geschafft!** Sie haben Challenge 1 gelöst. "
                        "**Challenge 2: Glatte Ordnung** ist jetzt in der "
                        "Seitenleiste freigeschaltet."
                    ),
                    style={"maxWidth": "1200px", "width": "100%", "margin": "16px auto",
                           "padding": "18px", "borderRadius": "12px",
                           "background": "rgba(4,180,134,0.10)",
                           "border": f"1px solid {c}", "boxSizing": "border-box"},
                ),
            ),
            spacing="4", width="100%", align_items="stretch",
        )

    def page(self) -> rx.Component:
        """Full page: heading plus the nested unlock gate that decides whether to
        show the content, a locked hint, a wait message, or a loading spinner."""
        return rx.vstack(
            rx.hstack(
                rx.heading("Challenge 1: Das Zahlenschloss", color=self.main_color, size="8",
                           style={"background": "linear-gradient(90deg, #04B486, #00FFFF)",
                                  "WebkitBackgroundClip": "text",
                                  "WebkitTextFillColor": "transparent"}),
                rx.text("🔓", size="8", align_self="center"),
                align_items="center", width="100%", spacing="2",
                style={"marginBottom": "24px"},
            ),
            # Gate 1: page state loaded? else show a spinner.
            rx.cond(
                CondState.is_ready & PlayerCardState.update_day_ready[2],
                # Gate 2: has the game master started the event?
                rx.cond(
                    CondState.event_enabled,
                    # Gate 3: previous chapter completed? else show the locked hint.
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
            # Initialise the accordion state for this page (34 sections).
            on_mount=lambda: AccordionState.init(self.PAGE_ID, 34),
        )

    def configure(self) -> None:
        """Page metadata: route, sidebar name/icon/colour, load hooks, and auth."""
        self.url = "/challenge_02_c1"
        self.name = "Challenge 1: Das Zahlenschloss"
        self.icon = "flame"
        self.main_color = "#04B486"
        self.group = "kapitel_02"
        self.position_priority = 90    # just below the Kurs page
        self.on_load = [
            CondState.reset_check_status,
            CondState.do_checks,
            PlayerCardState.update_day(2),
        ]
        self.background_class = "black"
        self.auth_required = True
        self.unlock_day = unlock_always
