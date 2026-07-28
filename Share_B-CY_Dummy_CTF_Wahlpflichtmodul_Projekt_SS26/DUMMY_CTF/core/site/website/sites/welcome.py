import os
import asyncio
from datetime import datetime
import typing

import reflex as rx

from website.engine.site import AbstractSiteBuilder
from website.auth_lib import AuthCookie, LoginState, BackendRequests

class _MatrixLetter:
    def __init__(self, leds: list[tuple[int, int]], width: int = None):
        self.width = width or 6
        self.leds = leds

class MatrixLetters:
    letters = {
        "arrow_stem": _MatrixLetter([
            (0, 2), (0, 3), (0, 4), (1, 2), (1, 3), (1, 4), (2, 2), (2, 3), (2, 4), (3, 2), (3, 3), (3, 4)
        ], width=3),
        "arrow_head": _MatrixLetter([
            (0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (2, 2),
            (2, 3), (2, 4), (3, 3)], width=5),
        "l": _MatrixLetter([
            (0, 0), (0, 6), (1, 0), (1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 6), (2, 6)
        ], width=4),
        "o": _MatrixLetter([
            (0, 3), (0, 4), (0, 5), (1, 2), (1, 6), (2, 2), (2, 6), (3, 2), (3, 6), (4, 3), (4, 4), (4, 5)
        ], width=6),
        "g": _MatrixLetter([
            (0, 3), (1, 2), (1, 4), (1, 6), (2, 2), (2, 4), (2, 6), (3, 2), (3, 4), (3, 6), (4, 2), (4, 3), (4, 4),
            (4, 5)
        ], width=6),
        "i": _MatrixLetter([
            (0, 2), (0, 6), (1, 0), (1, 2), (1, 3), (1, 4), (1, 5), (1, 6), (2, 6)
        ], width=4),
        "n": _MatrixLetter([
            (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (1, 3), (2, 2), (3, 2), (4, 3), (4, 4), (4, 5), (4, 6)
        ], width=6),
        "r": _MatrixLetter([
            (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (1, 3), (2, 2), (3, 2)
        ], width=5),
        "e": _MatrixLetter([
            (0, 3), (0, 4), (0, 5), (1, 2), (1, 4), (1, 6), (2, 2), (2, 4), (2, 6), (3, 2), (3, 4), (3, 6), (4, 3),
            (4, 4)
        ], width=6),
        "s": _MatrixLetter([
            (0, 3), (0, 6), (1, 2), (1, 4), (1, 6), (2, 2), (2, 4), (2, 6), (3, 2), (3, 4), (3, 6), (4, 2), (4, 5)
        ], width=6),
        "t": _MatrixLetter([
            (0, 2), (1, 0), (1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (2, 2), (2, 6), (3, 6)
        ], width=5),
    }

    @staticmethod
    def shifted(letter: str, x: int, y: int) -> list[tuple[int, int]]:
        return [(x + x_, y + y_) for x_, y_ in MatrixLetters.letters[letter].leds]

    @staticmethod
    def chain(letters: list[str], x: int = 0, y: int = 0) -> tuple[list[tuple[int, int]], int]:
        led_letters = []

        for lt in letters:
            led = MatrixLetters.letters[lt]
            letter = [(x + x_, y + y_) for x_, y_ in led.leds]
            led_letters.extend(letter)

            x += led.width

        return led_letters, x - 1

    @staticmethod
    def border_new(size_x: int, size_y: int) -> list[tuple[int, int]]:
        corner = [(0, 4), (0, 5), (0, 6), (0, 7), (0, 8), (1, 2), (1, 3), (2, 1), (3, 1), (4, 0)]
        corner_1 = [
            (-(x + 1) % size_x, y) for x, y in corner
        ]
        corner_2 = [
            (-(x + 1) % size_x, -(y + 1) % size_y) for x, y in corner
        ]
        corner_3 = [
            (x, -(y + 1) % size_y) for x, y in corner
        ]
        corner_4 = [
            (x, y) for x, y in corner
        ]
        corners = corner_1 + corner_2 + corner_3 + corner_4
        sides_h = [
            (x, y) for x in range(4, size_x - 4) for y in [0, size_y - 1]
        ]
        sides_v = [(x, y) for y in range(4, size_y - 4) for x in [0, size_x - 1]]

        return corners + sides_h + sides_v

    """def square_brackets(self, size_x: int, size_y: int) -> list[tuple[int, int]]:
        sides = [(x, y) for y in range(0, size_y) for x in [0, size_x - 1]]
        top_row = 
        
        
        return sides"""

class WelcomeState(rx.State):
    show_register: bool = False
    show_login: bool = False
    show_reset_pw: bool = False

    def toggle_register(self):
        self.show_register = not self.show_register
        self.show_login = False
        self.show_reset_pw = False

        # if self.show_register:
        #     return rx.set_focus("register_label")

    def toggle_login(self):
        self.show_login = not self.show_login
        self.show_register = False
        self.show_reset_pw = False

        # if self.show_login:
        #     return rx.set_focus("login_label")

    def toggle_reset_pw(self):
        self.show_reset_pw = not self.show_reset_pw
        self.show_login = False
        self.show_register = False

    def disable_all(self):
        self.show_register = False
        self.show_login = False
        self.show_reset_pw = False


class CondState(rx.State, BackendRequests):
    unlock_event: bool = False

    def check_page(self):
        self.unlock_event = datetime.today()>=unlock_251001

    event_registration_enabled: bool = False

    async def check_event_registration_enabled(self):
        response = await self.get("/admin/event/registration_status")
        status = response.json()
        self.event_registration_enabled = status["enabled"]

class WelcomeAuthState(AuthCookie, BackendRequests):
    @rx.event(background=True)
    async def auto_redirect_on_auth(self):
        # kurzer Delay, optional – sorgt für ruhigeres Laden
        await asyncio.sleep(0.1)

        result = await self.get("/login/token_valid", auth=self.auth_cookie)
        if result.status_code == 200:
            chapter_selection_mode = os.getenv("SET_CHAPTER_SELECTION")
            target = (
                "/login_chapter_selection"
                if chapter_selection_mode == "True"
                else "/login_redirect"
            )
            return rx.redirect(target)
        # Wenn nicht eingeloggt: einfach nichts zurückgeben → Seite bleibt sichtbar.

class WelcomePage(AbstractSiteBuilder):
    def page(self) -> rx.Component:
        return rx.vstack(
            # self.render_droplets(),

            rx.hstack(
                rx.spacer(),
                rx.hstack(
#                    rx.link(
#                        rx.image(
#                            src="/images/codeweek_logo.png",
#                            alt="CodeWeek",
#                            class_name="title_image",
#                        ),
#                        href="https://bayern.codeweek.de/",
#                        is_external=True,
#                    ),
#                    rx.text(
#                        "x",
#                        class_name="title_middle",
#                    ),
                    rx.link(
                        rx.image(
                            src="/logo/tcv_logo.png",
                            alt="TCV",
                            class_name="title_image",
                        ),
                        href="https://th-deg.de/tc-vilshofen",
                        is_external=True,
                    ),
                    class_name="login_header"
                ),
                rx.spacer(),
                class_name="login_header_container",
            ),
            rx.spacer(),
            self.title(),
            rx.spacer(),
            self.login_box(),
            self.cards(),
            width="100vw",
            spacing="0",
        )


    @staticmethod
    def led_matrix(toggled_leds: list[tuple[int, int]], window: typing.Callable = None, _x: int = 50, _y: int = 7,
                   class_name: str = "led_matrix_stack") -> rx.Component:
        matrix = rx.vstack(
            *[
                rx.hstack(
                    *[
                        rx.box(
                            class_name=f"{'led_matrix_active' if (x, y) in toggled_leds else 'led_matrix'}",
                        ) for x in range(int((_x + 1) / 2) * 2)
                    ],
                    spacing="0",
                ) for y in range(_y)
            ],
            spacing="0",
            class_name=class_name
        )
        return rx.hstack(
            rx.spacer(),
            matrix,
            rx.spacer(),
            width="100%",
            on_click=window
        )

    @staticmethod
    def window_login() -> rx.Component:
        return rx.cond(
            WelcomeState.show_login,
            rx.box(
                rx.hstack(
                    rx.spacer(),
                    rx.icon("x", size=36, class_name="forward_button", on_click=WelcomeState.toggle_login),
                ),
                rx.container(heigth="1vh"),
                rx.cond(
                    CondState.event_registration_enabled,
                    rx.vstack(
                        rx.center(
                            rx.heading(
                                "Melden Sie sich hier an",
                                size="6",
                                as_="h2",
                                text_align="center",
                                width="100%",
                            ),
                            direction="column",
                            spacing="5",
                            width="100%",
                        ),
                        rx.vstack(
                            rx.text(
                                "Benutzername",
                                size="3",
                                weight="medium",
                                text_align="left",
                                width="100%",
                            ),
                            rx.form(
                                rx.input(
                                    rx.input.slot(rx.icon("user")),
                                    placeholder="Benutzername hier",
                                    type="email",
                                    size="3",
                                    width="100%",
                                    value=LoginState.username,
                                    on_change=[LoginState.set_username, LoginState.reset_login_auth],
                                    id="login_label",
                                    autocomplete="username",
                                    on_mount=rx.set_focus("login_label"),
                                ),
                                on_submit=rx.set_focus("login_password_input_field"),
                            ),
                            spacing="2",
                            width="100%",
                        ),
                        rx.vstack(
                            rx.hstack(
                                rx.text(
                                    "Passwort",
                                    size="3",
                                    weight="medium",
                                ),
                                rx.button(
                                    "Passwort vergessen?",
                                    variant="ghost",
                                    size="3",
                                    on_click=WelcomeState.toggle_reset_pw
                                ),
                                justify="between",
                                width="100%",
                            ),
                            rx.input(
                                rx.input.slot(rx.icon("lock")),
                                placeholder="Passwort hier",
                                type="password",
                                size="3",
                                width="100%",
                                id="login_password_input_field",
                                value=LoginState.password,
                                on_change=[LoginState.set_password, LoginState.reset_login_auth]
                            ),
                            spacing="2",
                            width="100%",
                        ),  # ToDo: focus input fields
                        rx.button(
                            "Anmelden",
                            size="3",
                            width="100%",
                            disabled=~LoginState.check_login_valid | LoginState.failed_auth | LoginState.is_logging_in,
                            on_click=LoginState.login,
                            loading=LoginState.is_logging_in,
                            style={"cursor": "pointer"},
                        ),
                        rx.box(
                            rx.cond(
                                LoginState.failed_auth,
                                rx.callout(
                                    "Falscher Benutzername oder Passwort! Ändern Sie Ihre Eingabe",
                                    icon="triangle_alert",
                                    color_scheme="red",
                                    role="alert",
                                    width="100%",
                                ),
                            ),
                            width="100%",
                        ),
                        spacing="6",
                        width="100%",
                    ),
                    rx.vstack(
                        rx.center(
                            rx.heading(
                                "Das Event wurde noch nicht freigeschaltet!",
                                size="6",
                                as_="h2",
                                text_align="center",
                                width="100%",
                            ),
                            direction="column",
                            spacing="5",
                            width="100%",
                        ),
                        rx.text("Ein bisschen müssen Sie sich noch gedulden. Warten Sie bis der Spielleiter das Event öffnet."),
                        spacing="4",
                        width="100%",
                    ),
                ),
                size="4",
                width="100%",
                class_name="login_card",
            )
        )

    @staticmethod
    def window_reset_pw() -> rx.Component:
        return rx.cond(
            WelcomeState.show_reset_pw,
            rx.box(
                rx.hstack(
                    rx.spacer(),
                    rx.icon("x", size=36, class_name="forward_button", on_click=WelcomeState.toggle_reset_pw),
                ),
                rx.container(heigth="1vh"),
                rx.vstack(
                    rx.center(
                        rx.heading(
                            "Passwort zurücksetzen",
                            size="6",
                            as_="h2",
                            text_align="center",
                            width="100%",
                        ),
                        direction="column",
                        spacing="5",
                        width="100%",
                    ),
                    rx.vstack(
                        rx.text(
                            "E-Mail-Adresse",
                            size="3",
                            weight="medium",
                            text_align="left",
                            width="100%",
                        ),
                        rx.input(
                            rx.input.slot(rx.icon("user")),
                            placeholder="deine@email.de",
                            type="email",
                            size="3",
                            width="100%",
                            value=LoginState.username,
                            on_change=LoginState.set_username,
                            on_click=LoginState.clear_failed_pw_reset,
                            id="register_label",
                        ),
                        justify="start",
                        spacing="2",
                        width="100%",
                    ),
                    rx.vstack(              
                        rx.box(
                            rx.checkbox(
                                rx.text("Ich bestätige, dass die eingegebene ",rx.text.strong("E-Mail Adresse")," mir gehört und das Passwort zurücksetzen möchte",as_="label"),
                                default_checked=LoginState.reset_pw_rules_accepted.to(bool),
                                spacing="2",
                                on_click=LoginState.toggle_reset_pw_rules,
                            ),
                            width="100%",
                        ),
                        justify="start",
                        spacing="2",
                        width="100%",
                    ),
                    
                    rx.match(
                        LoginState.failed_pw_reset,
                        (1, rx.callout(
                            "Sollte das Konto existieren, wurde dir eine E-Mail geschickt",
                            icon="check",
                            color_scheme="green",
                            width="100%",
                        )),
                        (3, rx.callout(
                            "Warte noch bis wir eine neue E-Mail schicken",
                            icon="info",
                            color_scheme="yellow",
                            width="100%",
                        )),
                        rx.button(
                            "Passwort zurücksetzen",
                            size="3",
                            width="100%",
                            on_click=LoginState.reset_pw,
                            disabled=~LoginState.check_reset_pw_valid,
                        ),
                    ),
                    spacing="6",
                    width="100%",
                ),
                size="4",
                width="100%",
                class_name="login_card",
            )
        )
        
    @staticmethod
    def window_register() -> rx.Component:
        return rx.cond(
            WelcomeState.show_register,
            rx.box(
                rx.hstack(
                    rx.spacer(),
                    rx.icon("x", size=36, class_name="forward_button", on_click=WelcomeState.toggle_register),
                ),
                rx.container(heigth="1vh"),
                rx.cond(
                    CondState.event_registration_enabled,
                rx.vstack(
                    rx.center(
                        rx.heading(
                            "Account erstellen",
                            size="6",
                            as_="h2",
                            text_align="center",
                            width="100%",
                        ),
                        direction="column",
                        spacing="5",
                        width="100%",
                    ),
                    rx.vstack(
                        rx.text(
                            "E-Mail-Adresse",
                            size="3",
                            weight="medium",
                            text_align="left",
                            width="100%",
                        ),
                        rx.input(
                            rx.input.slot(rx.icon("user")),
                            placeholder="deine@email.de",
                            type="email",
                            size="3",
                            width="100%",
                            value=LoginState.username,
                            on_change=LoginState.set_username,
                            on_click=LoginState.clear_failed,
                            id="register_label",
                        ),
                        justify="start",
                        spacing="2",
                        width="100%",
                    ),
                    rx.vstack(              
                        rx.box(
                            rx.checkbox(
                                rx.text("Ich habe die ",rx.text.strong("Spielregeln")," gelesen und zur Kenntnis genommen",as_="label"),
                                default_checked=LoginState.rules_accepted.to(bool),
                                spacing="2",
                                on_click=LoginState.toggle_rules,
                            ),
                            width="100%",
                        ),
                        rx.box(
                            rx.checkbox(
                                rx.text("Ich habe die ",rx.text.strong("Datenschutzinformation")," und die ",rx.text.strong("Einverständniserklärung")," gelesen und zur Kenntnis genommen",as_="label"),  
                                default_checked=LoginState.privacy_info_accepted.to(bool),
                                spacing="2",
                                on_click=LoginState.toggle_privacy_info,
                            ),
                            width="100%",
                        ),
                        rx.box(
                            rx.checkbox(
                                rx.text("Ich bin ",rx.text.strong("16 oder älter"),as_="label"),
                                default_checked=LoginState.age_confirmed.to(bool),
                                spacing="2",
                                on_click=LoginState.toggle_age,
                            ),
                            width="100%",
                        ),                       
                        rx.spacer(),
                        rx.hstack(
                            rx.link(rx.button("Spielregeln", variant="ghost", size="2"), href=f"https://{os.getenv('DOMAIN')}/spielregeln/",is_external=True),
                            rx.button("Datenschutzerklärung", variant="ghost", size="2", on_click=rx.download(url="/legal/Datenschutzinformation_CTF.pdf")),
                            rx.button("Einverständniserklärung", variant="ghost", size="2", on_click=rx.download(url="/legal/Einverständniserklärung_CTF.pdf")),
                            justify="between",
                            width="100%",
                        ), 
                        justify="start",
                        spacing="2",
                        width="100%",
                    ),
                    rx.match(
                        LoginState.failed_register,
                        (1, rx.callout(
                            "Wir haben Ihnen eine E-Mail geschickt",
                            icon="check",
                            color_scheme="green",
                            width="100%",
                        )),
                        (2, rx.callout(
                            "Irgendwas ist schief gelaufen!",
                            icon="triangle_alert",
                            color_scheme="red",
                            role="alert",
                            width="100%",
                        )),
                        (3, rx.callout(
                            "Warten Sie noch bis wir eine neue E-Mail schicken",
                            icon="info",
                            color_scheme="yellow",
                            width="100%",
                        )),
                        (4, rx.callout(
                            "Diese E-Mail wird bereits verwendet",
                            icon="info",
                            color_scheme="yellow",
                            width="100%",
                        )),
                        (5, rx.callout(
                            "Sie sind leider nicht für das Event vorangemeldet und können sich deshalb nicht registrieren!",
                            icon="info",
                            color_scheme="yellow",
                            width="100%",
                        )),
                        rx.button(
                            "Registrieren",
                            size="3",
                            width="100%",
                            on_click=LoginState.register,
                            disabled=~LoginState.check_register_valid,
                        ),
                    ),
                    spacing="6",
                    width="100%",
                ),
                    rx.vstack(
                        rx.center(
                            rx.heading(
                                "Das Event wurde noch nicht freigeschaltet!",
                                size="6",
                                as_="h2",
                                text_align="center",
                                width="100%",
                            ),
                            direction="column",
                            spacing="5",
                            width="100%",
                        ),
                        rx.text("Ein bisschen müssen Sie sich noch gedulden. Warten Sie bis der Spielleiter das Event öffnet."),
                        spacing="4",
                        width="100%",
                    ),
                ),
                size="4",
                width="100%",
                class_name="login_card",
            )
        )

    @staticmethod
    def title() -> rx.Component:
        return rx.hstack(    
            rx.spacer(),
            rx.vstack(
                rx.box(
                    rx.heading(
                        f"{os.getenv('HEADING')}",
                        class_name="game_title",
                    ),
                    class_name="game_title_wrap",
                ),
                rx.text(
                    f"{os.getenv('SUB_HEADING')}",
                    class_name="game_description",
                ),
                max_width="50rem",
            ),
            rx.spacer(),
            width="100%",
        )


    def cards(self) -> rx.Component:
        return rx.box(
            self.window_register(),
            self.window_login(),
            self.window_reset_pw(),
        )

    def login_box(self) -> rx.Component:
        # MatrixLetters.border_new(52, 13) +
        return rx.hstack(
            rx.spacer(),
            rx.vstack(
                self.led_matrix(
                    MatrixLetters.chain(["l", "o", "g", "i", "n"], x=3, y=0)[0],
                    window=WelcomeState.toggle_login,
                    _x=32,
                    _y=7,
                ),
                rx.box(height="24px"),
                self.led_matrix(
                    MatrixLetters.chain(["r", "e", "g", "i", "s", "t", "e", "r"], x=3, y=0)[0],
                    window=WelcomeState.toggle_register,
                    _x=48,
                    _y=7,
                ),
                rx.box(height="32px"),
                spacing="0",
                height="100%",
            ),
            rx.spacer(),
            width="100%",
        )

    def configure(self) -> None:
        self.page_title = "Welcome!"
        self.url = "/"
        self.background_class = "event_background_team"
        self.is_standalone = True
        self.hide_sidebar = True
        self.on_load = [WelcomeState.disable_all,CondState.check_event_registration_enabled,WelcomeAuthState.auto_redirect_on_auth,]
        
