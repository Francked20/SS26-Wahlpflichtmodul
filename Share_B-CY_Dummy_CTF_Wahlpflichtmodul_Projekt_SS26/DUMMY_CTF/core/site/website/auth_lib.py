import asyncio
import base64
import os
import typing
import urllib.parse

import reflex as rx
import httpx
import pydantic
from reflex.event import EventSpec

from website.logger import create_logger

logger = create_logger("auth-engine")

MAX_SECONDS = 60 * 60 * 18

domain = os.environ.get("DOMAIN")
chapter_selection_mode = os.getenv("SET_CHAPTER_SELECTION")


class AuthCookie(rx.State):
    auth_cookie: str = rx.Cookie(
        name="AccessToken",
        max_age=MAX_SECONDS,
        secure=True,
        same_site="strict",
    )
    data_cookie: str = rx.Cookie(
        name="CTF_Username",
        # domain=domain,
        path="/",
        max_age=None,
        secure=True,
        #        same_site="strict",
        same_site="none",
    )
    #    data_cookie: str = rx.LocalStorage(name="DataCookie", sync=True)
    avatar_index: str = rx.LocalStorage(name="CTF_AvaIndex", sync=True)

    @rx.var
    def get_username(self) -> str:
        try:
            return self.data_cookie
        except TypeError:
            return "??"

    @rx.var
    def get_avatar_path(self) -> str:
        try:
            index = self.avatar_index
            return f"/players/player_{index}.png"
        except TypeError:
            return "/players/fallback.png"

    @rx.var
    def get_player_path(self) -> str:
        try:
            index = self.avatar_index
            return f"{index}"
        except TypeError:
            return "fallback"


class BackendRequests:  # (rx.State, mixin=True):

    url = f"http://api:8000"

    @classmethod
    def _build_url(cls, path, **params):
        args = "&".join([f"{urllib.parse.urlencode({k: v})}" for k, v in params.items()])
        return f"{cls.url}{path}{'?' if params else ''}{args}"

    @staticmethod
    def _get_headers(auth: typing.Optional[str]) -> dict:
        headers: dict = {
            'accept'      : 'application/json',
            'Content-Type': 'application/json',
        }

        if auth:
            headers |= {"Authorization": f"Bearer {auth}"}

        return headers

    @classmethod
    async def get(cls, path, params=None, auth=None, check=True) -> httpx.Response | EventSpec:
        headers = cls._get_headers(auth)

        async with httpx.AsyncClient(timeout=3, headers=headers) as client:
            response = await client.get(cls._build_url(path, **(params or {})))

        if check:
            if response.status_code >= 500:
                logger.error(
                    f"An unexpected error occurred ({response.status_code}: {response.text})")
                # return rx.redirect("/error/401")

        return response

    @classmethod
    async def post(cls, path, params=None, auth=None, check=True) -> httpx.Response | EventSpec:
        headers = cls._get_headers(auth)
        async with httpx.AsyncClient(timeout=3, headers=headers) as client:
            response = await client.post(cls._build_url(path), json=params)

        if check:
            if response.status_code >= 500:
                logger.error(
                    f"An unexpected error occurred ({response.status_code}: {response.text})")
                # return rx.redirect("/error/401")

        return response

    @classmethod
    async def put(cls):
        raise NotImplementedError()

    @classmethod
    async def delete(cls):
        raise NotImplementedError()


class PageAuthState(AuthCookie, BackendRequests):
    is_authenticated: typing.Optional[bool] = None
    # _backend_auth = asyncio.Event()

    routed_to_error: bool = False

    running_auth: bool = False
    running_reload: bool = False

    def reset_auth(self):
        self.is_authenticated = None
        # self._backend_auth.clear()

        self.routed_to_error = False
        self.running_auth = False
        self.running_reload = False

    def to_error_page(self, force: bool = False):
        if self.routed_to_error:
            return None

        self.routed_to_error = True
        return rx.redirect("/error/401")

    @rx.event(background=True)
    async def check_auth(self):
        async with self:
            if self.running_auth:
                return None

            self.running_auth = True

        try:
            result = await self.get("/login/token_valid", auth=self.auth_cookie)

            async with self:
                value = result.status_code == 200
                self.is_authenticated = value

                if not self.is_authenticated:
                    return self.to_error_page(force=True)

        finally:
            async with self:
                self.running_auth = False

    @rx.event(background=True)
    async def reloader(self):
        async with self:
            if self.running_reload:
                return None

            self.running_reload = True

        try:
            logger.info("Waiting for auth. Reloading page...")
            await asyncio.sleep(1.5)

            # reload page
            if self.is_authenticated is not False:
                return rx.redirect(self.router.page.raw_path)

        finally:
            async with self:
                self.running_reload = False


