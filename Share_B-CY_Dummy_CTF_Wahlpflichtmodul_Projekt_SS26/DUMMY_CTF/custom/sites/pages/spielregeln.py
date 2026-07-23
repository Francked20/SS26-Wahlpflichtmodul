import os
import reflex as rx

from website.engine.site import AbstractSiteBuilder


class Die_Spielregeln(AbstractSiteBuilder):
    def page(self) -> rx.Component:
        return rx.center(
            rx.vstack(
                rx.spacer(),

                # Überschrift mit Emoji zentriert
                rx.hstack(
                    rx.heading(
                        "Die Spielregeln ",
                        size="8",
                        style={
                            "background": "linear-gradient(90deg, #04B486, #00FFFF)",
                            "WebkitBackgroundClip": "text",
                            "WebkitTextFillColor": "transparent",
                            "marginBottom": "0px",
                        }
                    ),
                    rx.text("🎲", size="8", align_self="center"),
                    align_items="center",
                    justify_content="center",
                    spacing="1",
                    width="100%",
                    style={"marginBottom": "24px"}
                ),

                # Box mit Glassmorph-Optik
                rx.box(


                    rx.heading(
                       """Das "Ethical Hacking Bootcamp" - Capture-the-Flag Event 🕵️‍♀️ 🕵️‍♂️""",
                        margin_bottom="4px",
                        size="3",
                    ),

                    rx.markdown(
                        r"""Sie sind nun im Begriff ein Capture-the-Flag Event der besonderen Art zu spielen! **Capture-the-Flag (kurz CTF)** 
                        ist ein Wettbewerb, bei dem Teams eine Reihe von Aufgaben lösen müssen. Sobald eine Aufgabe erfolgreich gelöst wurde, 
                        findet der Spieler eine "Flagge" 🚩, die als **Beweis für die Erfüllung** gilt. Für das **Einreichen der Flagge** wird 
                        **eine Punktzahl** gutgeschrieben. Je nach Schwere der Aufgabe, gibt es eine angemessene Anzahl an Punkten. """
                    ),
                    rx.spacer(margin_bottom="10px"),
                    rx.markdown(
                        r"""Dieses CTF ist an die Thematik des **"Ethical Hackings"** angelehnt. Das heißt, Sie werden hier nun in die Konzepte 
                        des ethischen Hackings herangeführt! Dabei werden Sie in einem Team **Fragen beantworten** oder in **.txt-Dateien Flaggen 
                        finden**. Dabei geht es für Sie auch um Schnelligkeit!"""
                    ),
                    rx.spacer(margin_bottom="10px"),
                    rx.markdown(
                        r"""Denn auch andere Teams verfolgen die Mission des Findens von Flaggen. Sollte Ihr Team eine Aufgabe erfolgreich lösen, 
                        sehen Sie das an dem **farbigen Balken im Scoreboard**, der sich an Ihre erreichte Punktzahl anpasst!"""
                    ),
                    rx.spacer(margin_bottom="10px"), 

                    rx.center(
                        rx.link(
                            rx.button("Hier kommen Sie zum Scoreboard...", color_scheme="jade", is_external=True),

                            href=f"https://{os.getenv('SCR_DOMAIN')}"
                        ),
                        margin_bottom="10px"
                    ),

                    rx.markdown(
                        r"""Wie bereits erwähnt, finden Sie in diesem CTF Wissensfragen. Diese können das Format von **Single-/Multiple-Choice-Fragen** 
                        haben. Um diese Fragen beantworten zu können, können Sie sich entweder im Team austauschen oder zu diesem Thema im Internet 
                        recherchieren. Die **Lösungen und Flaggen zu den Freitextantworten** finden Sie alle in den für Sie zur Verfügung gestellten 
                        **virtuellen Maschinen**!"""
                    ),
                    rx.spacer(margin_bottom="10px"),

                    rx.markdown(
                        r"""Die Flaggen, die Sie finden werden, folgen dabei **folgendem Muster**:"""
                    ),
                    rx.spacer(margin_bottom="10px"),
 
                    rx.center(
                        rx.code("HIY{flaggenstring}", color="yellow.300"),
                        margin_bottom="10px"
                    ),
 
                    rx.spacer(margin_bottom="10px"),
                    rx.markdown(
                        r"""Das CTF selbst ist in mehrere Unterkategorien unterteilt. Jede dieser Unterkategorien hält **wichtige Aufgaben** 
                        für Sie bereit! Durch das Lösen aller Aufgaben dieser Kategorien können Sie den Abschnitt abschließen und die **nächste 
                        Unterkategorie wird für Sie freigeschalten**. Das bedeutet für Sie, durch die **korrekte Beantwortung** ✅ von Fragen 
                        und das **Lösen von Challenges** verdienen Sie und Ihr Team "Erfahrungspunkte", kurz "XPs" ✨. Doch Vorsicht, durch 
                        **falsche Antworten** ❌ oder das **Hinzuziehen von Hinweisen**, verringert sich die maximale Anzahl Ihrer XPs, 
                        die Sie für die korrekte Antwort bekommen hätten. Sollten Sie und Ihr Team die Ersten sein, die eine Challenge lösen, 
                        verdienen Sie zusätzlich das sogenannte **"First Blood"** 🩸. Eine besondere Ehre, die Ihnen nochmals **einen Boost 
                        für Ihre XPs** verpasst!"""
                    ),
                    rx.spacer(margin_bottom="10px"),

                    rx.markdown(
                        r"""Sollten Sie während dem Spiel fragen haben, stehen Ihnen **die Spielleiter gerne zur Verfügung**!"""
                    ),

                    rx.spacer(margin_bottom="10px"),
                    rx.markdown(
                        r"""Die Teams mit den **meisten Punkten gewinnen** dieses CTF-Event und werden **"Kings or Queens of the Hill"** 👑! Also 
                        viel Spaß und ran an die Flaggen 🚩!"""
                    ),
                    rx.spacer(margin_bottom="10px"),

                    # Stil der Box
                    style={
                        "maxWidth": "1400px",
                        "width": ["100%", "95%", "85%"],
                        "margin": "0 auto",
                        "padding": "5vw",
                        "borderRadius": "12px",
                        "backgroundColor": "rgba(255, 255, 255, 0.05)",
                        "backdropFilter": "blur(10px)",
                        "border": "1px solid rgba(255, 255, 255, 0.1)",
                        "boxShadow": "0 4px 8px rgba(0, 0, 0, 0.5)",
                        "boxSizing": "border-box",
                    }
                ),

                rx.spacer(),
                width="100%",
                padding_x="16px",
            ),
            style={
                "minHeight": "100vh",
                "padding": "5vw",
                "color": "#f9fafb",
                "fontFamily": "'Inter', sans-serif",
                "boxSizing": "border-box",
                "width": "100%", # hinzugefügt
                "alignItems": "center", # optional: zentriert auch vertikal
            }
        )


    def configure(self) -> None:
        #pass 
        self.url = "/spielregeln"
        self.name = "Die Spielregeln"
        self.icon = "flag"
        self.main_color = "#04B486"
        self.is_standalone = False
        self.hide_sidebar = True
        self.background_class = "black"