import reflex as rx

from website.sidebar.components import player_card, get_logo, navigation_links
from website.sidebar.components.nav_link import NavDescription
from website.engine.task_conf import PlayerCardState

def sidebar(elements: list[list[NavDescription]]) -> "rx.Component":
    return rx.vstack(
        get_logo(),
        rx.scroll_area(
            *[navigation_links(e) for e in elements],
            rx.container(height="1em"),
            type="hover",
            scrollbars="vertical",
            class_name="sidebar_links",
        ),
        player_card(),
        spacing="0",
        class_name="sidebar",
        state=PlayerCardState,
    )
