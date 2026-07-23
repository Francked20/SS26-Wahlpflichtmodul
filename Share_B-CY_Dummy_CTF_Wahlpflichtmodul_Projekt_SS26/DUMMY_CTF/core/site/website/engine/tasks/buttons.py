import os
import asyncio
import typing

from website.engine.challenge import CondState
from website.engine.task_conf import PlayerCardState

import reflex as rx
from reflex import Component

if typing.TYPE_CHECKING:
    from engine.tasks.models import TaskWidgetState, TaskWidgetConfiguration


class BaseCooldownButton(rx.State, mixin=True):
    cooldown_active: bool = False

    @rx.event(background=True)
    async def cooldown(self, cooldown_time: int):
        async with self:
            self.cooldown_active = True
        await asyncio.sleep(cooldown_time)
        async with self:
            self.cooldown_active = False


class RefreshButtonBase(BaseCooldownButton, rx.ComponentState):
    @classmethod
    def get_component(
            cls,
            widget_state: "TaskWidgetState",
            on_action: tuple[rx.EventHandler, ...],
            cooldown_time: int = 3,
    ) -> Component:
        click_events = [
            cls.cooldown(cooldown_time),
        ]
        call, *args = on_action

        if not isinstance(call, rx.EventHandler):
            raise ValueError(f"First argument in {cls.__class__.__name__} must be an event.")
        if not call.is_background:
            raise ValueError(f"Event for {cls.__class__.__name__} must be a background event!")

        parameters: dict = getattr(call, "__parameters", None)
        parameters: dict = getattr(call, "__parameters", None)

        if parameters and len(parameters.keys()) - 1 != len(args):
            raise ValueError("Arguments are not the same length as action parameters!")
        click_events.append(call(*args))

        return rx.button(
            rx.cond(
                widget_state.solved,
                rx.text("Gelöst!"),
                rx.cond(cls.cooldown_active, rx.text("Cooldown"), rx.text("Refresh")),
            ),
            rx.cond(
                widget_state.solved,
                rx.icon("party-popper"),
                rx.cond(cls.cooldown_active, rx.icon("clock"), rx.icon("refresh-ccw")),
            ),
            size="3",
            color_scheme="blue",
            variant="solid",
            style={"cursor": "pointer"},
            on_click=click_events,
            # loading=is_solving,
            disabled=cls.cooldown_active | widget_state.solved,  # | is_solving | manual_disable,
        )


class SolutionButtonBase(BaseCooldownButton, rx.ComponentState):
    @classmethod
    def get_component(
            cls,
            widget_state: "TaskWidgetState",
            on_action: tuple[rx.EventHandler, ...],
            is_solving: bool,
            manual_disable: bool,
            cooldown_time: int = 3,
    ) -> Component:
        click_events = [
            cls.cooldown(cooldown_time),
            PlayerCardState.set_old_level(),
        ]
        call, *args = on_action

        if not isinstance(call, rx.EventHandler):
            raise ValueError(f"First argument in {cls.__class__.__name__} must be an event.")
        if not call.is_background:
            raise ValueError(f"Event for {cls.__class__.__name__} must be a background event!")

        parameters: dict = getattr(call, "__parameters", None)

        if parameters and len(parameters.keys()) - 1 != len(args):
            raise ValueError("Arguments are not the same length as action parameters!")

        click_events.append(call(*args))
        click_events.append(PlayerCardState.check_new_level())

        return rx.button(
            rx.cond(
                widget_state.solved,
                rx.text("Gelöst!"),
                rx.cond(cls.cooldown_active, rx.text("Cooldown"), rx.text("Überprüfen")),
            ),
            rx.cond(
                widget_state.solved,
                rx.icon("party-popper"),
                rx.cond(cls.cooldown_active, rx.icon("clock"), rx.icon("send")),
            ),
            size="3",
            color_scheme="blue",
            variant="solid",
            style={"cursor": "pointer"},
            on_click=click_events,
            # loading=is_solving,
            disabled=cls.cooldown_active | widget_state.solved | is_solving | manual_disable,
        )


