import reflex as rx
import reflex_chakra as rc
from website.engine.site import AbstractSiteBuilder
from website.engine.tasks.widget import TaskWidget
from website.engine.task_conf import PlayerCardState, AccordionState, render_task
from website.engine.challenge import *
from ..tasks.challenge_02_tasks import *
from website.unlock_settings import *
from website.widgets.typography import code_block

#Inhalt der Tabelle
class TableState(rx.State):

    table_1_rows: list[dict[str, str]] = [
        {"cmd": "cd <Verzeichnis>",     "desc": "Wechsle in <Verzeichnis>"},
        {"cmd": "cd .. ",      "desc": "Wechsle eine Verzeichnisebene zurück"},
        {"cmd": "ls",  "desc": "Inhalt des aktuellen Verzeichnisses anzeigen"},
        {"cmd": "cat <Datei>","desc": "Inhalt von <Datei> anzeigen"},
        {"cmd": "id","desc": "Aktuellen Benutzer anzeigen"},
        {"cmd": "pwd","desc": "Aktuelles Verzeichnis anzeigen"},
    ]

    table_2_rows: list[dict[str, str]] = [
        {"cmd": "cd <Verzeichnis>", "desc": "Wechsle in <Verzeichnis>"},
        {"cmd": "cd .. ","desc": "Wechsle eine Verzeichnisebene zurück"},
        {"cmd": "ls",   "desc": "Inhalt des aktuellen Verzeichnisses anzeigen"},
        {"cmd": "type <Datei>", "desc": "Inhalt von <Datei> anzeigen"},
        {"cmd": "whoami ","desc": "Aktuellen Benutzer anzeigen"},
        {"cmd": "pwd","desc": "Aktuelles Verzeichnis anzeigen"},
    ]

