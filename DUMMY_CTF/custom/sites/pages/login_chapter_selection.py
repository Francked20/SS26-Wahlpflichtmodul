import asyncio
from website.unlock_settings import *

import reflex as rx

from website.auth_lib import AuthCookie, BackendRequests
from website.engine.site import AbstractSiteBuilder
from website.sites.welcome import WelcomeState, LoginState
from website.engine.task_conf import PlayerCardState

class CondState(rx.State):
    chapter_01_unlocked: bool = False
    chapter_02_unlocked: bool = False
    chapter_03_unlocked: bool = False
    chapter_04_unlocked: bool = False
    chapter_05_unlocked: bool = False
    chapter_06_unlocked: bool = False
    chapter_07_unlocked: bool = False
    chapter_08_unlocked: bool = False
    chapter_09_unlocked: bool = False
    chapter_10_unlocked: bool = False
    chapter_11_unlocked: bool = False
    chapter_12_unlocked: bool = False
    chapter_13_unlocked: bool = False
    chapter_14_unlocked: bool = False
    chapter_15_unlocked: bool = False
    chapter_16_unlocked: bool = False
    chapter_17_unlocked: bool = False
    chapter_18_unlocked: bool = False
    chapter_19_unlocked: bool = False
    chapter_20_unlocked: bool = False
    chapter_21_unlocked: bool = False
    chapter_22_unlocked: bool = False
    chapter_23_unlocked: bool = False
    chapter_24_unlocked: bool = False
    chapter_25_unlocked: bool = False
    chapter_26_unlocked: bool = False
    chapter_27_unlocked: bool = False
    chapter_28_unlocked: bool = False
    chapter_29_unlocked: bool = False
    chapter_30_unlocked: bool = False
    chapter_31_unlocked: bool = False

    def check_page(self):
        self.chapter_01_unlocked = datetime.today()>=unlock_251001
        self.chapter_02_unlocked = datetime.today()>=unlock_251002
        self.chapter_03_unlocked = datetime.today()>=unlock_251003
        self.chapter_04_unlocked = datetime.today()>=unlock_251004
        self.chapter_05_unlocked = datetime.today()>=unlock_251005
        self.chapter_06_unlocked = datetime.today()>=unlock_251006
        self.chapter_07_unlocked = datetime.today()>=unlock_251007
        self.chapter_08_unlocked = datetime.today()>=unlock_251008
        self.chapter_09_unlocked = datetime.today()>=unlock_251009
        self.chapter_10_unlocked = datetime.today()>=unlock_251010
        self.chapter_11_unlocked = datetime.today()>=unlock_251011
        self.chapter_12_unlocked = datetime.today()>=unlock_251012
        self.chapter_13_unlocked = datetime.today()>=unlock_251013
        self.chapter_14_unlocked = datetime.today()>=unlock_251014
        self.chapter_15_unlocked = datetime.today()>=unlock_251015
        self.chapter_16_unlocked = datetime.today()>=unlock_251016
        self.chapter_17_unlocked = datetime.today()>=unlock_251017
        self.chapter_18_unlocked = datetime.today()>=unlock_251018
        self.chapter_19_unlocked = datetime.today()>=unlock_251019
        self.chapter_20_unlocked = datetime.today()>=unlock_251020
        self.chapter_21_unlocked = datetime.today()>=unlock_251021
        self.chapter_22_unlocked = datetime.today()>=unlock_251022
        self.chapter_23_unlocked = datetime.today()>=unlock_251023
        self.chapter_24_unlocked = datetime.today()>=unlock_251024
        self.chapter_25_unlocked = datetime.today()>=unlock_251025
        self.chapter_26_unlocked = datetime.today()>=unlock_251026
        self.chapter_27_unlocked = datetime.today()>=unlock_251027
        self.chapter_28_unlocked = datetime.today()>=unlock_251028
        self.chapter_29_unlocked = datetime.today()>=unlock_251029
        self.chapter_30_unlocked = datetime.today()>=unlock_251030
        self.chapter_31_unlocked = datetime.today()>=unlock_251031


class ChapterSelectionState(AuthCookie, BackendRequests):
    @staticmethod
    def get_day_url() -> str:
        # format to current day's task
        day: int = datetime.now().day
        month: int = datetime.now().month
        year: int = datetime.now().year
        
        if all([year == 2024, month == 10]):
            return f"/challenge_{day:02d}"
        else:
            return f"/challenge_01"

    @rx.event(background=True)
    async def check_auth(self):
        # sleep first → feels like actual loading to the user
        await asyncio.sleep(0.25)

        for x in range(5):
            result = await self.get("/login/token_valid", auth=self.auth_cookie)

            if result.status_code != 200:
                await asyncio.sleep(1)
                continue

            return [
                PlayerCardState.update_on_first_load(),
                WelcomeState.disable_all(),
                LoginState.reset_auth(),
                CondState.check_page(),
#                rx.redirect(self.get_day_url())
            ]

        return rx.redirect("/error/401")


