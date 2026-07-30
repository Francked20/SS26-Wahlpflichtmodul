import abc
import importlib.util
import inspect
import itertools
import os
import traceback as tb
from datetime import datetime

# import fastapi
import typing

import reflex as rx

# from website.engine.tasks.meta import MetaTask
from website.sidebar import sidebar
from website.logger import create_logger
from website.auth_lib import PageAuthState
from website.engine.task_conf import PlayerCardState

from beanie import Document, Indexed
from typing import Annotated, List
from pydantic import BaseModel

# from website.engine.tasks.models import Challenge

logger = create_logger("site-engine")


class UserStats(BaseModel):
    points: int = 0
    challenges_solved: int = 0
    streak: int = 0
    first_solves: int = 0
    badges: str = ""


class User(Document):
    # id: UUID = Field(default_factory=uuid4)
    username: Annotated[str, Indexed(unique=True)]
    username_display: str

    email: str
    pw_hash: str

    avatar_index: str

    team: str = ""
    team_leader: bool = False

    stats: UserStats = UserStats()

    class Settings:
        name = "users"


solution_obj = str | List[str]


# def load_pages(app: "rx.App") -> None:
async def load_pages(app: "rx.App", root_path: str, warn_missing_builder=False) -> None:
    """Loads the pages from ./site and subfolders"""
#    root_path = root_path.removesuffix("/")
    root_path = os.path.abspath(root_path).rstrip("/")

    on_path = os.getenv("PYTHONPATH").split(":")

    logger.info(f"Searching through {root_path}...")

    modules: list[str] = []
    for root, _, files in os.walk(root_path):
        local_files = [file.replace(".py", "") for file in files if file.endswith('.py')]

        # avoid Python loading issues by requiring folder path declaration
        python_paths = {p: root.startswith(p) for p in on_path}
        if not any(python_paths.values()):
            logger.error(f"Folder {root} is not in PYTHONPATH! Skipping loading of pages.")
            return

        # fetch first matching pythonpath and adjust for local import
        local_root = root.removeprefix([k for k, v in python_paths.items() if v][0]).strip(os.sep)

        # build import path with local root path
        modules += [".".join(local_root.split(os.sep) + [file]) for file in local_files]

    logger.info(f"Found {len(modules)} files to load. Loading...")

    # load pages from /sites
    pages: list[AbstractSiteBuilder] = []
    used_urls: dict[str, str] = {}

    for module in modules:
        try:
            length = len(pages)
            imported_module = importlib.import_module(module)

            for name in dir(imported_module):
                attribute = getattr(imported_module, name)

                if not inspect.isclass(attribute):
                    continue

                # load page and configure
                if issubclass(attribute, AbstractSiteBuilder) and attribute != AbstractSiteBuilder:
                    mod_name = f"{module}.{attribute.__name__}"

                    page = attribute(app, mod_name)
                    page.configure()

                    if page.url in used_urls:
                        err_url = used_urls[page.url]
                        logger.error(f"URL `{page.url}` from `{mod_name}` is already used by {err_url}. Skipping...")
                        continue

                    pages.append(page)
                    used_urls.update({page.url: f"`{module}.{attribute.__name__}`"})

            if length == len(pages) and warn_missing_builder:
                logger.error(f"Could not find any sites in `{module}`. Did you use `AbstractSiteBuilder`?")

        except Exception as e:
            logger.error(f"Failed to load module: `{module}` -> {type(e)}: {e}")
            tb.print_exc()

    # group categories
    pages.sort(key=lambda p: p.group)
    grouped_pages: list[list[AbstractSiteBuilder]] = [list(v) for k, v in itertools.groupby(pages, key=lambda p: p.group)]

    for group in grouped_pages:
        # sort pages by priority first and alphabetically second
        group.sort(key=lambda p: (-p.position_priority, p.name))

        for page in group:
            page.configure()

            try:
                if page.url in getattr(app, "_unevaluated_pages"):
                    logger.error(f"URL {page.url} is already in use! Skipping...")
                    continue

                if not page.hide_sidebar:
                    s_bars: rx.Component = sidebar.sidebar([
                        (g[0].group, [p.navigation_element(page) for p in g if not p.is_standalone])
                        for g in grouped_pages
                        if any(not p.is_standalone for p in g)
                    ])
                    app.add_page(
                        rx.hstack(s_bars, page.build(app)),
                        route=page.url,
                        title=page.page_title,
                        image=page.page_icon,
                        on_load=page.on_load,
                    )

                else:
                    app.add_page(
                        page.build(app),
                        route=page.url,
                        title=page.page_title,
                        image=page.page_icon,
                        on_load=page.on_load,
                    )

                logger.info(f"Loaded page `{page.__class__.__name__}` on {page.url}")

            except Exception as e:
                logger.error(f"Failed to load page: {page}\n-> {type(e)}: {e}")
                tb.print_exc()


