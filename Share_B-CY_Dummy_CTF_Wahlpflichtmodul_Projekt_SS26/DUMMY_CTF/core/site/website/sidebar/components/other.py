import reflex as rx

__all__ = ["seperator"]


def seperator() -> "rx.Component":
    """returns an universal seperator"""
    return rx.box(
        rx.divider(),
        class_name="seperator",
    )
