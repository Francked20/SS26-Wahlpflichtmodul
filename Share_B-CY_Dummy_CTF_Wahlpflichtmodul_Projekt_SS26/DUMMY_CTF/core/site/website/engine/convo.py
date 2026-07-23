import os
import asyncio
import typing
import uuid
from dataclasses import dataclass
import re

from pydantic import BaseModel, ValidationError
import reflex as rx

__all__ = ["Player", "PlayerConversationWidget"]


@dataclass
class SpeedCategory:
    speed: float
    name: str


@dataclass
class Player:
    name: str
    position: typing.Literal["left", "right"] = ""

    def say(self, text: str, pose_left: str = "", pose_right: str = "") -> "PlayerSpeech":
        return PlayerSpeech(
            player=self,
            avatar_position_l=pose_left,
            avatar_position_r=pose_right,
            speech=text
        )


@dataclass
class PlayerSpeech:
    player: Player
    avatar_position_l: str
    avatar_position_r: str
    speech: str


class DisplaySettings(BaseModel):
    is_dyslexic: bool = False
    speed_category: int = 0


class ConvoDisplayState(BaseModel):
    avatar_position: str = "left"
    player_name: str = ""
    player_pose_l: str = ""
    player_pose_r: str = ""

    def set_from_player(self, data: PlayerSpeech):
        self.avatar_position = data.player.position
        self.player_name = data.player.name
        self.player_pose_l = data.avatar_position_l
        self.player_pose_r = data.avatar_position_r


class _PlayerConversationWidgetMeta(rx.ComponentState):
    """
    Create conversations with this widget between two characters displayed on left and right.
    Define two Players and their conversation with .say().
    Have at least one dialogue!
    You can use this on top of other widgets too, probably.

    Settings get stored in a local cookie.
    """

    # _all_speeches: list[PlayerSpeech] = []

    _current_text_index: int = 0
    _current_speed_text: str = "schnell"
    to_display_text = "Laden..."
    _play_random: uuid.UUID = None

    convo_disp_state = ConvoDisplayState()
    last_has_shown: bool = False

    settings: DisplaySettings = DisplaySettings()
    has_loaded_settings: bool = False
    settings_store: str = rx.Cookie(name="PlayerDialogueSettings")

    def load_settings(self) -> None:
        if not self.has_loaded_settings:
            try:
                self.settings = DisplaySettings.model_validate_json(self.settings_store)
            except ValidationError:
                self.save_settings()
            self.has_loaded_settings = True

    def save_settings(self) -> None:
        self.settings_store = self.settings.model_dump_json()

    def toggle_dyslexic(self):
        self.settings.is_dyslexic = not self.settings.is_dyslexic

    def next_text(self):
        if len(self._all_speeches) > self._current_text_index + 1:
            self._current_text_index += 1

        else:
            self.last_has_shown = True

        self.convo_disp_state.set_from_player(self._all_speeches[self._current_text_index])

    def first_text(self):
        self._current_text_index = 0
        self.last_has_shown = False
        self.convo_disp_state.set_from_player(self._all_speeches[self._current_text_index])

    def last_text(self):
        self._current_text_index = max(self._current_text_index - 1, 0)
        self.convo_disp_state.set_from_player(self._all_speeches[self._current_text_index])
        self.last_has_shown = False

    def set_speed(self):
        self.settings.speed_category = (self.settings.speed_category + 1) % 4
        self._current_speed_text = self.get_speed_category().name
        # self.settings_store

    # @rx.var
    def icon_category(self) -> int:
        return self.settings.speed_category

    def get_speed_category(self) -> SpeedCategory:
        match self.settings.speed_category:
            case 0:
                return SpeedCategory(0, "instant")
            case 1:
                return SpeedCategory(0.10, "langsam")
            case 2:
                return SpeedCategory(0.03, "mittel")
            case 3:
                return SpeedCategory(0.01, "schnell")
            case _:
                raise NotImplementedError()

    @rx.event(background=True)
    async def write_text(self):
        random_value = uuid.uuid4()
        async with self:
            # set random as identifier for current action
            self._play_random = random_value

            if self.last_has_shown:
                self.to_display_text = self._all_speeches[-1].speech
                return

            self.to_display_text = ""

        current_index = self._current_text_index
        text_to_write = self._all_speeches[current_index].speech
        # re-group so / and - symbols are kept
        text_chunks = re.split(r'([- /]+)', text_to_write)
        text_chunks = ["".join(text_chunks[x:x + 2]) for x in range(0, len(text_chunks) - 1, 2)] + [text_chunks[-1]]

        # use counter -> more performant than .pop(0)
        counter = 0
        if self.get_speed_category().speed > 0:
            await asyncio.sleep(0.2)

            # stop on text skipping
            while random_value == self._play_random:
                try:
                    chunk = text_chunks[counter]
                    counter += 1
                except IndexError:
                    if len(self._all_speeches) == current_index + 1:
                        async with self:
                            self.last_has_shown = True

                    return

                async with self:
                    self.to_display_text = f"{self.to_display_text}{chunk}"

                await asyncio.sleep((len(chunk) + 1) * self.get_speed_category().speed)

        else:
            async with self:
                self.to_display_text = text_to_write

    @staticmethod
    def abstract_icon(icon, typehint, func, color) -> rx.Component:
        return rx.tooltip(
            rx.icon(
                icon,
                color=color,
                size=32,
                on_click=func,
                class_name="forward_button"
            ),
            content=typehint,
            delay_duration=750,
            class_name="typehint"
        )

    @classmethod
    def get_component(cls, chapter: str, player_left: Player, player_right: Player, texts: list[PlayerSpeech]) -> "rx.Component":