class HintButton(rx.ComponentState):
    @classmethod
    def get_component(
            cls,
            widget_state: "TaskWidgetState",
            on_action: tuple[rx.EventHandler, ...],
    ) -> Component:
        call, *args = on_action

        return rx.cond(
            (widget_state.current_points == 0) | (widget_state.hints_point_cap[
                                                      widget_state.hints_unlocked.length()] >= widget_state.current_points),
            rx.button(
                rx.icon("lightbulb"),
                rx.text.strong("Gratis-Hinweis"),
                size="3",
                color_scheme="amber",
                style={"cursor": "pointer"},
                variant="soft",
                on_click=[call(*args)],
                disabled=widget_state.solved | ~(
                        widget_state.hints_unlocked.length() < widget_state.hints_point_cap.length()),
            ),
            rx.alert_dialog.root(
                rx.alert_dialog.trigger(
                    rx.button(
                        rx.icon("lightbulb"),
                        rx.cond(
                            widget_state.hints_unlocked.length() < widget_state.hints_point_cap.length(),
                            rx.text("Hinweis anfordern"),
                            rx.text("Keine Hinweise verfügbar"),
                        ),
                        size="3",
                        color_scheme="amber",
                        style={"cursor": "pointer"},
                        variant="soft",
                        disabled=widget_state.solved | ~(
                                widget_state.hints_unlocked.length() < widget_state.hints_point_cap.length()),
                    ),
                ),
                rx.alert_dialog.content(
                    rx.alert_dialog.title(
                        f"{widget_state.hints_unlocked.length() + 1}. Hinweis Anfordern?"),
                    rx.alert_dialog.description(
                        rx.markdown(
                            "Der nächste Hinweis wird die maximal erreichbare Punktzahl für "
                            f"diese Aufgabe auf nur **{widget_state.hints_point_cap[widget_state.hints_unlocked.length()]} "
                            "Punkte** begrenzen. Trotzdem fortfahren?"
                        ),
                        size="2",
                    ),
                    rx.flex(
                        rx.alert_dialog.cancel(
                            rx.button(
                                "Abbrechen",
                                size="3",
                                variant="soft",
                                color_scheme="gray",
                            )
                        ),
                        rx.alert_dialog.action(
                            rx.button(
                                rx.icon("lightbulb"),
                                rx.text.strong("Anfordern"),
                                size="3",
                                variant="soft",
                                color_scheme="yellow",
                                on_click=[call(*args)],
                            )
                        ),
                        spacing="3",
                        margin_top="16px",
                        justify="end",
                    ),
                ),
            )
        )


class DownloadButtonBase(BaseCooldownButton, rx.ComponentState):
    @classmethod
    def get_component(cls, widget_state: "TaskWidgetState", ) -> Component:
        return rx.button(
            rx.icon("download"),
            rx.text(widget_state.download_text),
            size="3",
            variant="soft",
            color_scheme="gray",
            style={"cursor": "pointer"},
            on_click=rx.download(url=widget_state.download_path)
        )


class CustomLinkButtonBase(BaseCooldownButton, rx.ComponentState):
    @classmethod
    def get_component(cls, widget_state: "TaskWidgetState", ) -> Component:
        return rx.link(
            rx.button(
                rx.icon("link"),
                rx.text(widget_state.link_text),
                size="3",
                variant="soft",
                color_scheme="gray",
                style={"cursor": "pointer"}
            ),
            href=f"https://{os.getenv('DOMAIN')}/{widget_state.link_path}",
            is_external=True
        )


class LinkButtonBase(rx.ComponentState, mixin=True):
    @classmethod
    def get_component(
            cls,
            widget_state: "TaskWidgetState",
            icon: str = "link",
            text: str = "Click!",
            href: str = "",
            color_scheme: str = "mint",
            is_external: bool = True,
            disabled: bool = None
    ) -> Component:
        disabled = disabled if disabled else False

        return rx.link(
            rx.button(
                rx.icon(icon),
                rx.text(text),
                size="3",
                variant="soft",
                color_scheme=color_scheme,
                style={"cursor": "pointer"},
                disabled=disabled,
            ),
            href=CondState.code_server_domain,
            is_external=True,
        )