#    asyncio.run(register_tasks())
#    await register_tasks()
#
# async def register_tasks():
#     logger.info("Setting up MongoDB connection...")
#     mongo = MongoDB()
#     await mongo.connect_mapper()
#
#     # Prepare your challenge dicts as before (however you do it in Reflex)
#     all_tasks = [task.to_backend_dict() for task in MetaTask]
#
#     # Insert/update challenges
#     for form in all_tasks:
#         challenge = await Challenge.find_one(Challenge.day == form["day"], Challenge.task == form["task"])
#         if challenge:
#             logger.info(f"Updating challenge {form['day']}/{form['task']}")
#             await challenge.update({"$set": form})
#         else:
#             logger.info(f"Creating new challenge {form['day']}/{form['task']}")
#             new_challenge = Challenge(**form)
#             await new_challenge.create()
#
#     await mongo.disconnect()
#     logger.info(f"Successfully registered {len(all_tasks)} tasks.")


class PageWrappers:
    @staticmethod
    def auth_required(page: "AbstractSiteBuilder") -> "rx.Component":
        return rx.flex(
            rx.cond(
                PageAuthState.is_authenticated,
                rx.flex(
                    page.page(),
                    class_name=page.background,
                ),
                rx.flex(
                    rx.flex(
                        rx.spacer(),
                        rx.text("Laden..."),
                        rx.spacer(),
                        width="100%",
                    ),
                    class_name=page.background,
                    # on_mount=[PageAuthState.reloader],
                ),
            ),
            on_mount=PageAuthState.check_auth,
            style=page.style,
        )


class DayLockComponent(rx.ComponentState):
    can_show_page: bool = False
    _unlock_on: datetime

    def check_page(self):
        if datetime.now() > self._unlock_on:
            self.can_show_page = True
            return None

        else:
            return rx.redirect("/zugriff_verweigert")

    @classmethod
    def get_component(cls, page: rx.Component, unlock: datetime) -> "rx.Component":
        cls._unlock_on = unlock

        # ToDo: wrap this inside the sidebar maybe?
        return rx.cond(
            cls.can_show_page,
            page,
            rx.flex(
                rx.spacer(),
                rx.spinner(size="3"),
                rx.spacer(),
                margin_top="2em",
                width="100%",
                on_mount=cls.check_page
            ),
        )


class AbstractSiteBuilder(abc.ABC):
    """Abstract class for page engine"""

    def __init__(self, app: "rx.App", mod_name: str = ""):
        """Init with default values. Set in `configure`"""
        self.app = app
        self.module_name = mod_name

        self.is_standalone = False  # hides site from showing in sidebar
        self.hide_sidebar = False  # hides sidebar on the page
        self.background_class = ""  # CSS classes applied to the top div

        self.name = self.__class__.__name__  # Name shown in the sidebar
        self.icon = "flag"  # Icon show in the sidebar, see lucide.dev
        self.main_color = "#fff5eee0"  # Color of text and icon
        self.url = f"/{self.__class__.__name__}".lower()  # url of the site (multiple uses get detected)

        self.page_title: str = f"{os.getenv('PAGE_TITLE')}"  # Title shown in the browser tab (top)
        self.page_icon: str = "/favicon.ico"  # Icon shown in the browser tab (top)

        self.group: str = "zzz"  # group sites in sidebar (alphabetically sorted)
        self.position_priority: int = 0  # sort inside the group, high numbers in the top

        self.auth_required = False  # user needs to be logged in to show site
        self.unlock_day: typing.Optional[datetime] = None  # define a Datetime object on which the site gets accessible

        self.on_load = []  # events or functions to be executed on site loading
        self.style = {"text-align": "justify"}  # additional page styling properties

    @abc.abstractmethod
    def page(self) -> "rx.Component":
        """Set your page here. Must be defined"""
        raise NotImplementedError()

    def configure(self) -> None:
        """Configure parameters here"""
        pass

    @property
    def background(self) -> str:
        return f"site_default {self.background_class}"

    @typing.final
    def build(self, _app: "rx.App"):
        """Builds the defined page"""

        self.configure()

        # Test if really needed
        #        if self.hide_sidebar is False:
        #            self.on_load.append(PlayerCardState.update_on_first_load)

        # ToDo: Check if datetime-unlocking works!
        # if self.unlock_day:
        #     self.on_load.insert(0, PageAuthState.timestamp_locker(self.unlock_day))

        if self.auth_required:
            page = PageWrappers.auth_required(self)

        else:
            page = rx.flex(
                self.page(),
                class_name=self.background,
                style=self.style,
            )

        # if self.unlock_day:
        #    assert isinstance(self.unlock_day, datetime)
        #    page = DayLockComponent.create(page, self.unlock_day)

        if self.hide_sidebar is False:
            page = rx.flex(
                rx.flex(
                    page,
                    class_name="has_sidebar"
                ),
                width="100vw",
                class_name=f"{self.background_class}"
            )

        self.on_load.insert(0, PlayerCardState.update_each_page)
        return page

    @typing.final
    def navigation_element(self, page: "AbstractSiteBuilder") -> sidebar.NavDescription:
        """Build navigation element"""
        return sidebar.NavDescription(
            self.icon,
            self.name,
            self.main_color,
            self.url,
            highlight=(self.url == page.url)
        )