#    def get_component(cls, player_left: Player, player_right: Player, texts: list[PlayerSpeech]) -> "rx.Component":
        assert len(texts) > 0
        cls._all_speeches = texts
        # cls.__fields__["_all_speeches"].default = texts  # noqa

        # set players
        player_left.position = "left"
        player_right.position = "right"

        # ToDo: required?
        # cls.convo_disp_state.set_from_player(texts[0])

        def speed_button(icon: str):
            return cls.abstract_icon(
                icon,
                f"Schreibgeschwindigkeit: {cls._current_speed_text}",
                cls.set_speed, "#707080"
            )

        def player_display():
            file_l = f"/poses/player_{player_left.name.lower()}_{cls.convo_disp_state.player_pose_l.lower()}.png"
#            file_r = f"/poses/player_{player_right.name.lower()}_{cls.convo_disp_state.player_pose_r.lower()}.png"

            return rx.container(
                rx.image(
                    src=file_l,
                    class_name="player_avatar",
#                    class_name=rx.cond(
#                        cls.convo_disp_state.player_name.to(str).lower() == player_right.name.lower(),
#                        "player_avatar un_focus",
#                        "player_avatar"
#                    ),
                    style=rx.style.Style({"left": "5vw"}),
                    alt="Player Left"
                ),
#                rx.image(
#                    src=file_r,
#                    class_name=rx.cond(
#                        cls.convo_disp_state.player_name.to(str).lower() == player_left.name.lower(),
#                        "player_avatar un_focus",
#                        "player_avatar"
#                    ),
#                    style=rx.style.Style({"right": "5vw"}),
#                    alt="Player Right"
#                ),
            )

        def settings_card() -> rx.Component:
            return rx.popover.root(
                rx.popover.trigger(
                    rx.icon(
                        "settings",
                        size=32,
                        class_name="settings_icon forward_button",
                    )
                ),
                rx.popover.content(
                    rx.vstack(
                        rx.cond(
                            cls.has_loaded_settings,
                            rx.vstack(
                                rx.match(
                                    cls.settings.speed_category,
                                    (0, speed_button("zap")),
                                    (1, speed_button("snail")),
                                    (2, speed_button("fish")),
                                    (3, speed_button("rabbit")),
                                    speed_button("dot"),
                                ),
                                rx.cond(
                                    cls.settings.is_dyslexic,
                                    cls.abstract_icon("star", "Schrift für Legastheniker: an",
                                                      cls.toggle_dyslexic, "#707080"),
                                    cls.abstract_icon("star-off", "Schrift für Legastheniker: aus",
                                                      cls.toggle_dyslexic, "#707080"),
                                ),
                                rx.tooltip(
                                    rx.popover.close(
                                        rx.icon(
                                            "x",
                                            color="#D22B2B",
                                            size=32,
                                            class_name="forward_button"
                                        ),
                                    ),
                                    content="Einstellungen schließen",
                                    delay_duration=750,
                                    class_name="typehint"
                                ),
                            ),
                            rx.vstack(
                                speed_button("dot"),
                                speed_button("dot"),
                            ),
                        ),
                    ),
                    class_name="settings_card"
                ),
            )

        name = rx.cond(
            cls.convo_disp_state.player_name.to(str) == "",
            "",
            f"➤ {cls.convo_disp_state.player_name}",
        )

        return rx.container(
            rx.hstack(
                rx.tooltip(
                    rx.icon(
                        "chevrons_left",
                        color="white",
                        size=36,
                        on_click=[
                            cls.last_text,
                            cls.write_text,
                        ],
                        margin="0.35em",
                        position="absolute",
                        bottom="0",
                        class_name="forward_button",
                    ),
                    content="Zurück",
                    delay_duration=1000,
                    class_name="typehint",
                ),
                rx.hstack(
                    rx.spacer(),
                    rx.cond(
                        cls.settings.is_dyslexic,
                        rx.text(
                            name,
                            class_name="text_dyslexic"
                        ),
                        rx.text(
                            name,
                            class_name="text_not_dyslexic"
                        ),
                    ),
                    rx.spacer(),
                    class_name="name_display"
                ),
                rx.scroll_area(
                    rx.cond(
                        cls.settings.is_dyslexic,
                        rx.text(
                            cls.to_display_text,
                            class_name="dialogue_text text_dyslexic"
                        ),
                        rx.text(
                            cls.to_display_text,
                            class_name="dialogue_text text_not_dyslexic"
                        ),
                    ),
                    width="100%",
                    type="auto",
                    scrollbars="vertical",
                    class_name="talk_box_scroll",
                    on_mount=[cls.write_text],
                    on_click=[cls.next_text, cls.write_text],
                ),
                rx.cond(
                    cls.last_has_shown,
                    rx.link(
                        rx.tooltip(
                            rx.icon(
                                "circle-check",
                                color="white",
                                on_click=[cls.first_text],
                                size=36,
                                margin="0.35em",
                                bottom="0",
                                right="0",
                                position="absolute",
                                class_name="forward_button"
                            ),
                            content="Szene beenden",
                            delay_duration=1000,
                            class_name="typehint"
                        ),

                        href=f"https://{os.getenv('DOMAIN')}/challenge_{chapter}/"
                    ),
                    rx.tooltip(
                        rx.icon(
                            "chevrons_right",
                            color="white",
                            size=36,
                            on_click=[cls.next_text, cls.write_text],
                            margin="0.35em",
                            bottom="0",
                            right="0",
                            position="absolute",
                            class_name="forward_button",
                        ),
                        content="Weiter",
                        delay_duration=1000,
                        class_name="typehint"
                    ),
                ),
                settings_card(),
                class_name=f"talk_box talk_box_bubble_{cls.convo_disp_state.avatar_position.to(str)}",
                on_mount=[cls.load_settings],
            ),
            player_display(),
        )


PlayerConversationWidget = _PlayerConversationWidgetMeta