class VSCodeButtonBase(BaseCooldownButton, rx.ComponentState):
    @classmethod
    def get_component(cls, widget_state: "TaskWidgetState", cooldown_time: int = 7) -> Component:
        return rx.cond(
            CondState.code_server_running & ~cls.cooldown_active,
            rx.alert_dialog.root(
                rx.alert_dialog.trigger(
                    rx.button(
                        rx.icon("ban"),
                        rx.text("VSCode stoppen"),
                        size="3",
                        color_scheme="red",
                        variant="soft",
                        style={"cursor": "pointer"},
                        disabled=cls.cooldown_active
                    )
                ),
                rx.alert_dialog.content(
                    rx.alert_dialog.title("VSCode stoppen?"),
                    rx.alert_dialog.description(
                        rx.markdown(
                            "Dies wird den VSCode Container beenden. Fortfahren?"
                        ),
                        size="2",
                    ),
                    rx.flex(
                        rx.alert_dialog.cancel(
                            rx.button(
                                "Abbrechen",
                                size="3",
                                variant="soft",
                                color_scheme="gray",
                            )
                        ),
                        rx.alert_dialog.action(
                            rx.button(
                                rx.icon("ban"),
                                rx.text.strong("VSCode stoppen"),
                                size="3",
                                color_scheme="red",
                                on_click=[cls.cooldown(cooldown_time), CondState.stop_code_server],
                            )
                        ),
                        spacing="3",
                        margin_top="16px",
                        justify="end",
                    ),
                ),
            ),
            rx.cond(
                cls.cooldown_active,
                rx.button(
                    rx.icon("files"),
                    rx.text("VSCode startet"),
                    size="3",
                    variant="soft",
                    color_scheme="iris",
                    style={"cursor": "not-allowed"},
                    disabled=True,
                ),
                rx.button(
                    rx.icon("files"),
                    rx.text("VSCode starten"),
                    size="3",
                    variant="soft",
                    color_scheme="iris",
                    on_click=[cls.cooldown(cooldown_time), CondState.start_code_server],
                    style={"cursor": "pointer"},
                    disabled=widget_state.solved,
                ),
            )
        )


class VSCodeLinkButton(LinkButtonBase):
    @classmethod
    def get_component(cls, widget_state: "TaskWidgetState", cond) -> Component:
        return rx.cond(
            cond,
            super().get_component(
                widget_state=widget_state, icon="link", text="VSCode",
                href=CondState.code_server_domain,
                color_scheme="iris",
                disabled=False
            ),
            rx.button(
                rx.icon("link"),
                rx.text("VSCode"),
                size="3",
                variant="soft",
                color_scheme="gray",
                style={"cursor": "not-allowed"},
                disabled=True,
            ),
        )


class VSCodeInjectButton(BaseCooldownButton, rx.ComponentState):
    @classmethod
    def get_component(cls, config: "TaskWidgetConfiguration", cond,
                      cooldown_time: int = 5, ) -> Component:
        return rx.button(
            rx.icon("play"),
            rx.text("Lade Dateien"),
            size="3",
            variant="soft",
            color_scheme="iris",
            on_click=[
                cls.cooldown(cooldown_time),
                CondState.inject_challenge(
                    config.day_id,
                    config.task_id,
                    None,  # ToDo: Check challenge index??
                ),
            ],
            style={"cursor": "pointer"},
            disabled=~cond | cls.cooldown_active,
        )


class KaliButtonBase(BaseCooldownButton, rx.ComponentState):
    @classmethod
    def get_component(cls, widget_state: "TaskWidgetState", cooldown_time: int = 7) -> Component:
        return rx.cond(
            CondState.kali_server_running & ~cls.cooldown_active,
            rx.alert_dialog.root(
                rx.alert_dialog.trigger(
                    rx.button(
                        rx.icon("ban"),
                        rx.text("Kali stoppen"),
                        size="3",
                        color_scheme="red",
                        variant="soft",
                        style={"cursor": "pointer"},
                        disabled=cls.cooldown_active
                    )
                ),
                rx.alert_dialog.content(
                    rx.alert_dialog.title("Kali stoppen?"),
                    rx.alert_dialog.description(
                        rx.markdown(
                            "Dies wird den Kali Container beenden. Fortfahren?"
                        ),
                        size="2",
                    ),
                    rx.flex(
                        rx.alert_dialog.cancel(
                            rx.button(
                                "Abbrechen",
                                size="3",
                                variant="soft",
                                color_scheme="gray",
                            )
                        ),
                        rx.alert_dialog.action(
                            rx.button(
                                rx.icon("ban"),
                                rx.text.strong("Kali stoppen"),
                                size="3",
                                color_scheme="red",
                                on_click=[cls.cooldown(cooldown_time), CondState.stop_kali_server],
                            )
                        ),
                        spacing="3",
                        margin_top="16px",
                        justify="end",
                    ),
                )
            ),
            rx.cond(
                cls.cooldown_active,
                rx.button(
                    rx.icon("swords"),
                    rx.text("Kali startet"),
                    size="3",
                    variant="soft",
                    color_scheme="mint",
                    style={"cursor": "not-allowed"},
                    disabled=True,
                ),
                rx.button(
                    rx.icon("swords"),
                    rx.text("Kali starten"),
                    size="3",
                    variant="soft",
                    color_scheme="mint",
                    on_click=[cls.cooldown(cooldown_time), CondState.start_kali_server],
                    style={"cursor": "pointer"},
                    disabled=widget_state.solved,
                ),
            )
        )