class ChapterSelectionPage(AbstractSiteBuilder):
    def page(self) -> rx.Component:
        return rx.vstack(
            rx.spacer(),
            rx.flex(
                rx.spacer(),
                rx.flex(
        
                    rx.heading("Kapitelauswahl: ⌚ Wohin willst du springen?", color=self.main_color, size="8"),
                    
                    rx.cond(
                        CondState.chapter_01_unlocked,
                        rx.card(
                            rx.inset(
                                rx.image(
                                    src="/custom/images/login_background.jpg",
                                    width="100%",
                                    height="150px",
        #                            object_fit="cover",  # Stellt sicher, dass das Bild die gesamte Fläche ausfüllt
                                    on_click=rx.redirect("/challenge_01"),
                                ),
                                side="top",
                                pb="current",
                            ),
                            rx.text(
                                "Kapitel 01"
                            ),
                            width="15vw",
                        ),
                        rx.card(
                            rx.inset(
                                rx.image(
                                    src="/images/background_gesperrt.jpg",
                                    width="100%",
                                    height="150px",
        #                            object_fit="cover",  # Stellt sicher, dass das Bild die gesamte Fläche ausfüllt
                                ),
                                side="top",
                                pb="current",
                            ),
                            rx.text(
                                "Kapitel gesperrt"
                            ),
                            width="15vw",
                        ),
                    ),
                    rx.hstack(
                        rx.cond(
                            CondState.chapter_02_unlocked,
                            rx.card(
                                rx.inset(
                                    rx.image(
                                        src="/images/background_02.jpg",
                                        width="100%",
                                        height="150px",
            #                            object_fit="cover",  # Stellt sicher, dass das Bild die gesamte Fläche ausfüllt
                                        on_click=rx.redirect("/challenge_02_kurs"),
                                    ),
                                    side="top",
                                    pb="current",
                                ), 
                                rx.text(
                                    "Kapitel 02"
                                ),
                                width="15vw",                    
                            ),
                            rx.card(
                                rx.inset(
                                    rx.image(
                                        src="/images/background_gesperrt.jpg",
                                        width="100%",
                                        height="150px",
            #                            object_fit="cover",  # Stellt sicher, dass das Bild die gesamte Fläche ausfüllt
                                    ),
                                    side="top",
                                    pb="current",
                                ),
                                rx.text(
                                    "Kapitel gesperrt"
                                ),
                                width="15vw",
                            ),
                        ),
                        rx.cond(
                            CondState.chapter_03_unlocked,
                            rx.card(
                                rx.inset(
                                    rx.image(
                                        src="/images/background_03.jpg",
                                        width="100%",
                                        height="150px",
            #                            object_fit="cover",  # Stellt sicher, dass das Bild die gesamte Fläche ausfüllt
                                        on_click=rx.redirect("/challenge_03"),
                                    ),
                                    side="top",
                                    pb="current",
                                ),
                                rx.text(
                                    "Kapitel 03"
                                ),
                                width="15vw",
                            ),
                            rx.card(
                                rx.inset(
                                    rx.image(
                                        src="/images/background_gesperrt.jpg",
                                        width="100%",
                                        height="150px",
            #                            object_fit="cover",  # Stellt sicher, dass das Bild die gesamte Fläche ausfüllt
                                    ),
                                    side="top",
                                    pb="current",
                                ),
                                rx.text(
                                    "Kapitel gesperrt"
                                ),
                                width="15vw",
                            ),
                        ),
                        rx.cond(
                            CondState.chapter_04_unlocked,
                            rx.card(
                                rx.inset(
                                    rx.image(
                                        src="/images/background_04.jpg",
                                        width="100%",
                                        height="150px",
            #                            object_fit="cover",  # Stellt sicher, dass das Bild die gesamte Fläche ausfüllt
                                        on_click=rx.redirect("/challenge_04"),
                                    ),
                                    side="top",
                                    pb="current",
                                ),
                                rx.text(
                                    "Kapitel 04"
                                ),
                                width="15vw",
                            ),
                            rx.card(
                                rx.inset(
                                    rx.image(
                                        src="/images/background_gesperrt.jpg",
                                        width="100%",
                                        height="150px",
            #                            object_fit="cover",  # Stellt sicher, dass das Bild die gesamte Fläche ausfüllt
                                    ),
                                    side="top",
                                    pb="current",
                                ),
                                rx.text(
                                    "Kapitel gesperrt"
                                ),
                                width="15vw",
                            ),
                        ),
                        rx.cond(
                            CondState.chapter_05_unlocked,
                            rx.card(
                                rx.inset(
                                    rx.image(
                                        src="/images/background_05.jpg",
                                        width="100%",
                                        height="150px",
            #                            object_fit="cover",  # Stellt sicher, dass das Bild die gesamte Fläche ausfüllt
                                        on_click=rx.redirect("/challenge_05"),
                                    ),
                                    side="top",
                                    pb="current",
                                ),
                                rx.text(
                                    "Kapitel 05"
                                ),
                                width="15vw",
                            ),
                            rx.card(
                                rx.inset(
                                    rx.image(
                                        src="/images/background_gesperrt.jpg",
                                        width="100%",
                                        height="150px",
            #                            object_fit="cover",  # Stellt sicher, dass das Bild die gesamte Fläche ausfüllt
                                    ),
                                    side="top",
                                    pb="current",
                                ),
                                rx.text(
                                    "Kapitel gesperrt"
                                ),
                                width="15vw",
                            ),
                        ),
                        rx.cond(
                            CondState.chapter_06_unlocked,
                            rx.card(
                                rx.inset(
                                    rx.image(
                                        src="/images/background_06.jpg",
                                        width="100%",
                                        height="150px",
            #                            object_fit="cover",  # Stellt sicher, dass das Bild die gesamte Fläche ausfüllt
                                        on_click=rx.redirect("/challenge_06"),
                                    ),
                                    side="top",
                                    pb="current",
                                ),
                                rx.text(
                                    "Kapitel 06"
                                ),
                                width="15vw",
                            ),
                            rx.card(
                                rx.inset(
                                    rx.image(
                                        src="/images/background_gesperrt.jpg",
                                        width="100%",
                                        height="150px",
            #                            object_fit="cover",  # Stellt sicher, dass das Bild die gesamte Fläche ausfüllt
                                    ),
                                    side="top",
                                    pb="current",
                                ),
                                rx.text(
                                    "Kapitel gesperrt"
                                ),
                                width="15vw",
                            ),
                        ),
                    ),
                    rx.hstack(
                        rx.cond(
                            CondState.chapter_07_unlocked,
                            rx.card(
                                rx.inset(
                                    rx.image(
                                        src="/images/background_07.jpg",
                                        width="100%",
                                        height="150px",
            #                            object_fit="cover",  # Stellt sicher, dass das Bild die gesamte Fläche ausfüllt
                                        on_click=rx.redirect("/challenge_07"),
                                    ),
                                    side="top",
                                    pb="current",
                                ),
                                rx.text(
                                    "Kapitel 07"
                                ),
                                width="15vw",
                            ),
                            rx.card(
                                rx.inset(
                                    rx.image(
                                        src="/images/background_gesperrt.jpg",
                                        width="100%",
                                        height="150px",
            #                            object_fit="cover",  # Stellt sicher, dass das Bild die gesamte Fläche ausfüllt
                                    ),
                                    side="top",
                                    pb="current",
                                ),
                                rx.text(
                                    "Kapitel gesperrt"
                                ),
                                width="15vw",
                            ),
                        ),
                        rx.cond(
                            CondState.chapter_08_unlocked,
                            rx.card(
                                rx.inset(
                                    rx.image(
                                        src="/images/background_08.jpg",
                                        width="100%",
                                        height="150px",
            #                            object_fit="cover",  # Stellt sicher, dass das Bild die gesamte Fläche ausfüllt
                                        on_click=rx.redirect("/challenge_08"),
                                    ),
                                    side="top",
                                    pb="current",
                                ),
                                rx.text(
                                    "Kapitel 08"
                                ),
                                width="15vw",
                            ),
                            rx.card(
                                rx.inset(
                                    rx.image(
                                        src="/images/background_gesperrt.jpg",
                                        width="100%",
                                        height="150px",
            #                            object_fit="cover",  # Stellt sicher, dass das Bild die gesamte Fläche ausfüllt
                                    ),
                                    side="top",
                                    pb="current",
                                ),
                                rx.text(
                                    "Kapitel gesperrt"
                                ),
                                width="15vw",
                            ),
                        ),
                        rx.cond(
                            CondState.chapter_09_unlocked,
                            rx.card(
                                rx.inset(
                                    rx.image(
                                        src="/images/background_09.jpg",
                                        width="100%",
                                        height="150px",
            #                            object_fit="cover",  # Stellt sicher, dass das Bild die gesamte Fläche ausfüllt
                                        on_click=rx.redirect("/challenge_09"),
                                    ),
                                    side="top",
                                    pb="current",
                                ),
                                rx.text(
                                    "Kapitel 09"
                                ),
                                width="15vw",
                            ),
                            rx.card(
                                rx.inset(
                                    rx.image(
                                        src="/images/background_gesperrt.jpg",
                                        width="100%",
                                        height="150px",
            #                            object_fit="cover",  # Stellt sicher, dass das Bild die gesamte Fläche ausfüllt
                                    ),
                                    side="top",
                                    pb="current",
                                ),
                                rx.text(
                                    "Kapitel gesperrt"
                                ),
                                width="15vw",
                            ),
                        ),
                        rx.cond(
                            CondState.chapter_10_unlocked,
                            rx.card(
                                rx.inset(
                                    rx.image(
                                        src="/images/background_10.jpg",
                                        width="100%",
                                        height="150px",
            #                            object_fit="cover",  # Stellt sicher, dass das Bild die gesamte Fläche ausfüllt
                                        on_click=rx.redirect("/challenge_10"),
                                    ),
                                    side="top",
                                    pb="current",
                                ),
                                rx.text(
                                    "Kapitel 10"
                                ),
                                width="15vw",
                            ),
                            rx.card(
                                rx.inset(
                                    rx.image(
                                        src="/images/background_gesperrt.jpg",
                                        width="100%",
                                        height="150px",
            #                            object_fit="cover",  # Stellt sicher, dass das Bild die gesamte Fläche ausfüllt
                                    ),
                                    side="top",
                                    pb="current",
                                ),
                                rx.text(
                                    "Kapitel gesperrt"
                                ),
                                width="15vw",
                            ),
                        ),
                        rx.cond(
                            CondState.chapter_11_unlocked,
                            rx.card(
                                rx.inset(
                                    rx.image(
                                        src="/images/background_11.jpg",
                                        width="100%",
                                        height="150px",
            #                            object_fit="cover",  # Stellt sicher, dass das Bild die gesamte Fläche ausfüllt
                                        on_click=rx.redirect("/challenge_11"),
                                    ),
                                    side="top",
                                    pb="current",
                                ),
                                rx.text(
                                    "Kapitel 11"
                                ),
                                width="15vw",
                            ),
                            rx.card(
                                rx.inset(
                                    rx.image(
                                        src="/images/background_gesperrt.jpg",
                                        width="100%",
                                        height="150px",
            #                            object_fit="cover",  # Stellt sicher, dass das Bild die gesamte Fläche ausfüllt
                                    ),
                                    side="top",
                                    pb="current",
                                ),
                                rx.text(
                                    "Kapitel gesperrt"
                                ),
                                width="15vw",
                            ),
                        ),
                    ),
                    rx.hstack(
                        rx.cond(
                            CondState.chapter_12_unlocked,
                            rx.card(
                                rx.inset(
                                    rx.image(
                                        src="/images/background_12.jpg",
                                        width="100%",
                                        height="150px",
            #                            object_fit="cover",  # Stellt sicher, dass das Bild die gesamte Fläche ausfüllt
                                        on_click=rx.redirect("/challenge_12"),
                                    ),
                                    side="top",
                                    pb="current",
                                ), 
                                rx.text(
                                    "Kapitel 12"
                                ),
                                width="15vw",                    
                            ),
                            rx.card(
                                rx.inset(
                                    rx.image(
                                        src="/images/background_gesperrt.jpg",
                                        width="100%",
                                        height="150px",
            #                            object_fit="cover",  # Stellt sicher, dass das Bild die gesamte Fläche ausfüllt
                                    ),
                                    side="top",
                                    pb="current",
                                ),
                                rx.text(
                                    "Kapitel gesperrt"
                                ),
                                width="15vw",
                            ),
                        ),
                        rx.cond(
                            CondState.chapter_13_unlocked,
                            rx.card(
                                rx.inset(
                                    rx.image(
                                        src="/images/background_13.jpg",
                                        width="100%",
                                        height="150px",
            #                            object_fit="cover",  # Stellt sicher, dass das Bild die gesamte Fläche ausfüllt
                                        on_click=rx.redirect("/challenge_13"),
                                    ),
                                    side="top",
                                    pb="current",
                                ),
                                rx.text(
                                    "Kapitel 13"
                                ),
                                width="15vw",
                            ),
                            rx.card(
                                rx.inset(
                                    rx.image(
                                        src="/images/background_gesperrt.jpg",
                                        width="100%",
                                        height="150px",
            #                            object_fit="cover",  # Stellt sicher, dass das Bild die gesamte Fläche ausfüllt
                                    ),
                                    side="top",
                                    pb="current",
                                ),
                                rx.text(
                                    "Kapitel gesperrt"
                                ),
                                width="15vw",
                            ),
                        ),
                        rx.cond(
                            CondState.chapter_14_unlocked,
                            rx.card(
                                rx.inset(
                                    rx.image(
                                        src="/images/background_14.jpg",
                                        width="100%",
                                        height="150px",
            #                            object_fit="cover",  # Stellt sicher, dass das Bild die gesamte Fläche ausfüllt
                                        on_click=rx.redirect("/challenge_14"),
                                    ),
                                    side="top",
                                    pb="current",
                                ),
                                rx.text(
                                    "Kapitel 14"
                                ),
                                width="15vw",
                            ),
                            rx.card(
                                rx.inset(
                                    rx.image(
                                        src="/images/background_gesperrt.jpg",
                                        width="100%",
                                        height="150px",
            #                            object_fit="cover",  # Stellt sicher, dass das Bild die gesamte Fläche ausfüllt
                                    ),
                                    side="top",
                                    pb="current",
                                ),
                                rx.text(
                                    "Kapitel gesperrt"
                                ),
                                width="15vw",
                            ),
                        ),
                        rx.cond(
                            CondState.chapter_15_unlocked,
                            rx.card(
                                rx.inset(
                                    rx.image(
                                        src="/images/background_15.jpg",
                                        width="100%",
                                        height="150px",
            #                            object_fit="cover",  # Stellt sicher, dass das Bild die gesamte Fläche ausfüllt
                                        on_click=rx.redirect("/challenge_15"),
                                    ),
                                    side="top",
                                    pb="current",
                                ),
                                rx.text(
                                    "Kapitel 15"
                                ),
                                width="15vw",
                            ),
                            rx.card(
                                rx.inset(
                                    rx.image(
                                        src="/images/background_gesperrt.jpg",
                                        width="100%",
                                        height="150px",
            #                            object_fit="cover",  # Stellt sicher, dass das Bild die gesamte Fläche ausfüllt
                                    ),
                                    side="top",
                                    pb="current",
                                ),
                                rx.text(
                                    "Kapitel gesperrt"
                                ),
                                width="15vw",
                            ),
                        ),
                        rx.cond(
                            CondState.chapter_16_unlocked,
                            rx.card(
                                rx.inset(
                                    rx.image(
                                        src="/images/background_16.jpg",
                                        width="100%",
                                        height="150px",
            #                            object_fit="cover",  # Stellt sicher, dass das Bild die gesamte Fläche ausfüllt
                                        on_click=rx.redirect("/challenge_16"),
                                    ),
                                    side="top",
                                    pb="current",
                                ),
                                rx.text(
                                    "Kapitel 16"
                                ),
                                width="15vw",
                            ),
                            rx.card(
                                rx.inset(
                                    rx.image(
                                        src="/images/background_gesperrt.jpg",
                                        width="100%",
                                        height="150px",
            #                            object_fit="cover",  # Stellt sicher, dass das Bild die gesamte Fläche ausfüllt
                                    ),
                                    side="top",
                                    pb="current",
                                ),
                                rx.text(
                                    "Kapitel gesperrt"
                                ),
                                width="15vw",
                            ),
                        ),   
                    ), 
                    rx.hstack(
                        rx.cond(
                            CondState.chapter_17_unlocked,
                            rx.card(
                                rx.inset(
                                    rx.image(
                                        src="/images/background_17.jpg",
                                        width="100%",
                                        height="150px",
            #                            object_fit="cover",  # Stellt sicher, dass das Bild die gesamte Fläche ausfüllt
                                        on_click=rx.redirect("/challenge_17"),
                                    ),
                                    side="top",
                                    pb="current",
                                ),
                                rx.text(
                                    "Kapitel 17"
                                ),
                                width="15vw",
                            ),
                            rx.card(
                                rx.inset(
                                    rx.image(
                                        src="/images/background_gesperrt.jpg",
                                        width="100%",
                                        height="150px",
            #                            object_fit="cover",  # Stellt sicher, dass das Bild die gesamte Fläche ausfüllt
                                    ),
                                    side="top",
                                    pb="current",
                                ),
                                rx.text(
                                    "Kapitel gesperrt"
                                ),
                                width="15vw",
                            ),
                        ),
                        rx.cond(
                            CondState.chapter_18_unlocked,
                            rx.card(
                                rx.inset(
                                    rx.image(
                                        src="/images/background_18.jpg",
                                        width="100%",
                                        height="150px",
            #                            object_fit="cover",  # Stellt sicher, dass das Bild die gesamte Fläche ausfüllt
                                        on_click=rx.redirect("/challenge_18"),
                                    ),
                                    side="top",
                                    pb="current",
                                ),
                                rx.text(
                                    "Kapitel 18"
                                ),
                                width="15vw",
                            ),
                            rx.card(
                                rx.inset(
                                    rx.image(
                                        src="/images/background_gesperrt.jpg",
                                        width="100%",
                                        height="150px",
            #                            object_fit="cover",  # Stellt sicher, dass das Bild die gesamte Fläche ausfüllt
                                    ),
                                    side="top",
                                    pb="current",
                                ),
                                rx.text(
                                    "Kapitel gesperrt"
                                ),
                                width="15vw",
                            ),
                        ),
                        rx.cond(
                            CondState.chapter_19_unlocked,
                            rx.card(
                                rx.inset(
                                    rx.image(
                                        src="/images/background_19.jpg",
                                        width="100%",
                                        height="150px",
            #                            object_fit="cover",  # Stellt sicher, dass das Bild die gesamte Fläche ausfüllt
                                        on_click=rx.redirect("/challenge_19"),
                                    ),
                                    side="top",
                                    pb="current",
                                ),
                                rx.text(
                                    "Kapitel 19"
                                ),
                                width="15vw",
                            ),
                            rx.card(
                                rx.inset(
                                    rx.image(
                                        src="/images/background_gesperrt.jpg",
                                        width="100%",
                                        height="150px",
            #                            object_fit="cover",  # Stellt sicher, dass das Bild die gesamte Fläche ausfüllt
                                    ),
                                    side="top",
                                    pb="current",
                                ),
                                rx.text(
                                    "Kapitel gesperrt"
                                ),
                                width="15vw",
                            ),
                        ),
                        rx.cond(
                            CondState.chapter_20_unlocked,
                            rx.card(
                                rx.inset(
                                    rx.image(
                                        src="/images/background_20.jpg",
                                        width="100%",
                                        height="150px",
            #                            object_fit="cover",  # Stellt sicher, dass das Bild die gesamte Fläche ausfüllt
                                        on_click=rx.redirect("/challenge_20"),
                                    ),
                                    side="top",
                                    pb="current",
                                ),
                                rx.text(
                                    "Kapitel 20"
                                ),
                                width="15vw",
                            ),
                            rx.card(
                                rx.inset(
                                    rx.image(
                                        src="/images/background_gesperrt.jpg",
                                        width="100%",
                                        height="150px",
            #                            object_fit="cover",  # Stellt sicher, dass das Bild die gesamte Fläche ausfüllt
                                    ),
                                    side="top",
                                    pb="current",
                                ),
                                rx.text(
                                    "Kapitel gesperrt"
                                ),
                                width="15vw",
                            ),
                        ),
                        rx.cond(
                            CondState.chapter_21_unlocked,
                            rx.card(
                                rx.inset(
                                    rx.image(
                                        src="/images/background_21.jpg",
                                        width="100%",
                                        height="150px",
            #                            object_fit="cover",  # Stellt sicher, dass das Bild die gesamte Fläche ausfüllt
                                        on_click=rx.redirect("/challenge_21"),
                                    ),
                                    side="top",
                                    pb="current",
                                ),
                                rx.text(
                                    "Kapitel 21"
                                ),
                                width="15vw",
                            ),
                            rx.card(
                                rx.inset(
                                    rx.image(
                                        src="/images/background_gesperrt.jpg",
                                        width="100%",
                                        height="150px",
            #                            object_fit="cover",  # Stellt sicher, dass das Bild die gesamte Fläche ausfüllt
                                    ),
                                    side="top",
                                    pb="current",
                                ),
                                rx.text(
                                    "Kapitel gesperrt"
                                ),
                                width="15vw",
                            ),
                        ),  
                    ),
                    rx.hstack(
                        rx.cond(
                            CondState.chapter_22_unlocked,
                            rx.card(
                                rx.inset(
                                    rx.image(
                                        src="/images/background_22.jpg",
                                        width="100%",
                                        height="150px",
            #                            object_fit="cover",  # Stellt sicher, dass das Bild die gesamte Fläche ausfüllt
                                        on_click=rx.redirect("/challenge_22"),
                                    ),
                                    side="top",
                                    pb="current",
                                ), 
                                rx.text(
                                    "Kapitel 22"
                                ),
                                width="15vw",                    
                            ),
                            rx.card(
                                rx.inset(
                                    rx.image(
                                        src="/images/background_gesperrt.jpg",
                                        width="100%",
                                        height="150px",
            #                            object_fit="cover",  # Stellt sicher, dass das Bild die gesamte Fläche ausfüllt
                                    ),
                                    side="top",
                                    pb="current",
                                ),
                                rx.text(
                                    "Kapitel gesperrt"
                                ),
                                width="15vw",
                            ),
                        ),
                        rx.cond(
                            CondState.chapter_23_unlocked,
                            rx.card(
                                rx.inset(
                                    rx.image(
                                        src="/images/background_23.jpg",
                                        width="100%",
                                        height="150px",
            #                            object_fit="cover",  # Stellt sicher, dass das Bild die gesamte Fläche ausfüllt
                                        on_click=rx.redirect("/challenge_23"),
                                    ),
                                    side="top",
                                    pb="current",
                                ),
                                rx.text(
                                    "Kapitel 23"
                                ),
                                width="15vw",
                            ),
                            rx.card(
                                rx.inset(
                                    rx.image(
                                        src="/images/background_gesperrt.jpg",
                                        width="100%",
                                        height="150px",
            #                            object_fit="cover",  # Stellt sicher, dass das Bild die gesamte Fläche ausfüllt
                                    ),
                                    side="top",
                                    pb="current",
                                ),
                                rx.text(
                                    "Kapitel gesperrt"
                                ),
                                width="15vw",
                            ),
                        ),
                        rx.cond(
                            CondState.chapter_24_unlocked,
                            rx.card(
                                rx.inset(
                                    rx.image(
                                        src="/images/background_24.jpg",
                                        width="100%",
                                        height="150px",
            #                            object_fit="cover",  # Stellt sicher, dass das Bild die gesamte Fläche ausfüllt
                                        on_click=rx.redirect("/challenge_24"),
                                    ),
                                    side="top",
                                    pb="current",
                                ),
                                rx.text(
                                    "Kapitel 24"
                                ),
                                width="15vw",
                            ),
                            rx.card(
                                rx.inset(
                                    rx.image(
                                        src="/images/background_gesperrt.jpg",
                                        width="100%",
                                        height="150px",
            #                            object_fit="cover",  # Stellt sicher, dass das Bild die gesamte Fläche ausfüllt
                                    ),
                                    side="top",
                                    pb="current",
                                ),
                                rx.text(
                                    "Kapitel gesperrt"
                                ),
                                width="15vw",
                            ),
                        ),
                        rx.cond(
                            CondState.chapter_25_unlocked,
                            rx.card(
                                rx.inset(
                                    rx.image(
                                        src="/images/background_25.jpg",
                                        width="100%",
                                        height="150px",
            #                            object_fit="cover",  # Stellt sicher, dass das Bild die gesamte Fläche ausfüllt
                                        on_click=rx.redirect("/challenge_25"),
                                    ),
                                    side="top",
                                    pb="current",
                                ),
                                rx.text(
                                    "Kapitel 25"
                                ),
                                width="15vw",
                            ),
                            rx.card(
                                rx.inset(
                                    rx.image(
                                        src="/images/background_gesperrt.jpg",
                                        width="100%",
                                        height="150px",
            #                            object_fit="cover",  # Stellt sicher, dass das Bild die gesamte Fläche ausfüllt
                                    ),
                                    side="top",
                                    pb="current",
                                ),
                                rx.text(
                                    "Kapitel gesperrt"
                                ),
                                width="15vw",
                            ),
                        ),
                        rx.cond(
                            CondState.chapter_26_unlocked,
                            rx.card(
                                rx.inset(
                                    rx.image(
                                        src="/images/background_26.jpg",
                                        width="100%",
                                        height="150px",
            #                            object_fit="cover",  # Stellt sicher, dass das Bild die gesamte Fläche ausfüllt
                                        on_click=rx.redirect("/challenge_26"),
                                    ),
                                    side="top",
                                    pb="current",
                                ),
                                rx.text(
                                    "Kapitel 26"
                                ),
                                width="15vw",
                            ),
                            rx.card(
                                rx.inset(
                                    rx.image(
                                        src="/images/background_gesperrt.jpg",
                                        width="100%",
                                        height="150px",
            #                            object_fit="cover",  # Stellt sicher, dass das Bild die gesamte Fläche ausfüllt
                                    ),
                                    side="top",
                                    pb="current",
                                ),
                                rx.text(
                                    "Kapitel gesperrt"
                                ),
                                width="15vw",
                            ),
                        ),      
                    ),
                    rx.hstack(
                        rx.cond(
                            CondState.chapter_27_unlocked,
                            rx.card(
                                rx.inset(
                                    rx.image(
                                        src="/images/background_27.jpg",
                                        width="100%",
                                        height="150px",
            #                            object_fit="cover",  # Stellt sicher, dass das Bild die gesamte Fläche ausfüllt
                                        on_click=rx.redirect("/challenge_27"),
                                    ),
                                    side="top",
                                    pb="current",
                                ),
                                rx.text(
                                    "Kapitel 27"
                                ),
                                width="15vw",
                            ),
                            rx.card(
                                rx.inset(
                                    rx.image(
                                        src="/images/background_gesperrt.jpg",
                                        width="100%",
                                        height="150px",
            #                            object_fit="cover",  # Stellt sicher, dass das Bild die gesamte Fläche ausfüllt
                                    ),
                                    side="top",
                                    pb="current",
                                ),
                                rx.text(
                                    "Kapitel gesperrt"
                                ),
                                width="15vw",
                            ),
                        ),
                        rx.cond(
                            CondState.chapter_28_unlocked,
                            rx.card(
                                rx.inset(
                                    rx.image(
                                        src="/images/background_28.jpg",
                                        width="100%",
                                        height="150px",
            #                            object_fit="cover",  # Stellt sicher, dass das Bild die gesamte Fläche ausfüllt
                                        on_click=rx.redirect("/challenge_28"),
                                    ),
                                    side="top",
                                    pb="current",
                                ),
                                rx.text(
                                    "Kapitel 28"
                                ),
                                width="15vw",
                            ),
                            rx.card(
                                rx.inset(
                                    rx.image(
                                        src="/images/background_gesperrt.jpg",
                                        width="100%",
                                        height="150px",
            #                            object_fit="cover",  # Stellt sicher, dass das Bild die gesamte Fläche ausfüllt
                                    ),
                                    side="top",
                                    pb="current",
                                ),
                                rx.text(
                                    "Kapitel gesperrt"
                                ),
                                width="15vw",
                            ),
                        ),
                        rx.cond(
                            CondState.chapter_29_unlocked,
                            rx.card(
                                rx.inset(
                                    rx.image(
                                        src="/images/background_29.jpg",
                                        width="100%",
                                        height="150px",
            #                            object_fit="cover",  # Stellt sicher, dass das Bild die gesamte Fläche ausfüllt
                                        on_click=rx.redirect("/challenge_29"),
                                    ),
                                    side="top",
                                    pb="current",
                                ),
                                rx.text(
                                    "Kapitel 29"
                                ),
                                width="15vw",
                            ),
                            rx.card(
                                rx.inset(
                                    rx.image(
                                        src="/images/background_gesperrt.jpg",
                                        width="100%",
                                        height="150px",
            #                            object_fit="cover",  # Stellt sicher, dass das Bild die gesamte Fläche ausfüllt
                                    ),
                                    side="top",
                                    pb="current",
                                ),
                                rx.text(
                                    "Kapitel gesperrt"
                                ),
                                width="15vw",
                            ),
                        ),
                        rx.cond(
                            CondState.chapter_30_unlocked,
                            rx.card(
                                rx.inset(
                                    rx.image(
                                        src="/images/background_30.jpg",
                                        width="100%",
                                        height="150px",
            #                            object_fit="cover",  # Stellt sicher, dass das Bild die gesamte Fläche ausfüllt
                                        on_click=rx.redirect("/challenge_30"),
                                    ),
                                    side="top",
                                    pb="current",
                                ),
                                rx.text(
                                    "Kapitel 30"
                                ),
                                width="15vw",
                            ),
                            rx.card(
                                rx.inset(
                                    rx.image(
                                        src="/images/background_gesperrt.jpg",
                                        width="100%",
                                        height="150px",
            #                            object_fit="cover",  # Stellt sicher, dass das Bild die gesamte Fläche ausfüllt
                                    ),
                                    side="top",
                                    pb="current",
                                ),
                                rx.text(
                                    "Kapitel gesperrt"
                                ),
                                width="15vw",
                            ),
                        ),
                        rx.cond(
                            CondState.chapter_31_unlocked,
                            rx.card(
                                rx.inset(
                                    rx.image(
                                        src="/images/background_31.jpg",
                                        width="100%",
                                        height="150px",
            #                            object_fit="cover",  # Stellt sicher, dass das Bild die gesamte Fläche ausfüllt
                                        on_click=rx.redirect("/challenge_31"),
                                    ),
                                    side="top",
                                    pb="current",
                                ),
                                rx.text(
                                    "Kapitel 31"
                                ),
                                width="15vw",
                            ),
                            rx.card(
                                rx.inset(
                                    rx.image(
                                        src="/images/background_gesperrt.jpg",
                                        width="100%",
                                        height="150px",
            #                            object_fit="cover",  # Stellt sicher, dass das Bild die gesamte Fläche ausfüllt
                                    ),
                                    side="top",
                                    pb="current",
                                ),
                                rx.text(
                                    "Kapitel gesperrt"
                                ),
                                width="15vw",
                            ),
                        ),    
                    ),
                    
                spacing="3",
                align_items="center",
                direction="column",
                ),
                rx.spacer(),
                direction="row",
                width="100%",
            ),
            rx.spacer(),
            height="100vh",
            width="100vw",
        ),

    def configure(self) -> None:
        self.page_title = "Kapitelauswahl"
        self.url = "/login_chapter_selection"
        # self.background_class = "event_background_team"
        self.is_standalone = True
        self.hide_sidebar = True
        self.on_load = [ChapterSelectionState.check_auth]
        self.background_class = "black"
