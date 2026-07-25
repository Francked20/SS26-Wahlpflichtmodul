import os
import base64
import logging
import string

import httpx
import reflex as rx

from website.auth_lib import AuthCookie, BackendRequests
from website.engine.site import AbstractSiteBuilder

chapter_selection_mode = os.getenv("SET_CHAPTER_SELECTION")

class ResetPWState(AuthCookie, BackendRequests):
    progress_state: int = 0

#    username: str = ""
#    username_valid: typing.Optional[int] = None
    password: str = ""
    password_repeat: str = ""

    failed_reset_pw_message: str = ""

    def set_password(self, value: str) -> None:
        self.password = value

    def set_password_repeat(self, value: str) -> None:
        self.password_repeat = value

    def reset_states(self):
        self.reset()

    @rx.var
    def reset_pw_token(self) -> str:
        return self.router.url.query_parameters.get("token", "??")

    @rx.var
    def all_fields_valid(self) -> bool:
        return all([
            len(self.password) >= 8,
            self.password == self.password_repeat,
            self.check_passwords_valid == 1,
        ])

    @rx.var
    def check_passwords_valid(self) -> int:
        if len(self.password) >= 10:
            if all([
                any(letter in string.ascii_lowercase for letter in self.password),
                any(letter in string.ascii_uppercase for letter in self.password),
                any(letter in string.digits for letter in self.password),
                any(letter in string.punctuation for letter in self.password),
            ]):
                return 1 if self.password == self.password_repeat else 2
            else:
                return 4
        else:
            return 3

    def complete_pw_reset(self):
        # ToDo: send data to backend

        if chapter_selection_mode == "True":
            return rx.redirect("/login_chapter_selection")
        else:
            return rx.redirect("/login_redirect")

    async def reset_user_pw(self):
        async with httpx.AsyncClient() as client:
            password: str = base64.b64encode(self.password.encode("utf-8")).decode("utf-8")
            data = {
#                "username": self.username,
                "password": password,
#                "avatar": str(self.chosen_avatar)
            }
#            url = self.build_url(f"/reset_password/{self.reset_pw_token}")
#            response = await client.post(url, json=data)

            response = await self.post(
                f"/reset_password/{self.reset_pw_token}",
                params=data
            )


            if response.status_code < 300:
                data = response.json()
                self.auth_cookie = data["token"]
                self.data_cookie = data["display_name"]
                self.avatar_index = data["avatar_index"]

                self.progress_state = 1

            elif response.status_code == 404:
                self.failed_reset_pw_message = "Invalider Token"

            elif response.status_code == 403:
                self.failed_reset_pw_message = "Token ist abgelaufen, forderen Sie einen neuen an!"

            elif response.status_code == 402:
                self.failed_reset_pw_message = "User nicht registriert"

            else:
                logging.error(f"Failed to reset password: {response.status_code} {response.text}")
                raise Exception(f"Failed to reset password: {response.status_code}")

#    def back_to_avatar(self):
#        self.progress_state = 0
#
#    def set_avatar(self, index: int):
#        self.chosen_avatar = index
#        self.progress_state = 1


class ResetPWCard(AbstractSiteBuilder):
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
            rx.radio(
                options,
                size="3",
                direction="row",
            ),
            justify="start",
            spacing="1",
            width="100%",
        )

    @staticmethod
    def get_input_field(text: str, hint: str, icon: str, **params) -> rx.Component:
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
            justify="start",
            spacing="1",
            width="100%",
        )

    def statistics_card(self) -> rx.Component:
        return rx.card(
            rx.callout(
                "Zurücksetzen des Passwortes erfolgreich!",
                icon="check",
                color_scheme="green",
                width="100%",
                margin_bottom="0.5em"
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
                rx.text("Das hat geklappt. Schön, Sie wieder begrüßen zu dürfen!"),
                rx.text.strong("Danke! ❤️"),
                rx.text("Wir wünschen Ihnen weiterhin viel Spaß bei der Jagd nach den Flaggen!"),
                rx.container(height="0.5em"),
                rx.button(
                    "Capture the Flag!",
                    size="3",
                    width="100%",
                    on_click=ResetPWState.complete_pw_reset,
                ),
                spacing="4",
                width="100%",
            ),          
            max_width="28em",
            size="5",
            width="100%",
            class_name="login_card",
        )

    def pw_reset_card(self) -> rx.Component:
        return rx.card(
            rx.vstack(
                rx.center(
                    rx.heading(
                        "Wählen Sie ein neues Passwort",
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
                    "🟊 Passwort",
                    "Sicheres Passwort",
                    "lock",
                    value=ResetPWState.password,
                    on_change=ResetPWState.set_password,
                    type="password",
                    max_length=128,
                ),
                self.get_input_field(
                    "🟊 Passwort wiederholen",
                    "Passwort wiederholen",
                    "repeat",
                    value=ResetPWState.password_repeat,
                    on_change=ResetPWState.set_password_repeat,
                    type="password",
                    max_length=128,
                ),
                rx.match(
                    ResetPWState.check_passwords_valid,
                    (1, rx.callout(
                        "Passwörter stimmen überein",
                        icon="check",
                        color_scheme="green",
                        width="100%",
                    )),
                    (2, rx.callout(
                        "Passwörter stimmen nicht überein",
                        icon="triangle_alert",
                        color_scheme="red",
                        role="alert",
                        width="100%",
                    )),
                    (3, rx.callout(
                        "Mindestens 10 Zeichen",
                        icon="triangle_alert",
                        color_scheme="red",
                        role="alert",
                        width="100%",
                    )),
                    (4, rx.callout(
                        "Passwort muss mindestens einen Großbuchstaben, Kleinbuchstaben, eine Zahl und ein Sonderzeichen enthalten",
                        icon="triangle_alert",
                        color_scheme="red",
                        role="alert",
                        width="100%",
                    )),
                ),
                rx.container(height="0.5em"),
                rx.flex(
#                    rx.spacer(),
#                    rx.button(
#                        rx.icon("undo-2"),
#                        size="3",
#                        variant="soft",
#                        on_click=ResetPWState.back_to_avatar,
#                        margin_right="0.5em",
#                    ),
                    rx.button(
                        "Neues Passwort setzen",
                        size="3",
                        width="100%",
                        disabled=~ResetPWState.all_fields_valid,
                        on_click=ResetPWState.reset_user_pw,
                    ),
                    direction="row",
                    width="100%"
                ),
                rx.cond(
                    ResetPWState.failed_reset_pw_message != "",  # noqa
                    rx.callout(
                        ResetPWState.failed_reset_pw_message,
                        icon="triangle_alert",
                        color_scheme="red",
                        role="alert",
                        width="100%",
                    )
                ),
                spacing="4",
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
                    ResetPWState.progress_state,
                    (0, self.pw_reset_card()),
                    (1, self.statistics_card()),
                ),
                rx.spacer(),
            ),
            width="100vw",
        )

    def configure(self) -> None:
        self.page_title = "Password Reset"
        self.url = "/reset_password"
        self.is_standalone = True
        self.hide_sidebar = True
        self.background_class = "event_background_team"
        self.on_load = [ResetPWState.reset_states]
