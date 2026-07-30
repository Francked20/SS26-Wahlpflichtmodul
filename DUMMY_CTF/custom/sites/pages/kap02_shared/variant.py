"""Shared State fuer Kapitel 02 Sub-pages"""

import hashlib
import reflex as rx
from website.auth_lib import AuthCookie

# Must match the generator (--variants)
N_VARIANTS = 200


class DhVariantState(AuthCookie):
    """Derives the personal variant index from the username"""

    @rx.var
    def variant_index(self) -> int:
        try:
            username = self.data_cookie
            if not username:
                return -1
            digest = hashlib.sha256(username.strip().lower().encode()).hexdigest()
            return int(digest, 16) % N_VARIANTS
        except (TypeError, AttributeError):
            return -1

    @rx.var
    def index_label(self) -> str:
        idx = self.variant_index
        return str(idx) if idx >= 0 else "?"

    @rx.var
    def cap_1(self) -> str:
        return f"/custom/0200/{self.variant_index}/challenge_1.tcvcap"

    @rx.var
    def cap_2(self) -> str:
        return f"/custom/0200/{self.variant_index}/challenge_2.tcvcap"

    @rx.var
    def cap_3(self) -> str:
        return f"/custom/0200/{self.variant_index}/challenge_3.tcvcap"

    @rx.var
    def cap_4(self) -> str:
        return f"/custom/0200/{self.variant_index}/challenge_4.tcvcap"

    @rx.var
    def cap_5(self) -> str:
        return f"/custom/0200/{self.variant_index}/challenge_5.tcvcap"

    @rx.var
    def cap_6(self) -> str:
        return f"/custom/0200/{self.variant_index}/challenge_6.tcvcap"

    @rx.var
    def cap_7(self) -> str:
        return f"/custom/0200/{self.variant_index}/challenge_7.tcvcap"

    @rx.var
    def cap_8(self) -> str:
        return f"/custom/0200/{self.variant_index}/challenge_8.tcvcap"

    @rx.var
    def cap_9(self) -> str:
        return f"/custom/0200/{self.variant_index}/challenge_9.tcvcap"

    @rx.var
    def cap_10(self) -> str:
        return f"/custom/0200/{self.variant_index}/challenge_10.tcvcap"


def index_banner(color: str) -> rx.Component:
    """Small banner showing the student's personal index"""
    return rx.box(
        rx.hstack(
            rx.icon("fingerprint", size=20),
            rx.text("Ihr persönlicher Index: ",
                    rx.text.strong(DhVariantState.index_label),
                    font_size="1.05em"),
            align_items="center", spacing="2",
        ),
        style={
            "maxWidth": "1200px", "width": "100%", "margin": "12px auto",
            "padding": "14px 18px", "borderRadius": "12px",
            "background": "rgba(180, 210, 255, 0.10)",
            "border": "1px solid rgba(255,255,255,0.14)",
            "boxSizing": "border-box", "borderLeft": f"4px solid {color}",
        },
    )


def download_button(text: str, href) -> rx.Component:
    """Capture-Download-Link, als Button gestylt"""
    return rx.el.a(
        rx.hstack(
            rx.icon("download", size=18),
            rx.text(text, font_weight="500"),
            align_items="center", spacing="2",
        ),
        href=href,
        download="",
        target="_blank",
        rel="noopener",
        style={
            "display": "inline-flex",
            "margin": "8px auto",
            "padding": "10px 18px",
            "borderRadius": "10px",
            "background": "rgba(4, 180, 134, 0.18)",
            "border": "1px solid #04B486",
            "color": "#04B486",
            "textDecoration": "none",
            "cursor": "pointer",
        },
    )
