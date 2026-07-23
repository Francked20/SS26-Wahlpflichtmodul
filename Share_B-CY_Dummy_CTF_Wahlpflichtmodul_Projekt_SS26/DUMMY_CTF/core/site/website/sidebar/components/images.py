import reflex as rx
from .other import seperator

__all__ = ["get_logo", "hover_icon"]


def get_logo() -> "rx.Component":
    """returns the logo"""
    return rx.vstack(
        rx.link(
            rx.image(
                src="/logo/tcv_logo.png",
                class_name="logo_image"
            ),
            href="https://th-deg.de/tc-vilshofen",
            is_external=True,
        ),
        seperator(),
        gap=0,
    )


def hover_icon(icon: str, selected: bool = False) -> "rx.Component":
    """icon that changes color on hovering"""
    class_name = "select_icon" if selected else "nav_icon"
    stroke_width = 3 if selected else 2

    return rx.icon(
        icon,
        class_name=class_name,
        stroke_width=stroke_width,
    )
