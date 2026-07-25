import reflex as rx
import reflex_chakra as rc
from website.engine.site import AbstractSiteBuilder
from website.engine.tasks.widget import TaskWidget
from website.engine.task_conf import PlayerCardState, AccordionState, render_task
from website.engine.challenge import *
from ..tasks.challenge_01_tasks import *
from website.unlock_settings import *
from website.widgets.typography import code_block

#Inhalt der Tabelle
class TableState(rx.State):

    table_1_rows: list[dict[str, str]] = [
        {"cmd": "cd",     "desc": "Wechsle ins Home-Verzeichnis"},
        {"cmd": "cd <Verzeichnis>",     "desc": "Wechsle in <Verzeichnis>"},
        {"cmd": "cd .. ",      "desc": "Wechsle eine Verzeichnisebene zurück"},
        {"cmd": "ls",  "desc": "Inhalt des aktuellen Verzeichnisses anzeigen"},
        {"cmd": "ls -l",  "desc": "Detaillierte Informationen über Inhalt des aktuellen Verzeichnisses"},
        {"cmd": "ls -a",  "desc": "Listet alle Dateien, einschließlich versteckter auf"},
        {"cmd": "cat <Datei>","desc": "Inhalt von <Datei> anzeigen"},
        {"cmd": "pwd","desc": "Aktuelles Verzeichnis anzeigen"},
        {"cmd": "mkdir <Verzeichnis>","desc": "Neues Verzeichnis erstellen"},
    ]

