import asyncio

import reflex as rx

from website.auth_lib import AuthCookie, BackendRequests
from website.engine.site import AbstractSiteBuilder
from website.sites.welcome import WelcomeState, LoginState
from website.engine.task_conf import PlayerCardState

class LimboPageState(AuthCookie, BackendRequests):
    @staticmethod
    def get_day_url() -> str:
        return f"/challenge_01"
#        return f"/login_chapter_selection"

#        # format to current day's task
#        day: int = datetime.datetime.now().day
#        month: int = datetime.datetime.now().month
#        year: int = datetime.datetime.now().year
#        
#        if all([year == 2024, month == 10]):
#            return f"/challenge_{day:02d}"
#        else:
#            return f"/challenge_01"

    @rx.event(background=True)
    async def check_auth(self):
        # sleep first → feels like actual loading to the user
        # ToDo:
        # await asyncio.sleep(0.25)

        for x in range(5):
            result = await self.get("/login/token_valid", auth=self.auth_cookie)

            if result.status_code != 200:
                await asyncio.sleep(1)
                continue

            return [
                PlayerCardState.update_on_first_load(),
                WelcomeState.disable_all(),
                LoginState.reset_auth(),
                rx.redirect(self.get_day_url())
            ]

        return rx.redirect("/error/401")


class LimboPage(AbstractSiteBuilder):
    def page(self) -> rx.Component:
        return rx.vstack(
            rx.spacer(),
            rx.flex(
                rx.spacer(),
                rx.flex(
                    # rx.spinner(size="3"),
                    rx.heading("Challenges werden geladen..."),
                    spacing="3",
                    align_items="center",
                    direction="row",
                ),
                rx.spacer(),
                direction="row",
                width="100%",
            ),
            rx.spacer(),
            height="100vh",
            width="100vw",
        )

    def configure(self) -> None:
        self.page_title = "Redirecting"
        self.url = "/login_redirect"
        # self.background_class = "event_background_team"
        self.is_standalone = True
        self.hide_sidebar = True
        self.on_load = [LimboPageState.check_auth]
        self.background_class = "black"
