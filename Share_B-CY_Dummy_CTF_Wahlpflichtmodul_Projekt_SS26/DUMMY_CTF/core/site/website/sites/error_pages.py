import reflex as rx
from website.engine.site import AbstractSiteBuilder
from website.sites.login_limbo import LimboPageState


class NotUnlockedYet(AbstractSiteBuilder):
    def page(self) -> "rx.Component":
        return rx.vstack(
            rx.spacer(),
            rx.flex(
                rx.spacer(),
                rx.flex(
                    rx.heading("⚠️ Error 403: Zugriff verweigert ⚠️", color=self.main_color, size="8"),

                    rx.box(
                        rx.heading(
                            "Warnung! ",
                            margin_bottom="4px",
                            size="3",
                        ),
                        rx.text(
                            """Ohoh… Sie befinden sich auf einer gesperrten Seite!""",
                            rx.spacer(margin_bottom="5px"),
                            """Gehen Sie lieber schnell zurück.""",
                        ),
                        style=rx.style.Style({
                            "background": "var(--amber-a2)",
                            "border": "1px dashed var(--white-a7)",
                        }),
                        padding="16px",
                    ),
                    rx.vstack(
                        rx.spinner(size="3"),  # geht nur bis 3
                        align="center",
                        style=rx.style.Style({
                            "display": "flex",
                            "justify-content": "center",
                            "align-items": "center",
                            "height": "20vh",
                            "width": "100%",
                        }),
                    ),
#                    rx.flex(
#                        "Kehren Sie schnell um, wenn Sie unentdeckt bleiben wollen!",
#                        font_style="italic",
#                        font_size="1em",
#                        color="white",
#                        display=["none", "none", "none", "none", "flex"],
#                        margin_right="15px",
#                    ),
                    
                    rx.button(
                        rx.icon(tag="arrow-big-left-dash"),
                        "zu den Challenges",
                        color_scheme="jade",
                        on_click=rx.redirect(LimboPageState.get_day_url()),
                        width="fit-content",
                    ),
                    spacing="3",
                    align_items="center",
                    direction="column",
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
        # pass
        self.url = "/zugriff_verweigert"
        self.name = "Error 403: Zugriff verweigert"
        # self.icon = "triangle-alert"
        self.main_color = "#04B486"
        self.is_standalone = True
        self.hide_sidebar = True
        self.background_class = "black"
        self.auth_required = True


# noinspection SqlDialectInspection
class Page404(AbstractSiteBuilder):
    def page(self) -> "rx.Component":
        return rx.center(
            rx.vstack(
                rx.heading("404", size="9"),
                rx.heading("no flags here", size="8"),
#                rx.heading("Select a page on the sidebar to return", size="3"),
                align="center",
            ),
            width="100%"
        )

    def configure(self) -> None:
        self.page_title = "Not a hidden flag"
        self.is_standalone = True
        self.hide_sidebar = True
        self.url = "/[unknown]"

#class HiddenFlag(AbstractSiteBuilder):
#    def page(self) -> "rx.Component":
#        return rx.center(
#            rx.vstack(
#                rx.heading("404", size="9"),
#                rx.heading("hints for one flag here", size="8"),
#                rx.heading("Dein Schlüssel: Nftp3rTj6WPqeNOznpkSrVrx4D8VZv-0ORiIpocWCI8=", size="3"),
#                rx.heading("Dein verschlüsseltes Geheimnis: gAAAAABnI0qkCdXcjZpNumsIX2JOeFSwJj-0_ZpxqPvH3Mdh4n135T2WKKQl0HtPr3V5--R1nULl-VpA1bWzmK-Arp_CH0eUO5k7YkIYYKikvQEs2A6I1eBB4Vu8OH5HQDll9l2MaXbN", size="3"),
#                align="center",
#            ),
#            width="100%"
#        )
#
#    def configure(self) -> None:
#        self.page_title = "Hidden flag"
#        self.is_standalone = True
#        self.hide_sidebar = True
#        self.url = "/s/e/c/r/e/t/"  

class Page401(AbstractSiteBuilder):
    def page(self) -> "rx.Component":
        return rx.vstack(
            rx.spacer(),
            rx.flex(
                rx.spacer(),
                rx.flex(
                    rx.heading("401"),
                    rx.callout.root(
                        rx.callout.icon(
                            rx.icon("triangle_alert"),
                            align_items="center",
                            display="flex",
                            height="200%",
                            margin_right="0.5rem",
                        ),
                        rx.callout.text("Sie sind nicht angemeldet!"),
                        rx.callout.text("Bitte melden Sie sich zuerst an."),
                        color_scheme="red",
                        role="alert",
                    ),
                    rx.button(
                        "Zurück zur Startseite",
                        on_click=rx.redirect("/"),
                        width="fit-content",
                    ),
                    spacing="3",
                    align_items="center",
                    direction="column",
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
        self.page_title = "Nicht angemeldet"
        self.is_standalone = True
        self.hide_sidebar = True
        self.url = "/error/401"
        self.background_class = "black"