class Kapitel_01(AbstractSiteBuilder):
    PAGE_ID = "challenge_01"
    def page(self) -> rx.Component:
        return rx.vstack(
            rx.hstack(
                rx.heading(
                    "01: Überschrift 0815",   
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
                    "⌨️",  
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
                CondState.is_ready & PlayerCardState.update_day_ready[1],
                rx.vstack(

                    rx.cond(
                        CondState.event_enabled,
                        rx.vstack(

                            rx.markdown(
                                r"""Herzlich Willkommen beim **"Dummy" - Capture-the-Flag Event!** 👋"""
                            ),

                            rx.text(
                                """Lorem Ipsum"""
                            ),
                            
                            rx.flex(
                                rx.spacer(),
                                rx.link(rx.button(rx.icon(tag="message-circle-more"),
                                                "Nehmen Sie mit uns Kontakt auf..."),
                                        href=f"https://{os.getenv('DOMAIN')}/char_01/"),
                                rx.spacer(),
                                width="100%",
                            ),

                            rx.text(
                                """Lorem Ipsum"""
                            ),

                            rx.divider(orientation="horizontal", color_scheme="jade", decorative=True, size="4"),

                            rx.text(
                                rx.text.strong("Überschrift"),
                                font_family="IBM Plex Mono",
                                font_size="1.5em",
                                color=self.main_color,
                                display=["flex", "flex", "flex", "flex", "flex"],
                            ),

                            rx.markdown(
                                r"""Markdown **Lorem** Ipsum"""
                            ),

                            rx.box(
                                rx.markdown(
                                    r"""Box Lorem Ipsum"""
                                ),
                                style={
                                    "maxWidth": "1200px",
                                    "width": "100%",
                                    "margin": "24px auto",
                                    "padding": "25px",
                                    "borderRadius": "16px",
                                    "background": (
                                        "linear-gradient(135deg, "
                                        "rgba(180, 255, 210, 0.18) 0%, "
                                        "rgba(160, 240, 190, 0.10) 100%)"
                                    ),
                                    "border": "1px solid rgba(255, 255, 255, 0.18)",
                                    "boxShadow": "0 2px 10px rgba(120, 255, 180, 0.18)",
                                    "boxSizing": "border-box",
                                }
                            ),



                            rx.text(
                                """Lorem Ipsum"""
                            ),

                            rx.box(
                                rx.markdown(
                                    r"""**Übrigens:** Lorem Ipsum"""
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

                            render_task(self.PAGE_ID, 0, "Aufgabe 1.1", TaskWidget(task_01_00)),

                            rx.divider(orientation="horizontal", color_scheme="jade", decorative=True, size="4"),

                            rx.cond(
                                PlayerCardState.tasks_solved["day_01_task_00"] | PlayerCardState.enable_test_mode,
                                rx.vstack(
                                    rx.text(
                                        rx.text.strong("Überschrift"),
                                        font_family="IBM Plex Mono",
                                        font_size="1.5em",
                                        color=self.main_color,
                                        display=["flex", "flex", "flex", "flex", "flex"],
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

                                    rx.text.strong(
                                        """Lorem Ipsum"""
                                    ),

                                    render_task(self.PAGE_ID, 1, "Aufgabe 1.2", TaskWidget(task_01_01)),

                                    rx.divider(orientation="horizontal", color_scheme="jade", decorative=True, size="4"),

                                    rx.cond(
                                        PlayerCardState.tasks_solved["day_01_task_01"] | PlayerCardState.enable_test_mode,
                                        rx.vstack(

                                            rx.text(
                                                rx.text.strong("Überschrift"),
                                                font_family="IBM Plex Mono",
                                                font_size="1.5em",
                                                color=self.main_color,
                                                display=["flex", "flex", "flex", "flex", "flex"],
                                            ),

                                            rx.markdown(
                                                r"""Lorem Ipsum"""
                                            ),

                                            render_task(self.PAGE_ID, 2, "Aufgabe 1.3", TaskWidget(task_01_02)),

                                            rx.cond(
                                                PlayerCardState.tasks_solved["day_01_task_02"] | PlayerCardState.enable_test_mode,
                                                rx.vstack(

                                                    rx.markdown(
                                                        r"""Lorem Ipsum """
                                                    ), 

                                                    rx.markdown(
                                                        r"""Lorem Ipsum """
                                                    ),

                                                    render_task(self.PAGE_ID, 3, "Aufgabe 1.4", TaskWidget(task_01_03)),

                                                    rx.cond(
                                                        PlayerCardState.tasks_solved["day_01_task_03"] | PlayerCardState.enable_test_mode,
                                                        rx.vstack(

                                                            rx.markdown(
                                                                r"""Lorem Ipsum"""
                                                            ),

                                                            render_task(self.PAGE_ID, 4, "Aufgabe 1.5", TaskWidget(task_01_04)),
                                                            
                                                            rx.divider(orientation="horizontal", color_scheme="jade", decorative=True, size="4"),

                                                            rx.cond(
                                                                PlayerCardState.tasks_solved["day_01_task_04"] | PlayerCardState.enable_test_mode,
                                                                rx.vstack(

                                                                    rx.text(
                                                                        rx.text.strong("Lorem Ipsum"),
                                                                        font_family="IBM Plex Mono",
                                                                        font_size="1.5em",
                                                                        color=self.main_color,
                                                                        display=["flex", "flex", "flex", "flex", "flex"],
                                                                    ),

                                                                    rx.markdown(
                                                                        r"""Lorem Ipsum"""
                                                                    ), 

                                                                    rx.markdown(
                                                                        r"""Lorem Ipsum"""
                                                                    ), 

                                                                    render_task(self.PAGE_ID, 5, "Aufgabe 1.6", TaskWidget(task_01_05)),

                                                                    rx.cond(
                                                                        PlayerCardState.tasks_solved["day_01_task_05"] | PlayerCardState.enable_test_mode,
                                                                        rx.vstack(

                                                                            rx.markdown(
                                                                                r"""Lorem Ipsum"""
                                                                            ),

                                                                            render_task(self.PAGE_ID, 6, "Aufgabe 1.7", TaskWidget(task_01_06)),

                                                                            rx.divider(orientation="horizontal", color_scheme="jade", decorative=True, size="4"),

                                                                            rx.cond(
                                                                                PlayerCardState.tasks_solved["day_01_task_06"] | PlayerCardState.enable_test_mode,
                                                                                rx.vstack(


                                                                                    rx.text(
                                                                                        rx.text.strong("Überschrift"),
                                                                                        font_family="IBM Plex Mono",
                                                                                        font_size="1.5em",
                                                                                        color=self.main_color,
                                                                                        display=["flex", "flex", "flex", "flex", "flex"],
                                                                                    ),

                                                                                    rx.markdown(
                                                                                        r"""Lorem Ipsum"""
                                                                                    ), 

                                                                                    rx.markdown(
                                                                                        r"""Lorem Ipsum"""
                                                                                    ), 

                                                                                    rc.accordion(
                                                                                        rc.accordion_item(
                                                                                            rc.accordion_button(
                                                                                                rc.heading("Abbildung 1.1: Lorem Ipsum", size="sm"),
                                                                                                rc.accordion_icon(),
                                                                                            ),
                                                                                            rc.accordion_panel(
                                                                                                rx.center(
                                                                                                    rx.card(
                                                                                                        rx.inset(
                                                                                                            rx.image(
                                                                                                                src="/custom/CyberRange_Widget.png",
                                                                                                                width="100%",      # Bild füllt die Card
                                                                                                                height="auto",
                                                                                                                object_fit="cover"
                                                                                                            ),
                                                                                                            width="100%",
                                                                                                            height="auto",
                                                                                                            padding="0",
                                                                                                            margin="0"
                                                                                                        ),
                                                                                                        width="50%",           # Card ist 50% breit → Bild auch
                                                                                                        padding="0",
                                                                                                        margin="0"
                                                                                                    ),
                                                                                                    width="100%",
                                                                                                    padding="20px 0"
                                                                                                )
                                                                                            ),
                                                                                        ),
                                                                                        allow_toggle=True,
                                                                                        allow_multiple=True,
                                                                                        width="100%",
                                                                                    ),

                                                                                    rx.box(
                                                                                        rx.markdown(r"""Lorem Ipsum"""),

                                                                                        style={
                                                                                            "maxWidth": "1200px",
                                                                                            "width": "100%",
                                                                                            "margin": "24px auto",
                                                                                            "padding": "25px",
                                                                                            "borderRadius": "16px",
                                                                                            "background": (
                                                                                                "linear-gradient(135deg, "
                                                                                                "rgba(255, 210, 160, 0.18) 0%, "
                                                                                                "rgba(255, 190, 140, 0.10) 100%)"
                                                                                            ),
                                                                                            "border": "1px solid rgba(255, 255, 255, 0.18)",
                                                                                            "boxShadow": "0 2px 10px rgba(255, 180, 120, 0.18)",
                                                                                            "boxSizing": "border-box",
                                                                                        }
                                                                                    ),

                                                                                    rx.markdown(
                                                                                        r"""Lorem Ipsum"""
                                                                                    ), 

                                                                                    rc.accordion(
                                                                                        rc.accordion_item(
                                                                                            rc.accordion_button(
                                                                                                rc.heading("Abbildung 1.2: Lorem Ipsum", size="sm"),
                                                                                                rc.accordion_icon(),
                                                                                            ),
                                                                                            rc.accordion_panel(
                                                                                                rx.center(
                                                                                                    rx.card(
                                                                                                        rx.inset(
                                                                                                            rx.image(
                                                                                                                src="/custom/Guacamole.png",
                                                                                                                width="100%",      # Bild füllt die Card
                                                                                                                height="auto",
                                                                                                                object_fit="cover"
                                                                                                            ),
                                                                                                            width="100%",
                                                                                                            height="auto",
                                                                                                            padding="0",
                                                                                                            margin="0"
                                                                                                        ),
                                                                                                        width="50%",           # Card ist 50% breit → Bild auch
                                                                                                        padding="0",
                                                                                                        margin="0"
                                                                                                    ),
                                                                                                    width="100%",
                                                                                                    padding="20px 0"
                                                                                                )
                                                                                            ),
                                                                                        ),
                                                                                        allow_toggle=True,
                                                                                        allow_multiple=True,
                                                                                        width="100%",
                                                                                    ),

                                                                                    rx.markdown(
                                                                                        r"""Lorem Ipsum"""
                                                                                    ), 

                                                                                    rc.accordion(
                                                                                        rc.accordion_item(
                                                                                            rc.accordion_button(
                                                                                                rc.heading("Abbildung 1.3: Lorem Ipsum", size="sm"),
                                                                                                rc.accordion_icon(),
                                                                                            ),
                                                                                            rc.accordion_panel(
                                                                                                rx.center(
                                                                                                    rx.card(
                                                                                                        rx.inset(
                                                                                                            rx.image(
                                                                                                                src="/custom/Kali.png",
                                                                                                                width="100%",      # Bild füllt die Card
                                                                                                                height="auto",
                                                                                                                object_fit="cover"
                                                                                                            ),
                                                                                                            width="100%",
                                                                                                            height="auto",
                                                                                                            padding="0",
                                                                                                            margin="0"
                                                                                                        ),
                                                                                                        width="50%",           # Card ist 50% breit → Bild auch
                                                                                                        padding="0",
                                                                                                        margin="0"
                                                                                                    ),
                                                                                                    width="100%",
                                                                                                    padding="20px 0"
                                                                                                )
                                                                                            ),
                                                                                        ),
                                                                                        allow_toggle=True,
                                                                                        allow_multiple=True,
                                                                                        width="100%",
                                                                                    ),

                                                                                    rx.markdown(
                                                                                        r"""Lorem Ipsum"""
                                                                                    ), 

                                                                                    rc.accordion(
                                                                                        rc.accordion_item(
                                                                                            rc.accordion_button(
                                                                                                rc.heading("Abbildung 1.4: Lorem Ipsum", size="sm"),
                                                                                                rc.accordion_icon(),
                                                                                            ),
                                                                                            rc.accordion_panel(
                                                                                                rx.center(
                                                                                                    rx.card(
                                                                                                        rx.inset(
                                                                                                            rx.image(
                                                                                                                src="/custom/terminal.png",
                                                                                                                width="100%",      # Bild füllt die Card
                                                                                                                height="auto",
                                                                                                                object_fit="cover"
                                                                                                            ),
                                                                                                            width="100%",
                                                                                                            height="auto",
                                                                                                            padding="0",
                                                                                                            margin="0"
                                                                                                        ),
                                                                                                        width="50%",           # Card ist 50% breit → Bild auch
                                                                                                        padding="0",
                                                                                                        margin="0"
                                                                                                    ),
                                                                                                    width="100%",
                                                                                                    padding="20px 0"
                                                                                                )
                                                                                            ),
                                                                                        ),
                                                                                        allow_toggle=True,
                                                                                        allow_multiple=True,
                                                                                        width="100%",
                                                                                    ),

                                                                                    rx.markdown(
                                                                                        r"""Lorem Ipsum"""
                                                                                    ),

                                                                                    rx.text.strong("Tabelle 1.1: Wichtige Befehle (engl. Commands)"),
                                                                                    rc.table(
                                                                                        rc.thead(
                                                                                            rc.tr(
                                                                                                rc.th("Terminal-Befehl"),
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

                                                                                    rx.markdown(
                                                                                        r"""Lorem Ipsum"""
                                                                                    ),

                                                                                    rx.box(
                                                                                        rx.markdown(
                                                                                            r"""Lorem Ipsum"""
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

                                                                                    render_task(self.PAGE_ID, 7, "Aufgabe 1.8", TaskWidget(task_01_07)),

                                                                                    rx.cond(
                                                                                        PlayerCardState.tasks_solved["day_01_task_07"] | PlayerCardState.enable_test_mode,
                                                                                        rx.vstack(                                                                                    

                                                                                            rx.markdown(
                                                                                                r"""Lorem Ipsum"""
                                                                                            ),

                                                                                            render_task(self.PAGE_ID, 8, "Aufgabe 1.9", TaskWidget(task_01_08)),

                                                                                            rx.cond(
                                                                                                PlayerCardState.tasks_solved["day_01_task_08"] | PlayerCardState.enable_test_mode,
                                                                                                rx.vstack(                                                                                        

                                                                                                    rx.markdown(
                                                                                                        r"""Lorem Ipsum"""
                                                                                                    ),

                                                                                                    render_task(self.PAGE_ID, 9, "Aufgabe 1.10", TaskWidget(task_01_09)),

                                                                                                    rx.divider(orientation="horizontal", color_scheme="jade", decorative=True, size="4"),

                                                                                                    rx.cond(                                
                                                                                                        PlayerCardState.tasks_solved["day_01_task_09"] | PlayerCardState.enable_test_mode,
                                                                                                        rx.vstack(


                                                                                                            rx.text(
                                                                                                                rx.text.strong("Was springt für Sie dabei heraus?"),
                                                                                                                font_family="IBM Plex Mono",
                                                                                                                font_size="1.5em",
                                                                                                                color=self.main_color,
                                                                                                                display=["flex", "flex", "flex", "flex", "flex"],
                                                                                                            ),

                                                                                                            rx.text(
                                                                                                                """Bei diesem Spiel gibt es für Sie natürlich auch was zu gewinnen! Aber sehen Sie selbst ... """
                                                                                                            ), 

                                                                                                            rc.accordion(
                                                                                                                rc.accordion_item(
                                                                                                                rc.accordion_button(
                                                                                                                    rc.heading("Medaillen für die Besten betrachten", size="sm"),
                                                                                                                    rc.accordion_icon(),
                                                                                                                    ),
                                                                                                                    rc.accordion_panel(
                                                                                                                        rx.flex(
                                                                                                                            rx.spacer(),
                                                                                                                            rx.card(
                                                                                                                                rx.inset(
                                                                                                                                    rx.image(
                                                                                                                                        src="/custom/CTF_at_TCV_Trophy.png",
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

                                                                                                            rx.text(
                                                                                                                """Lorem Ipsum"""
                                                                                                            ),

                                                                                                            rx.flex(
                                                                                                                rx.spacer(),
                                                                                                                rx.link(rx.button(rx.icon(tag="arrow-big-right"),"Auf zum nächsten Kapitel..."), href=f"https://{os.getenv('DOMAIN')}/challenge_02/"),
                                                                                                                rx.spacer(),
                                                                                                                width="100%",
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
                                            ),
                                        ),
                                    ),
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
            on_mount=lambda: AccordionState.init(self.PAGE_ID, 10)
        )

    def configure(self) -> None:
        #pass 
        self.url = "/challenge_01"
        self.name = "01: Kapitel 01"
        self.icon = "keyboard"
        self.main_color = "#04B486"
        self.is_standalone = False
        self.hide_sidebar = False
        self.on_load = [CondState.reset_check_status,CondState.do_checks,CondState.do_check_cyberrange,PlayerCardState.update_day(1)]
        self.background_class = "black"
        self.auth_required = True
        self.unlock_day = unlock_always