class LoginState(BackendRequests, AuthCookie):
    username: str = ""
    password: str = ""
    age_confirmed: bool = False
    rules_accepted: bool = False
    reset_pw_rules_accepted: bool = False
    privacy_info_accepted: bool = False

    fields_valid: bool = False
    is_logging_in: bool = False

    failed_auth: bool = False
    failed_register: typing.Optional[int] = None
    failed_pw_reset: typing.Optional[int] = None

    team: typing.Optional[str] = None
    team_leader: typing.Optional[bool] = None

    # _logout_hooks: dict[str, typing.Callable] = {}

    def set_username(self, value: str) -> None:
        self.username = value

    def set_password(self, value: str) -> None:
        self.password = value

    @rx.var
    def check_login_valid(self) -> bool:
        try:
            # pydantic.validate_email(self.username)
            return len(self.password) > 0

        except ValueError:
            return False

    @rx.var
    def check_register_valid(self) -> bool:
        try:
            pydantic.validate_email(self.username)
            #            return self.age_confirmed
            return all([
                self.rules_accepted,
                self.privacy_info_accepted,
                self.age_confirmed,
            ])

        except ValueError:
            return False

    @rx.var
    def check_reset_pw_valid(self) -> bool:
        try:
            pydantic.validate_email(self.username)
            #            return self.age_confirmed
            return all([
                self.reset_pw_rules_accepted,
            ])

        except ValueError:
            return False

    def toggle_age(self) -> None:
        self.age_confirmed = not self.age_confirmed

    def toggle_rules(self) -> None:
        self.rules_accepted = not self.rules_accepted

    def toggle_reset_pw_rules(self) -> None:
        self.reset_pw_rules_accepted = not self.reset_pw_rules_accepted

    def toggle_privacy_info(self) -> None:
        self.privacy_info_accepted = not self.privacy_info_accepted

    @rx.event(background=True)
    async def login(self):
        async with self:
            self.is_logging_in = True

        await asyncio.sleep(0.2)  # ToDo: remove visual delay!

        username = self.username
        password = base64.b64encode(self.password.encode("utf-8")).decode("utf-8")

        try:
            async with httpx.AsyncClient() as client:
                url = self._build_url("/login")
                #            response = await client.post(url, json={"username": username, "password": password})
                response = await client.post(url, json={"username": username, "password": password,
                                                        "team"    : "", "team_leader": False})

                if response.status_code == 200:
                    data = response.json()
                    async with self:
                        self.auth_cookie = data["token"]
                        self.data_cookie = data["display_name"]
                        self.avatar_index = data["avatar_index"]
                        self.team = data["team"]
                        self.team_leader = data["team_leader"]

                    if chapter_selection_mode == "True":
                        return rx.redirect("/login_chapter_selection")
                    else:
                        return rx.redirect("/login_redirect")

                else:
                    async with self:
                        self.failed_auth = True

        finally:
            async with self:
                self.is_logging_in = False

    def logout(self):
        PageAuthState.reset_auth()

        return [
            rx.remove_cookie("AccessToken"),
            #            rx.remove_cookie("DisplayUsername"),
            rx.remove_cookie("CTF_Username"),
            #            rx.remove_local_storage("CTF_Username"),
            rx.remove_local_storage("CTF_AvaIndex"),
            rx.redirect("/"),
        ]

    def reset_auth(self):
        self.reset()

    def clear_failed(self):
        if self.failed_register != 1:
            self.failed_register = None

    def clear_failed_pw_reset(self):
        if self.failed_pw_reset != 1:
            self.failed_pw_reset = None

    async def register(self):
        username = self.username

        async with httpx.AsyncClient() as client:
            url = self._build_url("/register", email=username, age_above_16=True)
            response = await client.post(url)

            if response.status_code == 413:
                self.failed_register = 5
            elif response.status_code == 409:
                self.failed_register = 4
            elif response.status_code == 208:
                self.failed_register = 3
            elif response.status_code < 300:
                self.failed_register = 1
            else:
                self.failed_register = 2

    async def reset_pw(self):
        username = self.username

        async with httpx.AsyncClient() as client:
            url = self._build_url("/reset_pw", email=username)
            response = await client.post(url)

            if response.status_code == 208:
                self.failed_pw_reset = 3
            else:
                self.failed_pw_reset = 1


    def reset_login_auth(self):
         self.failed_auth = False
