import os
import base64
import typing
import logging
import string

import httpx
import reflex as rx

from urllib.parse import quote

from website.auth_lib import AuthCookie, BackendRequests
from website.engine.site import AbstractSiteBuilder


chapter_selection_mode = os.getenv("SET_CHAPTER_SELECTION")


# ---------------------------------------------------------
# CONDITIONAL / EVENT STATE
# ---------------------------------------------------------

class CondState(rx.State, BackendRequests):
    team_event_mode: bool = False
    team_event_leader_mode: bool = False
#    teams_list: List[str] = [""]

    async def get_team_event_info(self) -> None:
        response = await self.get("/admin/event/teamevent_mode")
        status = response.json()
        self.team_event_mode = status["teamevent_mode"]

        if status["teamevent_mode"]:
            response = await self.get("/admin/event/teamevent_leader_mode")
            status = response.json()
            self.team_event_leader_mode = status["teamevent_leader_mode"]

#            response = await self.get("/admin/event/get_event_teams_list")
#            status = response.json()
#            self.teams_list = status["teams_list"]


# ---------------------------------------------------------
# REGISTER STATE
# ---------------------------------------------------------

class RegisterState(AuthCookie, BackendRequests):
    progress_state: int = 0
    chosen_avatar: typing.Optional[int] = None

    username: str = ""
    username_valid: typing.Optional[int] = None
    password: str = ""
    password_repeat: str = ""

    team: str = ""
    team_leader: bool = False
    team_leader_exists: bool = False

    teams_list: list[str] = []
    team_colors: list[str] = []
    team_color_bg: str = "rgba(255,255,255,0.12)"
    team_color_border: str = "rgba(255,255,255,0.25)"
    team_color_glow: str = "rgba(255,255,255,0.15)"

    failed_register_message: str = ""

    def set_username(self, value: str) -> None:
        self.username = value

    def set_password(self, value: str) -> None:
        self.password = value

    def set_password_repeat(self, value: str) -> None:
        self.password_repeat = value

    def reset_states(self) -> None:
        self.reset()

    @rx.var
    def register_token(self) -> str:
        return self.router.url.query_parameters.get("token", "??")

    @rx.var
    def all_fields_valid(self) -> bool:
        return all(
            [
                len(self.username) >= 4,
                len(self.password) >= 8,
                self.password == self.password_repeat,
                self.username_valid == 1,
                self.check_passwords_valid == 1,
            ]
        )

    @rx.var
    def all_fields_valid_team_event(self) -> bool:
        return all(
            [
                len(self.username) >= 4,
                len(self.password) >= 8,
                self.password == self.password_repeat,
                self.username_valid == 1,
                self.check_passwords_valid == 1,
                self.team != "",
            ]
        )

    @rx.var
    def check_passwords_valid(self) -> int:
        if len(self.password) >= 10:
            if all(
                [
                    any(letter in string.ascii_lowercase for letter in self.password),
                    any(letter in string.ascii_uppercase for letter in self.password),
                    any(letter in string.digits for letter in self.password),
                    any(letter in string.punctuation for letter in self.password),
                ]
            ):
                return 1 if self.password == self.password_repeat else 2
            else:
                return 4
        else:
            return 3

    def complete_register(self):
        if chapter_selection_mode == "True":
            return rx.redirect("/login_chapter_selection")
        else:
            return rx.redirect("/login_redirect")

    async def check_username_valid(self, value: str) -> None:
        self.username = value
        if len(value) >= 4:
            try:
                async with httpx.AsyncClient(timeout=3) as client:
                    safe_username = quote(self.username, safe="")

#                    response = await client.get(
#                        self.build_url(
#                            f"/user/{safe_username}/exists", check_forbidden="true"
#                        )
#                    )

                    response = await self.get(
                        f"/user/{safe_username}/exists",
                        params={"check_forbidden": "true"}
                    )

                    text = response.json()
                    self.username_valid = 2 if text.get("exists", False) else 1

                    if text.get("forbidden", False):
                        self.username_valid = 4

            except Exception as e:
                logging.error(f"Failed to check username: {e}")
                self.username_valid = None
        else:
            self.username_valid = 3

    async def check_team_leader_exists(self, team_name: str) -> None:
        self.team = team_name
        try:
            async with httpx.AsyncClient(timeout=3) as client:
                safe_teamname = quote(team_name, safe="")
                response = await self.get(f"/teams/{safe_teamname}/leader_exists")
