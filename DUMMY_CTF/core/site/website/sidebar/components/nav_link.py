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


def _group_heading(title: str) -> "rx.Component":
    """Big group title shown above a block of navigation links"""
    return rx.text(
        title,
        class_name="sidebar_group_heading",
        style={
            "textTransform": "uppercase",
            "fontSize": "0.72rem",
            "fontWeight": "700",
            "letterSpacing": "0.08em",
            "opacity": "0.65",
            "padding": "14px 16px 4px 16px",
            "width": "100%",
        },
    )


def navigation_links(elements: list[NavDescription], group_title: str = "") -> "rx.Component":
    """returns all navigation links, optionally with a group heading on top"""

    highlighted = [d for d in elements if d.highlight]
    if highlighted:
        highlighted = highlighted[0]

    heading = [_group_heading(group_title)] if group_title else []

    return rx.vstack(
        *heading,
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
