import reflex as rx

from website.sidebar.components import player_card, get_logo, navigation_links
from website.sidebar.components.nav_link import NavDescription
from website.engine.task_conf import PlayerCardState


def _clean_group_title(group: str) -> str:
    """Entfernt das Sortier-Prefix und versteckt die Default-Gruppe 'zzz'"""
    if group == "zzz":
        return ""
    if len(group) > 2 and group[0].isdigit() and group[1] == "_":
        return group[2:]
    return group


def sidebar(elements: list[tuple[str, list[NavDescription]]]) -> "rx.Component":
    """elements: list of (group_name, [nav items]) tuples, already ordered"""
    return rx.vstack(
        get_logo(),
        rx.scroll_area(
            *[navigation_links(items, _clean_group_title(group)) for group, items in elements],
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
