import asyncio
import json
import logging
import sys
import typing
from urllib.parse import quote

import reflex as rx
from reflex import Component

from website.engine.task_conf import PlayerCardState
from website.auth_lib import AuthCookie, BackendRequests, PageAuthState

from .buttons import HintButton, SolutionButtonBase, DownloadButtonBase, CustomLinkButtonBase, VSCodeButtonBase, \
    KaliButtonBase, ResetButtonBase, VSCodeInjectButton, VSCodeLinkButton, KaliLinkButton, CyberRangeLinkButton, \
    CyberRangeUserCopyButton, CyberRangePasswordCopyButton, RefreshButtonBase
from .meta import MetaTask
from .models import TaskData, TaskWidgetConfiguration, TaskWidgetState

from website.engine.challenge import CondState


class TaskWidgetClass(rx.ComponentState):
    has_loaded: bool = False
    username: typing.Optional[str] = None

    widget_state: TaskWidgetState = TaskWidgetState()

    answer_state: str = ""
    is_solving: bool = False
    attempted_solve: bool = False

    def set_answer_state(self, value: str) -> None:
        self.answer_state = value

    @classmethod
    def create(cls, data: TaskData) -> Component:
        config = MetaTask.register(data)
        return super().create(config=config)

    @rx.event
    async def load_state_event(self, day_id, task_id):
        await self.load_state(day_id, task_id)

    @rx.event(background=True)
    async def load_state_event_bg(self, day_id, task_id):
        await self.load_state(day_id, task_id)

    @rx.event(background=True)
    async def request_hint_event(self, day_id, task_id):
        async with self:
            token = await self.get_var_value(AuthCookie.auth_cookie)
        response = await BackendRequests.post(
            "/challenges/hint",
            params={
                "day" : day_id,
                "task": task_id,
            },
            auth=token,
        )

        if response.status_code == 401:
            return PageAuthState.to_error_page()

        if response.json().get("hint_unlocked", False):
            await self.load_state(day_id, task_id)
        return None

    @rx.event(background=True)
    async def submit_task_event(self, day_id, task_id):
        async with self:
            self.is_solving = True
            self.attempted_solve = True

        try:
            events = await self.submit_task(day_id, task_id)
            await asyncio.sleep(0.5)  # optional
            await self.load_state(day_id, task_id)
            return events
        finally:
            async with self:
                self.is_solving = False


    @rx.event(background=True)
    async def reset_task_event(self, day_id, task_id):
        logging.info(f"Resetting day {day_id} task {task_id} for {self.username}")

        async with self:
            token = await self.get_var_value(AuthCookie.auth_cookie)
        response = await BackendRequests.post(
            "/challenges/reset",
            params={
                "day" : day_id,
                "task": task_id,
            },
            auth=token,
        )
        if response.status_code == 401:
            return PageAuthState.to_error_page()

        async with self:
            self.answer_state = ""
            self.attempted_solve = False
            self.is_solving = False

        await self.load_state(day_id, task_id)
        return [
            PlayerCardState.reset_day_ready(day_id),
            PlayerCardState.update_day(day_id),
        ]

    async def load_state(self, day_id, task_id):
        if self.username is None:
            async with self:
                username = await self.get_var_value(AuthCookie.get_username)

            if not username:
                logging.warning("Username not loaded yet!")
                return rx.toast.error(
                    f"Cannot load username.\nTry reloading the page or authenticating again.",
                    position="top-center",
                )

            async with self:
                self.username = username

        safe_username = quote(self.username, safe="")

        async with self:
            token = await self.get_var_value(AuthCookie.auth_cookie)
        response = await BackendRequests.get(
            f"/user/{safe_username}/challenges_dataset/{day_id}/{task_id}", auth=token
        )

        if response.status_code == 401:
            return PageAuthState.to_error_page()

        data = response.json()

        async with self:
            self.widget_state = TaskWidgetState(**data)
            self.has_loaded = True

        print(f"LOADED STATE {day_id=} {task_id=}", file=sys.stderr)
        return None

    async def submit_task(self, day_id, task_id):
        async with self:
            token = await self.get_var_value(AuthCookie.auth_cookie)
        response = await BackendRequests.post(
            "/challenges/solve",
            params={
                "day"     : day_id,
                "task"    : task_id,
                "solution": str(self.answer_state),
            },
            auth=token,
        )

        if response.status_code == 401:
            return PageAuthState.to_error_page()