class Kapitel_02(AbstractSiteBuilder):
    PAGE_ID = "challenge_02"
    def page(self) -> rx.Component:
        return rx.vstack(
            rx.hstack(
                rx.heading(
                    "02: Überschrift ",  
                    color=self.main_color,
                    size="8",
                    style={
                        "background": "linear-gradient(90deg, #04B486, #00FFFF)",
                        "WebkitBackgroundClip": "text",
                        "WebkitTextFillColor": "transparent",
                        "marginBottom": "0px", 
                    }
                ),
                rx.text(
                    "🗺️",  
                    size="8", 
                    align_self="center", 
                ),
                align_items="center",  
                justify_content="flex-start", 
                width="100%", 
                spacing="1", 
                style={
                    "marginBottom": "24px",  
                }
            ),

# Schneefall-Hintergrund
#            rx.badge(
#                rx.flex(
#                    rx.icon("sun-snow", size=18),
#                    direction="row",
#                    gap="1",
#                    align="center",
#                ),
#                size="2",
#                radius="full",
#                color_scheme="gray",
#                on_click=rx.call_script("snowStorm.toggleSnow()"),
#            ),

            rx.cond(
                CondState.is_ready & PlayerCardState.update_day_ready[2],
                rx.vstack(
                    rx.cond(
                        CondState.event_enabled,
                        rx.cond(
                            PlayerCardState.tasks_solved["day_01_task_09"] | PlayerCardState.enable_test_mode,
                            rx.vstack(

                                rx.text(
                                    """Lorem Ipsum"""
                                ),

                                rx.flex(
                                    rx.spacer(),
                                    rx.link(rx.button(rx.icon(tag="message-circle-more"),
                                                    "Nehmen Sie mit uns Kontakt auf..."),
                                            href=f"https://{os.getenv('DOMAIN')}/char_02/"),
                                    rx.spacer(),
                                    width="100%",
                                ),

                                rx.box(
                                    rx.vstack(
                                        rx.text(
                                        rx.text.strong("""Lorem Ipsum"""),
                                        rx.spacer(margin_bottom="5px"),
                                        rx.markdown(r"""Lorem Ipsum"""),
                                        rx.markdown(r"""Lorem Ipsum"""),
                                        rx.markdown(r"""Lorem Ipsum"""),
                                        rx.markdown(r"""Lorem Ipsum"""),
                                        ),
                                    ),

                                    style={
                                        "maxWidth": "1200px",
                                        "width": "100%",
                                        "margin": "24px auto",
                                        "padding": "25px",
                                        "borderRadius": "16px",
                                        "background": (
                                            "linear-gradient(135deg, "
                                            "rgba(180, 210, 255, 0.18) 0%, "
                                            "rgba(160, 190, 255, 0.10) 100%)"
                                        ),
                                        "border": "1px solid rgba(255, 255, 255, 0.18)",
                                        "boxShadow": "0 2px 10px rgba(120, 160, 255, 0.18)",
                                        "boxSizing": "border-box",
                                    }
                                ),



                                rx.divider(orientation="horizontal", color_scheme="jade", decorative=True, size="4"),

                                rx.text(
                                    rx.text.strong("""Überschrift"""),
                                    font_family="IBM Plex Mono",
                                    font_size="1.5em",
                                    color=self.main_color,
                                    display=["flex", "flex", "flex", "flex", "flex"],
                                ),

                                rx.markdown(
                                    r"""Lorem Ipsum"""
                                ),

                                rx.text(
                                    """Lorem Ipsum"""
                                ),

                                rx.markdown(
                                    r"""Lorem Ipsum"""
                                ),

                                rx.text(
                                    """Lorem Ipsum"""
                                ),

                                rx.markdown(
                                    r"""Lorem Ipsum"""
                                ),

                                rc.accordion(
                                    rc.accordion_item(
                                    rc.accordion_button(
                                        rc.heading("Abbildung 2.1: Lorem Ipsum", size="sm"),
                                        rc.accordion_icon(),
                                        ),
                                        rc.accordion_panel(
                                            rx.flex(
                                                rx.spacer(),
                                                rx.card(
                                                    rx.inset(
                                                        rx.image(
                                                            src="/custom/netzwerk.png",
                                                            width="100%",
                                                            height="100%",
                                                            object_fit="cover"  # Stellt sicher, dass das Bild die gesamte Fläche ausfüllt
                                                        ),

                                                        width="50vw",
                                                        height="auto",  # Passt die Höhe der Karte an die Höhe des Bildes an
                                                        padding="0",  # Entfernt jegliche Innenabstände
                                                        margin="0"    # Entfernt jegliche Außenabstände
                                                    ),
                                                ),
                                                rx.spacer(),
                                                width="100%",
                                            ), 
                                        ),
                                    ),
                                    allow_toggle=True,
                                    allow_multiple=True,
                                    width="100%",
                                ),
                                
                                render_task(self.PAGE_ID, 0, "Aufgabe 2.1", TaskWidget(task_02_00)),

                                rx.divider(orientation="horizontal", color_scheme="jade", decorative=True, size="4"),

                                rx.cond(
                                    PlayerCardState.tasks_solved["day_02_task_00"] | PlayerCardState.enable_test_mode,
                                    rx.vstack(

                                        rx.text(
                                            rx.text.strong("""Überschrift"""),
                                            font_family="IBM Plex Mono",
                                            font_size="1.5em",
                                            color=self.main_color,
                                            display=["flex", "flex", "flex", "flex", "flex"],
                                        ),

                                        rx.text(
                                            """Lorem Ipsum: """
                                        ),

                                        rx.box(
                                            rx.vstack(
                                                rx.text(
                                                rx.text.strong("""Lorem Ipsum"""),
                                                rx.spacer(margin_bottom="5px"),
                                                rx.markdown(r"""Lorem Ipsum"""),
                                                rx.markdown(r"""Lorem Ipsum"""),
                                                ),
                                            ),
                                            style={
                                                "maxWidth": "1200px",
                                                "width": "100%",
                                                "margin": "24px auto",
                                                "padding": "25px",
                                                "borderRadius": "16px",
                                                "background": (
                                                    "linear-gradient(135deg, "
                                                    "rgba(180, 210, 255, 0.18) 0%, "
                                                    "rgba(160, 190, 255, 0.10) 100%)"
                                                ),
                                                "border": "1px solid rgba(255, 255, 255, 0.18)",
                                                "boxShadow": "0 2px 10px rgba(120, 160, 255, 0.18)",
                                                "boxSizing": "border-box",
                                            }
                                        ),

                                        render_task(self.PAGE_ID, 1, "Aufgabe 2.2", TaskWidget(task_02_01)),

                                        rx.cond(
                                            PlayerCardState.tasks_solved["day_02_task_01"] | PlayerCardState.enable_test_mode,
                                            rx.vstack(

                                                render_task(self.PAGE_ID, 2, "Aufgabe 2.3", TaskWidget(task_02_02)),

                                                rx.divider(orientation="horizontal", color_scheme="jade", decorative=True, size="4"),

                                                rx.cond(
                                                    PlayerCardState.tasks_solved["day_02_task_02"] | PlayerCardState.enable_test_mode,
                                                    rx.vstack(

                                                        rx.text(
                                                            rx.text.strong("""Überschrift"""),
                                                            font_family="IBM Plex Mono",
                                                            font_size="1.5em",
                                                            color=self.main_color,
                                                            display=["flex", "flex", "flex", "flex", "flex"],
                                                        ),

                                                        rx.text.strong("""Lorem Ipsum"""),

                                                        rx.markdown(
                                                            r"""Lorem Ipsum"""
                                                        ),

                                                        rx.text.strong("""Lorem Ipsum"""),

                                                        rx.text(
                                                            """Lorem Ipsum"""
                                                        ),

                                                        rx.text(
                                                            """Lorem Ipsum"""
                                                        ),

                                                        rx.text(
                                                            """Lorem Ipsum"""
                                                        ),

                                                        code_block(r"""
Lorem Ipsum
"""),

                                                        rx.text(
                                                            """Lorem Ipsum"""
                                                        ),

                                                        rx.box(
                                                            rx.markdown(
                                                                r"""**Hinweis:** Lorem Ipsum"""
                                                            ),

                                                            style={
                                                                "maxWidth": "1200px",
                                                                "width": "100%",
                                                                "margin": "24px auto",
                                                                "padding": "25px",
                                                                "borderRadius": "16px",
                                                                "background": (
                                                                    "linear-gradient(135deg, "
                                                                    "rgba(180, 210, 255, 0.18) 0%, "
                                                                    "rgba(160, 190, 255, 0.10) 100%)"
                                                                ),
                                                                "border": "1px solid rgba(255, 255, 255, 0.18)",
                                                                "boxShadow": "0 2px 10px rgba(120, 160, 255, 0.18)",
                                                                "boxSizing": "border-box",
                                                            }
                                                        ),

                                                        rx.text(
                                                            """Lorem Ipsum"""
                                                        ),

                                                        
                                                        rx.text.strong("Tabelle 2.1: Wichtige Linux-Befehle"),
                                                            rc.table(
                                                                rc.thead(
                                                                    rc.tr(
                                                                        rc.th("Linux-Befehl"),
                                                                        rc.th("Beschreibung"),
                                                                    )
                                                                ),
                                                                rc.tbody(
                                                                    rx.foreach(
                                                                        TableState.table_1_rows,
                                                                        lambda row: rc.tr(
                                                                            rc.td(row["cmd"]),
                                                                            rc.td(row["desc"]),
                                                                        )
                                                                    )
                                                                ),
                                                                variant="simple",
                                                                size="2",
                                                                width="100%",
                                                            ),

                                                            rx.text.strong("Tabelle 2.2: Wichtige Powershell-Befehle"),
                                                            rc.table(
                                                                rc.thead(
                                                                    rc.tr(
                                                                        rc.th("Befehl"),
                                                                        rc.th("Beschreibung"),
                                                                    )
                                                                ),
                                                                rc.tbody(
                                                                    rx.foreach(
                                                                        TableState.table_2_rows,
                                                                        lambda row: rc.tr(
                                                                            rc.td(row["cmd"]),
                                                                            rc.td(row["desc"]),
                                                                        )
                                                                    )
                                                                ),
                                                                variant="simple",
                                                                size="2",
                                                                width="100%",
                                                            ),

                                                        render_task(self.PAGE_ID, 3, "Aufgabe 2.4", TaskWidget(task_02_03)),

                                                        rx.cond(
                                                            PlayerCardState.tasks_solved["day_02_task_03"] | PlayerCardState.enable_test_mode,
                                                            rx.vstack(

                                                                render_task(self.PAGE_ID, 4, "Aufgabe 2.5", TaskWidget(task_02_04)),

                                                                rx.cond(
                                                                    PlayerCardState.tasks_solved["day_02_task_04"] | PlayerCardState.enable_test_mode,
                                                                    rx.vstack(

                                                                        render_task(self.PAGE_ID, 5, "Aufgabe 2.6", TaskWidget(task_02_05)),

                                                                        rx.cond(
                                                                            PlayerCardState.tasks_solved["day_02_task_05"] | PlayerCardState.enable_test_mode,
                                                                            rx.vstack(

                                                                                render_task(self.PAGE_ID, 6, "Aufgabe 2.7", TaskWidget(task_02_06)),

                                                                                rx.cond(
                                                                                    PlayerCardState.tasks_solved["day_02_task_06"] | PlayerCardState.enable_test_mode,
                                                                                    rx.vstack(
                                                                                        rx.text(
                                                                                            """Glückwunsch! 🎉 Sie haben sich nicht nur das finale Abzeichen verdient und das Event erfolgreich abgeschlossen, sondern 
                                                                                            auch gezeigt, was in Ihnen steckt!"""
                                                                                        ),

                                                                                        rx.text(
                                                                                            """Wahrlich ein Grund zu feiern."""
                                                                                        ),
                                                                                    ),
                                                                                ),
                                                                            ),
                                                                        ),
                                                                    ),
                                                                ),
                                                            ),
                                                        ),
                                                    ),
                                                ),
                                            ),
                                        ),
                                    ),
                                ),
                            ),
                            rx.vstack(
                                rx.text(
                                    """Es müssen zuerst alle Aufgaben des vorherigen Abschnitts gelöst werden, um diesen Abschnitt freizuschalten!"""
                                ),
                            ),
                        ),
                        rx.vstack(
                            rx.text(
                                """Sie wollen schon loslegen? Fair Play! Bitte warten Sie, bis der Spielleiter das Event für alle Teilnehmer startet!"""
                            ),
                        ),
                    ),
                ),
                rx.vstack(
                    rx.spinner()
                ),
            ),
            on_mount=lambda: AccordionState.init(self.PAGE_ID, 7)
        )

    #Name der Seite, Icon in Sidebar
    def configure(self) -> None:
        #pass 
        self.url = "/challenge_02"
        self.name = "02: Kapitel 02"
        self.icon = "map"
        self.main_color = "#04B486"
        self.is_standalone = False
        self.hide_sidebar = False
        self.on_load = [CondState.reset_check_status,CondState.do_checks,PlayerCardState.update_day(2)]
        self.background_class = "black"
        self.auth_required = True
        self.unlock_day = unlock_always