#                response = await client.get(
#                    self.build_url(f"/teams/{safe_teamname}/leader_exists")
#                )
                team_leader_response = response.json()
                self.team_leader_exists = team_leader_response["team_leader_exists"]
        except Exception as e:
            logging.error(f"Failed to check team leader: {e}")
            self.team_leader_exists = False

    async def register(self) -> None:
        async with httpx.AsyncClient() as client:
            password: str = base64.b64encode(
                self.password.encode("utf-8")
            ).decode("utf-8")
            data = {
                "username": self.username,
                "password": password,
                "avatar": str(self.chosen_avatar),
                "team": self.team,
                "team_leader": self.team_leader,
            }

            response = await self.post(
                f"/register_complete/{self.register_token}",
                params=data
            )
#            url = self.build_url(f"/register_complete/{self.register_token}")
#            response = await client.post(url, json=data)

            if response.status_code < 300:
                data = response.json()
                self.auth_cookie = data["token"]
                self.data_cookie = data["display_name"]
                self.avatar_index = data["avatar_index"]
                self.progress_state = 2

            elif response.status_code == 404:
                self.failed_register_message = "Invalider Token"

            elif response.status_code == 403:
                self.failed_register_message = (
                    "Token ist abgelaufen, forderen Sie einen neuen an!"
                )

            elif response.status_code == 409:
                self.failed_register_message = "Benutzername ist vergeben!"

            elif response.status_code == 412:
                self.failed_register_message = "Team hat bereits einen Leader"

            else:
                logging.error(
                    f"Failed to register: {response.status_code} {response.text}"
                )
                raise Exception(f"Failed to register: {response.status_code}")

    def back_to_avatar(self) -> None:
        self.progress_state = 0

    def set_avatar(self, index: int) -> None:
        self.chosen_avatar = index
        self.progress_state = 1

    # -------------------------------------------------
    # Team-Infos laden (Teams + Farben)
    # -------------------------------------------------
    async def load_team_event_info(self):
        try:
            response = await self.get("/admin/event/get_event_teams_list")
            status = response.json()
            self.teams_list = status["teams_list"]
        except Exception as e:
            logging.error(f"Error loading teams_list: {e}")
            self.teams_list = []

        try:
            response = await self.get("/admin/event/get_event_team_colors_list")
            status = response.json()
            self.team_colors = status["team_colors"]
        except Exception as e:
            logging.error(f"Error loading team_colors: {e}")
            self.team_colors = []

    # -------------------------------------------------
    # Team setzen + Farbe berechnen
    # -------------------------------------------------
    @rx.event
    async def set_team(self, team: str) -> None:
        self.team = team
        await self.check_team_leader_exists(team)

        if team in self.teams_list:
            idx = self.teams_list.index(team)
            base = self.team_colors[idx]  # z.B. "rgba(220,20,60,0.85)"

            try:
                parts = base.split(",")
                # rgba(r,g,b,a)
                r = parts[0][5:]
                g = parts[1]
                b = parts[2]

                self.team_color_bg = f"rgba({r},{g},{b},0.12)"
                self.team_color_border = f"rgba({r},{g},{b},0.35)"
                self.team_color_glow = f"rgba({r},{g},{b},0.35)"
            except Exception as e:
                logging.error(f"Error parsing team color '{base}': {e}")
                self.team_color_bg = "rgba(255,255,255,0.12)"
                self.team_color_border = "rgba(255,255,255,0.25)"
                self.team_color_glow = "rgba(255,255,255,0.15)"
        else:
            self.team_color_bg = "rgba(255,255,255,0.12)"
            self.team_color_border = "rgba(255,255,255,0.25)"
            self.team_color_glow = "rgba(255,255,255,0.15)"

    def toggle_team_leader(self) -> None:
        self.team_leader = not self.team_leader


# ---------------------------------------------------------
# REGISTER CARD (UI)
# ---------------------------------------------------------