#        return None
        return [
            PlayerCardState.reset_day_ready(day_id),
            PlayerCardState.update_day(day_id),
        ]

    def set_checkbox(self, value: bool, position: int):
        if not self.answer_state:
            self.answer_state = "0" * len(self.widget_state.options)

        value = str(int(bool(value)))
        assert len(value) == 1

        answers = self.answer_state
        self.answer_state = answers[:position] + value + answers[position + 1:]

    @staticmethod
    def component_debug_panel(cls: type["TaskWidgetClass"], config: "TaskWidgetConfiguration"):
        return rx.cond(
            PlayerCardState.enable_test_mode,
            rx.vstack(
                rx.callout(
                    "DEBUG PANEL: REMOVE IN PROD",
                    color_scheme="yellow",
                    high_contrast=True,
                    icon="info",
                    size="2",
                    width="100%",
                ),
                rx.scroll_area(
                    rx.code_block(f'{{"cls.answer_state": "{cls.answer_state}"}}\n' f"{
                    json.dumps(
                        {
                            n: f"{getattr(cls.widget_state, n)}"[:-1]
                            for n in TaskWidgetState.model_fields.keys()
                        },
                        indent=2,
                        default=str
                    )
                    }\n" f"{config.model_dump_json(indent=2, fallback=str)}"),
                    type="always",
                    scrollbars="both",
                    width="calc(70vw - 2em)",
                    height="30vh",
                ),
                width="100%",
            ),
            # rx.container()
        )

    @staticmethod
    def component_answer_field(
            cls: type["TaskWidgetClass"], config: "TaskWidgetConfiguration",
            answer_event: rx.EventChain
    ) -> rx.Component:
        if config.task_type == "input":
            return rx.form(
                rx.input(
                    type="text",
                    placeholder=cls.widget_state.placeholder_text,
                    value=cls.answer_state,
                    on_change=cls.set_answer_state,
                    disabled=cls.widget_state.solved | ~cls.widget_state.is_answerable,
                    width="100%",
                ),
                on_submit=answer_event,
            )

        elif config.task_type == "select":
            return rx.radio(
                cls.widget_state.options,
                on_change=cls.set_answer_state,
                disabled=cls.widget_state.solved | ~cls.widget_state.is_answerable,
                size="3",
                direction="column",
            )

        elif config.task_type == "multiple":
            return rx.vstack(
                rx.foreach(
                    cls.widget_state.options,
                    lambda s, i: rx.checkbox(
                        s,
                        on_change=lambda val, idx=i: cls.set_checkbox(val, idx),
                        disabled=cls.widget_state.solved | ~cls.widget_state.is_answerable,
                        size="3",
                    ),
                )
            )

        raise ValueError("Invalid task type")

    @staticmethod
    def component_answer_panel(
            cls: type["TaskWidgetClass"],
            config: "TaskWidgetConfiguration",
    ) -> tuple[rx.Component, rx.EventChain]:

        # --- Gruppe: Überprüfen / Hinweis / Reset ---
        submit_button = SolutionButtonBase.create(
            widget_state=cls.widget_state,
            is_solving=cls.is_solving,
            manual_disable=(cls.answer_state == ""),
            on_action=[cls.submit_task_event, config.day_id, config.task_id],
        )
        on_click = submit_button.event_triggers["on_click"]

        group_check: list[rx.Component] = [submit_button]

        if config.allow_hints:
            group_check.append(
                HintButton.create(
                    widget_state=cls.widget_state,
                    on_action=[cls.request_hint_event, config.day_id, config.task_id],
                )
            )

        if config.allow_reset:
            group_check.append(
                ResetButtonBase.create(
                    widget_state=cls.widget_state,
                    on_action=[cls.reset_task_event, config.day_id, config.task_id],
                )
            )
        else:
            # nur global erlaubt → reaktiv
            group_check.append(
                rx.cond(
                    PlayerCardState.allow_task_reset,
                    ResetButtonBase.create(
                        widget_state=cls.widget_state,
                        on_action=[cls.reset_task_event, config.day_id, config.task_id],
                    ),
                )
            )      

        # --- Gruppe: Refresh ---
        refresh_button = RefreshButtonBase.create(
            widget_state=cls.widget_state,
            on_action=[cls.load_state_event_bg, config.day_id, config.task_id],
        )
        # on_click = refresh_button.event_triggers["on_click"]

        group_refresh: list[rx.Component] = [refresh_button]

        # --- Gruppe: VSCode Buttons ---
        group_vscode: list[rx.Component] = []
        vs_cond = None

        if config.allow_vscode:
            vscode_button = VSCodeButtonBase.create(widget_state=cls.widget_state)
            group_vscode.append(vscode_button)
            vs_cond = vscode_button.children[0].cond

            if config.injectible:
                group_vscode.append(
                    VSCodeInjectButton.create(
                        config=config,
                        cond=vs_cond,
                    )
                )

            group_vscode.append(
                VSCodeLinkButton.create(
                    widget_state=cls.widget_state,
                    cond=vs_cond,
                )
            )

        # --- Gruppe: Kali Buttons ---
        group_kali: list[rx.Component] = []

        if config.allow_kali:
            kali_button = KaliButtonBase.create(widget_state=cls.widget_state)
            group_kali.append(kali_button)

            kl_cond = kali_button.children[0].cond

            group_kali.append(
                KaliLinkButton.create(
                    widget_state=cls.widget_state,
                    cond=kl_cond,
                )
            )

        # --- Gruppe: Cyber Range ---
        group_cyber_range: list[rx.Component] = []

        if config.allow_cyber_range:

            ready_cond = CondState.cyber_range_running & ~CondState.cyber_range_busy

            # --- FALL A: Cyber Range bereit → Buttons anzeigen ---
            group_cyber_range.append(
                rx.cond(
                    ready_cond & cls.widget_state.is_answerable,
                    rx.hstack(
                        CyberRangeLinkButton.create(
                            widget_state=cls.widget_state,
                            cond=ready_cond,
                        ),
                        CyberRangeUserCopyButton.create(
                            cond=ready_cond,
                        ),
                        CyberRangePasswordCopyButton.create(
                            cond=ready_cond,
                        ),
                        spacing="3",
                    ),
                )
            )

            # --- FALL B: Cyber Range NICHT bereit → Hinweistext anzeigen ---
            group_cyber_range.append(
                rx.cond(
                    ~ready_cond & cls.widget_state.is_answerable,
                    rx.cond(
                        CondState.cyber_range_busy,
                        rx.text(
                            "ℹ️ Cyber Range wird gerade erstellt/gestartet/zurückgesetzt... Bitte warten und Seite neu laden."
                        ),
                        rx.cond(
                            CondState.cyber_range_exists,
                            rx.text("⚠️ Cyber Range existiert, läuft aber nicht. Bitte Eventleitung informieren."),
                            rx.text("⚠️ Cyber Range wurde noch nicht erstellt! Bitte Eventleitung informieren."),
                        ),
                    ),
                )
            )

        # --- Gruppe: Download ---
        group_download: list[rx.Component] = []

        if config.allow_download:
            group_download.append(
                DownloadButtonBase.create(widget_state=cls.widget_state)
            )

        # --- Gruppe: Link ---
        group_link: list[rx.Component] = []

        if config.allow_link:
            group_link.append(
                CustomLinkButtonBase.create(widget_state=cls.widget_state)
            )

        # --- Banner-Komponenten ---
        def component_answer_banner() -> rx.Component:
            return rx.cond(
                cls.widget_state.solved,
                rx.vstack(
                    rx.callout(
                        f"Richtige Antwort! {cls.widget_state.current_points} Punkte erhalten.",
                        icon="check",
                        color_scheme="green",
                        width="100%",
                    ),
                    rx.cond(
                        PlayerCardState.show_answers,
                        rx.callout(
                            f"{cls.widget_state.solution}",
                            icon="info",
                            color_scheme="blue",
                            width="100%",
                        ),
                    ),
                    rx.cond(
                        cls.widget_state.first_blood,
                        rx.callout(
                            "Firstblood! 🩸",
                            icon="flame",
                            color_scheme="red",
                            width="100%",
                        ),
                    ),        
                    width="100%",
                ),
                rx.cond(
                    cls.attempted_solve,
                    rx.cond(
                        cls.is_solving,
                        rx.callout(
                            "Antwort wird geprüft...",
                            icon="loader-circle",
                            color_scheme="blue",
                            width="100%",
                        ),
                        rx.callout(
                            "Die Antwort ist falsch!",
                            icon="triangle_alert",
                            color_scheme="red",
                            role="alert",
                            width="100%",
                        ),
                    ),
                    rx.fragment(),
                ),
            )

        def component_hint_banner() -> rx.Component:
            def build_hint(text: str, index: int) -> rx.Component:
                return rx.callout.root(
                    rx.callout.icon(rx.icon("lightbulb"), margin_right="0.5rem"),
                    rx.callout.text(f"Hinweis {index + 1}: {text}"),
                    icon="info",
                    color_scheme="yellow",
                    width="100%",
                )

            #return rx.foreach(cls.widget_state.hints_unlocked, build_hint)

            return rx.cond(
                ~cls.widget_state.solved,
                rx.foreach(cls.widget_state.hints_unlocked, build_hint)
            )

        # --- Finales Layout: Jede Gruppe in einer eigenen Zeile ---
        panel = rx.vstack(
#            rx.hstack(*group_check, spacing="3") if group_check else rx.fragment(),
            rx.cond(
                cls.widget_state.is_answerable,
                rx.hstack(*group_check, spacing="3") if group_check else rx.fragment(),
                rx.hstack(*group_refresh, spacing="3") if group_refresh else rx.fragment(),
            ),
            rx.hstack(*group_vscode, spacing="3") if group_vscode else rx.fragment(),
            rx.hstack(*group_kali, spacing="3") if group_kali else rx.fragment(),
            rx.hstack(*group_cyber_range, spacing="3") if group_cyber_range else rx.fragment(),
            rx.hstack(*group_download, spacing="3") if group_download else rx.fragment(),
            rx.hstack(*group_link, spacing="3") if group_link else rx.fragment(),
            component_answer_banner(),
            component_hint_banner(),
            spacing="4",
            width="100%",
        )

        return panel, on_click

    @classmethod
    def get_component(cls, config: TaskWidgetConfiguration) -> Component:
        state = cls.widget_state
        is_loading: bool = ~cls.has_loaded

        answer_panel, answer_event = cls.component_answer_panel(cls, config)

        return rx.vstack(
            rx.flex(
                rx.heading(
                    rx.skeleton(rx.markdown(state.question), loading=is_loading),
                    as_="h2",
                    size="5",
                    overflow="clip",
                ),
                rx.spacer(),
                rx.text(
                    rx.skeleton(
                        f"{state.current_points}/{state.maximum_points} ✨",
                        loading=is_loading,
                    ),
                    padding_left="1em",
                ),
                width="100%",
            ),
            rx.skeleton(
                rx.markdown(state.question_further, overflow="clip"),
                loading=is_loading,
            ),
            rx.skeleton(
                cls.component_answer_field(cls, config, answer_event),
                loading=is_loading,
            ),
            rx.skeleton(
                answer_panel,
                loading=is_loading,
            ),
            cls.component_debug_panel(cls, config),
            spacing="3",
            width="100%",
            style={
                "borderRadius": "16px",
                "padding": "24px",
                "margin": "24px 0",
                "background": (
                    "linear-gradient(135deg, "
                    "rgba(220, 235, 255, 0.18) 0%, "
                    "rgba(200, 220, 255, 0.10) 100%)"
                ),
                "border": "1px solid rgba(255, 255, 255, 0.18)",
                "boxShadow": "0 2px 10px rgba(120, 160, 255, 0.18)",
            },
            on_mount=[cls.load_state_event(config.day_id, config.task_id)],
        )

TaskWidget: typing.Callable[[TaskData], rx.Component] = TaskWidgetClass.create
