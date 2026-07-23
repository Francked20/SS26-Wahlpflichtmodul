import dataclasses

import reflex as rx
from .images import hover_icon
from .other import seperator

__all__ = ["navigation_links", "NavDescription"]


@dataclasses.dataclass
class NavDescription:
    icon: str
    text: str
    color: str
    href: str
    highlight: bool = False


def navigation_links(elements: list[NavDescription]) -> "rx.Component":
    """returns all navigation links"""

    highlighted = [d for d in elements if d.highlight]
    if highlighted:
        highlighted = highlighted[0]

    return rx.vstack(
        *[navigation_link(d) for d in elements],
        seperator(),
        width="100%",
        spacing="0",
        on_mount=[
            rx.scroll_to(f"nav_element_{highlighted.href}")
        ] if highlighted else []
    )


def navigation_link(data: NavDescription) -> "rx.Component":
    """returns a clickable navigation item"""
    highlight = "navigation_element_highlight" if data.highlight else ""

    # corner-down-right chevrons-right chevron-right
    widgets = [] if not data.highlight else [hover_icon("chevrons-right", selected=True)]
    widgets += [
        hover_icon(data.icon),
        rx.text(data.text),
    ]

    return rx.flex(
        rx.link(
            rx.hstack(*widgets),
            href=data.href,
        ),
        id=f"nav_element_{data.href}",
        class_name=f"{highlight} navigation_element",
        style=rx.style.Style({"--hover-nav-color": data.color}),
    )