class KaliLinkButton(LinkButtonBase):
    @classmethod
    def get_component(cls, widget_state: "TaskWidgetState", cond) -> Component:
        return rx.cond(
            cond,
            super().get_component(
                widget_state=widget_state, icon="link", text="Kali",
                href=CondState.kali_server_domain,
                color_scheme="mint",
                disabled=False
            ),
            rx.button(
                rx.icon("link"),
                rx.text("Kali"),
                size="3",
                variant="soft",
                color_scheme="gray",
                style={"cursor": "not-allowed"},
                disabled=True,
            ),
        )


class CyberRangeLinkButton(LinkButtonBase):
    @classmethod
    def get_component(cls, widget_state: "TaskWidgetState", cond) -> Component:
        return rx.cond(
            cond,
            # --- FALL A: Cyber Range bereit → Button anzeigen ---
            rx.button(
                rx.icon("target"),
                rx.text("Cyber Range"),
                size="3",
                variant="soft",
                color_scheme="mint",
                on_click=[
                    lambda: rx.redirect(CondState.cyber_range_domain, is_external=True),
                ],
                style={"cursor": "pointer"},
            ),
            # --- FALL B: Cyber Range NICHT bereit → Disabled Button ---
            rx.button(
                rx.icon("target"),
                rx.text("Cyber Range"),
                size="3",
                variant="soft",
                color_scheme="gray",
                disabled=True,
                style={"cursor": "not-allowed"},
            ),
        )


class CyberRangeUserCopyButton(rx.ComponentState):
    @classmethod
    def get_component(cls, cond) -> Component:
        return rx.cond(
            cond,
            rx.button(
                rx.icon("square-user-round"),
                rx.text("Benutzername kopieren"),
                size="3",
                variant="soft",
                color_scheme="sky",
                on_click=[
                    rx.set_clipboard(CondState.cyber_range_user),
                    lambda: CondState.cyber_range_user_toast(),
                ],
                style={"cursor": "pointer"},
            ),
            rx.button(
                rx.icon("square-user-round"),
                rx.text("Benutzername kopieren"),
                size="3",
                variant="soft",
                color_scheme="gray",
                disabled=True,
                style={"cursor": "not-allowed"},
            ),
        )


class CyberRangePasswordCopyButton(rx.ComponentState):
    @classmethod
    def get_component(cls, cond) -> Component:
        return rx.cond(
            cond,
            rx.button(
                rx.icon("square-asterisk"),
                rx.text("Passwort kopieren"),
                size="3",
                variant="soft",
                color_scheme="sky",
                on_click=[
                    rx.set_clipboard(CondState.cyber_range_password),
                    lambda: CondState.cyber_range_pw_toast(),
                ],
                style={"cursor": "pointer"},
            ),
            rx.button(
                rx.icon("square-asterisk"),
                rx.text("Passwort kopieren"),
                size="3",
                variant="soft",
                color_scheme="gray",
                disabled=True,
                style={"cursor": "not-allowed"},
            ),
        )


class ResetButtonBase(BaseCooldownButton, rx.ComponentState):
    @classmethod
    def get_component(
            cls,
            widget_state: "TaskWidgetState",
            on_action: tuple[rx.EventHandler, ...],
            cooldown_time=10,
    ) -> Component:
        click_events = [
            cls.cooldown(cooldown_time),
            PlayerCardState.set_old_level(),
        ]

        call, *args = on_action
        click_events.append(call(*args))
        click_events.append(PlayerCardState.check_new_level())

        return rx.button(
            rx.icon("rotate-ccw"),
            rx.text("Reset"),
            size="3",
            variant="soft",
            color_scheme="red",
            style={"cursor": "pointer"},
            on_click=click_events,
            disabled=cls.cooldown_active | ~widget_state.solved,
        )