class RegisterCard(AbstractSiteBuilder):
    @staticmethod
    def get_selection_field(text: str, options: list[str]) -> rx.Component:
        return rx.vstack(
            rx.text(
                text,
                size="3",
                weight="medium",
                text_align="left",
                width="100%",
            ),
            rx.box(
                rx.radio(
                    options,
                    size="3",
                    direction="column",
                    required=True,
                    on_change=RegisterState.set_team,
                    width="100%",
                    class_name="team-radio",
                ),
                max_height="250px",
                overflow_y="auto",
                padding="12px",
                border_radius="12px",
                width="100%",
                style={
                    "backgroundColor": RegisterState.team_color_bg,
                    "backdropFilter": "blur(10px)",
                    "border": f"1px solid {RegisterState.team_color_border}",
                    "boxShadow": f"0 4px 12px {RegisterState.team_color_glow}",
                    "transition": "all 0.25s ease",
                },
            ),
            justify="start",
            spacing="1",
            width="100%",
        )

    @staticmethod
    def get_input_field(
        text: str, hint: str, icon: str, **params
    ) -> rx.Component:
        return rx.vstack(
            rx.text(
                text,
                size="3",
                weight="medium",
                text_align="left",
                width="100%",
            ),
            rx.input(
                rx.input.slot(rx.icon(icon, color="#35373d")),
                placeholder=hint,
                size="3",
                width="100%",
                **params,
            ),
            justify_content="start",
            spacing="1",
            width="100%",
        )

    def statistics_card(self) -> rx.Component:
        return rx.card(
            rx.callout(
                "Registrierung erfolgreich!",
                icon="check",
                color_scheme="green",
                width="100%",
                margin_bottom="0.5em",
            ),
            rx.vstack(
                rx.center(
                    rx.heading(
                        "Alles ist bereit",
                        size="6",
                        as_="h2",
                        text_align="center",
                        width="100%",
                    ),
                    direction="column",
                    spacing="5",
                    width="100%",
                ),
                rx.text("Schön, dass Sie sich beim TCV CTF Event beteiligen!"),
                rx.text.strong("Danke! ❤️"),
                rx.text(
                    "Wir wünschen Ihnen viel Spaß bei der Jagd nach den Flaggen!"
                ),
                rx.container(height="0.5em"),
                rx.button(
                    "Capture the Flag!",
                    size="3",
                    width="100%",
                    on_click=RegisterState.complete_register,
                ),
                spacing="4",
                width="100%",
            ),
            max_width="28em",
            size="5",
            width="100%",
            class_name="login_card",
        )

    def signup_card(self) -> rx.Component:
        return rx.card(
            rx.vstack(
                rx.center(
                    rx.heading(
                        "Erstellen Sie einen Account",
                        size="6",
                        as_="h2",
                        text_align="center",
                        width="100%",
                    ),
                    direction="column",
                    spacing="5",
                    width="100%",
                ),
                self.get_input_field(
                    "🟊 Benutzername",
                    "Kreativer Benutzername",
                    "user",
                    value=RegisterState.username,
                    on_change=RegisterState.check_username_valid,
                    type="text",
                    max_length=16,
                ),
                rx.match(
                    RegisterState.username_valid,
                    (
                        1,
                        rx.callout(
                            f"{RegisterState.username} ist verfügbar",
                            icon="check",
                            color_scheme="green",
                            width="100%",
                        ),
                    ),
                    (
                        2,
                        rx.callout(
                            f"{RegisterState.username} ist bereits vergeben",
                            icon="triangle_alert",
                            color_scheme="red",
                            role="alert",
                            width="100%",
                        ),
                    ),
                    (
                        3,
                        rx.callout(
                            "Mindestens 4 Zeichen",
                            icon="triangle_alert",
                            color_scheme="red",
                            role="alert",
                            width="100%",
                        ),
                    ),
                    (
                        4,
                        rx.callout(
                            f"{RegisterState.username} ist nicht erlaubt!",
                            icon="triangle_alert",
                            color_scheme="red",
                            role="alert",
                            width="100%",
                        ),
                    ),
                ),
                self.get_input_field(
                    "🟊 Passwort",
                    "Sicheres Passwort",
                    "lock",
                    value=RegisterState.password,
                    on_change=RegisterState.set_password,
                    type="password",
                    max_length=128,
                ),
                self.get_input_field(
                    "🟊 Passwort wiederholen",
                    "Passwort wiederholen",
                    "repeat",
                    value=RegisterState.password_repeat,
                    on_change=RegisterState.set_password_repeat,
                    type="password",
                    max_length=128,
                ),
                rx.match(
                    RegisterState.check_passwords_valid,
                    (
                        1,
                        rx.callout(
                            "Passwörter stimmen überein",
                            icon="check",
                            color_scheme="green",
                            width="100%",
                        ),
                    ),
                    (
                        2,
                        rx.callout(
                            "Passwörter stimmen nicht überein",
                            icon="triangle_alert",
                            color_scheme="red",
                            role="alert",
                            width="100%",
                        ),
                    ),
                    (
                        3,
                        rx.callout(
                            "Mindestens 10 Zeichen",
                            icon="triangle_alert",
                            color_scheme="red",
                            role="alert",
                            width="100%",
                        ),
                    ),
                    (
                        4,
                        rx.callout(
                            "Passwort muss mindestens einen Großbuchstaben, "
                            "Kleinbuchstaben, eine Zahl und ein Sonderzeichen enthalten",
                            icon="triangle_alert",
                            color_scheme="red",
                            role="alert",
                            width="100%",
                        ),
                    ),
                ),
                rx.cond(
                    CondState.team_event_mode,
                    rx.vstack(
#                        self.get_selection_field("Wählen Sie Ihr Team",CondState.teams_list),
                        self.get_selection_field(
                            "Wählen Sie Ihr Team",
                            RegisterState.teams_list,
                        ),
                        rx.cond(
                            CondState.team_event_leader_mode,
                            rx.box(
                                rx.text("Sind Sie Team Leader?", size="3", weight="medium", text_align="left", width="100%",),
                                rx.cond(
                                    RegisterState.team_leader_exists,
                                    rx.tooltip(
                                        rx.checkbox(
                                            rx.text("Team Leader", as_="label"),
                                            default_checked=RegisterState.team_leader.to(bool),
                                            spacing="2",
                                            on_click=RegisterState.toggle_team_leader,
                                            disabled=True,  # explizit disabled
                                        ),
                                        content="Dieses Team hat bereits einen Leader",
                                        side="bottom",
                                    ),
                                    rx.tooltip(
                                        rx.checkbox(
                                            rx.text("Team Leader", as_="label"),
                                            default_checked=RegisterState.team_leader.to(bool),
                                            spacing="2",
                                            on_click=RegisterState.toggle_team_leader,
                                            disabled=False,
                                        ),
                                        content="Sie können Team Leader für dieses Team werden",
                                        side="bottom",
                                    ),
                                ),
                                width="100%",
                                margin_top="1.0em",
                            ),
                        ),
                        justify="start",
                        spacing="1",
                        width="100%",
                    ),
                ),
                rx.container(height="0.5em"),
                rx.flex(
                    rx.spacer(),
                    rx.button(
                        rx.icon("undo-2"),
                        size="3",
                        variant="soft",
                        on_click=RegisterState.back_to_avatar,
                        margin_right="0.5em",
                    ),
                    rx.cond(
                        CondState.team_event_mode,
                        rx.button(
                            "Jetzt registrieren",
                            size="3",
                            disabled=~RegisterState.all_fields_valid_team_event,
                            on_click=RegisterState.register,
                        ),
                        rx.button(
                            "Jetzt registrieren",
                            size="3",
                            disabled=~RegisterState.all_fields_valid,
                            on_click=RegisterState.register,
                        ),
                    ),
                    direction="row",
                    width="100%",
                ),
                rx.cond(
                    RegisterState.failed_register_message != "",
                    rx.callout(
                        RegisterState.failed_register_message,
                        icon="triangle_alert",
                        color_scheme="red",
                        role="alert",
                        width="100%",
                    ),
                ),
                spacing="4",
                width="100%",
            ),
            max_width="28em",
            size="5",
            width="100%",
            class_name="login_card",
        )

    @staticmethod
    def character_selection_card() -> rx.Component:
        def image_line(row: int) -> rx.Component:
            def image(index: int) -> rx.Component:
                return rx.flex(
                    rx.avatar(
                        src=f"/players/player_{index}.png",
                        fallback=f"Bild {index}",
                        radius="medium",
                        class_name="avatar_picture",
                    ),
                    on_click=lambda *_: RegisterState.set_avatar(index),
                    key=f"avatar_select_index_{index}",
                )

            items_count = 3
            return rx.center(
                rx.hstack(
                    *[
                        image(x)
                        for x in [row * items_count + i for i in range(items_count)]
                    ],
                    spacing="7",
                ),
                width="100%",
            )

        return rx.card(
            rx.vstack(
                rx.center(
                    rx.heading(
                        "Wählen Sie Ihren Avatar!",
                        size="6",
                        as_="h2",
                        text_align="center",
                        width="100%",
                    ),
                    direction="column",
                    spacing="5",
                    width="100%",
                ),
                *[image_line(x) for x in range(4)],
                spacing="7",
                width="100%",
            ),
            max_width="28em",
            size="5",
            width="100%",
            class_name="login_card",
        )

    def page(self) -> rx.Component:
        return rx.center(
            rx.hstack(
                rx.spacer(),
                rx.match(
                    RegisterState.progress_state,
                    (0, self.character_selection_card()),
                    (1, self.signup_card()),
                    (2, self.statistics_card()),
                ),
                rx.spacer(),
            ),
            width="100vw",
        )

    def configure(self) -> None:
        self.page_title = "Register"
        self.url = "/complete_register"
        self.is_standalone = True
        self.hide_sidebar = True
        self.background_class = "event_background_team"
        self.on_load = [
            RegisterState.reset_states,
            CondState.get_team_event_info,
            RegisterState.load_team_event_info
        ]
