"""
Startseite / Willkommen — die erste Seite, die beim Öffnen der App erscheint.

Keine Aufgaben: ein einladender Überblick über das gesamte CTF, die zwei
Lernpfade (Road to Diffie-Hellman & FREAK), die Lernziele und eine kurze
Anleitung. is_standalone=True -> erscheint nicht in der Seitenleiste, bleibt
aber die Landing-Page unter /challenge_01.
"""

import reflex as rx
from website.engine.site import AbstractSiteBuilder
from website.engine.task_conf import PlayerCardState
from website.engine.challenge import *
from website.unlock_settings import *

# Farben / Theme
_TEAL = "#04B486"
_CYAN = "#00FFFF"
_RED = "#E63946"
_AMBER = "#EF9F27"
_GRAD = f"linear-gradient(90deg, {_TEAL}, {_CYAN})"

_KURS_URL = "/challenge_02_kurs"


def _section_title(emoji: str, text: str) -> rx.Component:
    return rx.hstack(
        rx.text(emoji, font_size="1.4em"),
        rx.heading(text, size="6", color=_TEAL, font_family="IBM Plex Mono"),
        align_items="center", spacing="2",
        style={"margin": "40px 0 14px 0"},
    )


def _path_card(kicker: str, title: str, desc: str, items: list[str],
               accent: str) -> rx.Component:
    bg = (f"linear-gradient(135deg, rgba(4,180,134,0.10), rgba(0,255,255,0.04))"
          if accent == _TEAL else
          f"linear-gradient(135deg, rgba(230,57,70,0.10), rgba(230,57,70,0.03))")
    return rx.box(
        rx.text(kicker, style={
            "fontFamily": "IBM Plex Mono, monospace", "fontSize": "0.72rem",
            "textTransform": "uppercase", "letterSpacing": "0.08em", "opacity": "0.6"}),
        rx.heading(title, size="5", style={"margin": "6px 0 10px 0"}),
        rx.text(desc, style={"fontSize": "0.95rem", "opacity": "0.85",
                             "marginBottom": "12px"}),
        rx.unordered_list(
            *[rx.list_item(it) for it in items],
            style={"fontSize": "0.9rem", "opacity": "0.8"},
        ),
        style={
            "padding": "24px", "borderRadius": "16px", "background": bg,
            "border": "1px solid rgba(255,255,255,0.14)",
            "borderLeft": f"4px solid {accent}", "height": "100%",
            "boxSizing": "border-box",
        },
    )


def _learn_item(text: str) -> rx.Component:
    return rx.hstack(
        rx.text("▹", style={"color": _TEAL, "fontWeight": "700"}),
        rx.markdown(text),
        align_items="start", spacing="2",
        style={"fontSize": "0.95rem"},
    )


def _step(n: int, md: str) -> rx.Component:
    return rx.hstack(
        rx.box(
            rx.text(str(n), style={"fontWeight": "700", "color": "#0a0e14"}),
            style={"minWidth": "28px", "height": "28px", "borderRadius": "50%",
                   "background": _TEAL, "display": "flex", "alignItems": "center",
                   "justifyContent": "center", "flexShrink": "0"},
        ),
        rx.markdown(md),
        align_items="start", spacing="3",
        style={"padding": "14px 16px", "borderRadius": "12px",
               "background": "rgba(255,255,255,0.03)",
               "border": "1px solid rgba(255,255,255,0.08)",
               "width": "100%", "boxSizing": "border-box"},
    )


class Kapitel_01(AbstractSiteBuilder):
    PAGE_ID = "challenge_01"

    def _hero(self) -> rx.Component:
        return rx.vstack(
            rx.text("🔐", font_size="3rem"),
            rx.heading(
                "Willkommen im Krypto-CTF",
                size="9", text_align="center",
                style={"background": _GRAD, "WebkitBackgroundClip": "text",
                       "WebkitTextFillColor": "transparent", "fontWeight": "800",
                       "lineHeight": "1.15", "marginBottom": "12px"},
            ),
            rx.text(
                "Ein Hands-on-Parcours durch die Angriffe, die echte Verschlüsselung "
                "in die Knie gezwungen haben - von den Grundlagen bis zu realen "
                "TLS-Exploits.",
                text_align="center",
                style={"fontSize": "1.15rem", "opacity": "0.8", "maxWidth": "640px"},
            ),
            rx.text(
                "Capture the Flag · Angewandte Kryptografie",
                style={"marginTop": "18px", "padding": "6px 16px",
                       "border": f"1px solid rgba(4,180,134,0.4)",
                       "borderRadius": "999px", "fontFamily": "IBM Plex Mono, monospace",
                       "fontSize": "0.85rem", "color": _TEAL},
            ),
            align_items="center", spacing="1",
            style={"padding": "40px 20px 30px 20px", "borderRadius": "20px",
                   "marginBottom": "12px", "width": "100%",
                   "background": "radial-gradient(ellipse at top, rgba(4,180,134,0.12), transparent 70%)"},
        )

    def _content(self) -> rx.Component:
        return rx.vstack(
            self._hero(),

            # Worum geht's
            _section_title("👋", "Worum geht's hier?"),
            rx.markdown(
                "In diesem CTF schlüpfst du in die Rolle einer Angreiferin bzw. eines "
                "Angreifers und knackst kryptografische Verfahren - nicht mit roher "
                "Gewalt, sondern indem du ihre **Schwachstellen** verstehst und "
                "ausnutzt. Jede Challenge erzählt eine kleine Geschichte, erklärt die "
                "Theorie Schritt für Schritt und lässt dich das Gelernte sofort an "
                "einer echten Aufgabe anwenden. Am Ende jeder Aufgabe wartet eine "
                "**Flagge** im Format `crypto{…}` auf dich.",
            ),

            # Zwei Wege
            _section_title("🗺️", "Deine zwei Wege"),
            rx.grid(
                _path_card(
                    "Teil 1 · Grundlagen & Vertiefung",
                    "Road to Diffie-Hellman",
                    "Ein durchgehender Lernpfad: vom ersten Prinzip des "
                    "Schlüsselaustauschs bis zu zehn immer raffinierteren Angriffen. "
                    "Ideal zum Einsteigen und Aufbauen.",
                    ["Kleine Primzahlen & diskreter Logarithmus",
                     "Glatte Ordnungen, Pohlig-Hellman, Logjam",
                     "Man-in-the-Middle & elliptische Kurven",
                     "Invalid-Curve, ElGamal & DSA-Nonce-Angriffe"],
                    _TEAL,
                ),
                _path_card(
                    "Teil 2 · Reale TLS-Angriffe",
                    "FREAK",
                    "Hier wird's echt: du fängst echten TLS-Verkehr mit Wireshark "
                    "ab und brichst ihn - genau wie die berühmten "
                    "Export-Grade-Lücken der 1990er.",
                    ["Schwaches Diffie-Hellman (Logjam) - echter Handshake",
                     "Export Ciphers (FREAK / RSA-Export)",
                     "Faktorisieren mit yafu, TLS Master Secret knacken",
                     "Die Flagge aus dem entschlüsselten Verkehr ziehen"],
                    _RED,
                ),
                columns=rx.breakpoints(initial="1", sm="2"),
                spacing="4", width="100%",
            ),

            # Lernziele
            _section_title("🎓", "Das nimmst du mit"),
            rx.grid(
                _learn_item("Wie Diffie-Hellman, RSA, ElGamal und DSA **wirklich** funktionieren"),
                _learn_item("Warum **schlechte Parameter** ein sicheres Verfahren wertlos machen"),
                _learn_item("Den diskreten Logarithmus per **Pohlig-Hellman** & BSGS brechen"),
                _learn_item("Echten **TLS-Handshake** in Wireshark lesen und analysieren"),
                _learn_item("Werkzeuge wie **yafu** und **SageMath** praktisch einsetzen"),
                _learn_item("Warum ein wiederverwendeter **Nonce** ganze Schlüssel verrät"),
                columns=rx.breakpoints(initial="1", sm="2"),
                spacing="3", width="100%",
            ),

            # Anleitung
            _section_title("🚀", "So gehst du vor"),
            rx.vstack(
                _step(1, "**Fang links an.** Öffne in der Seitenleiste den Bereich "
                         "*Road to Diffie-Hellman* und beginne beim **Kurs** - dort "
                         "lernst du die Grundlagen, die du danach brauchst."),
                _step(2, "**Lies die Theorie.** Jede Challenge erklärt zuerst das "
                         "Konzept und den Angriff. Nimm dir die Zeit - das Verständnis "
                         "ist der halbe Weg zur Flagge."),
                _step(3, "**Klapp die Schritt-für-Schritt-Lösung auf**, wenn du "
                         "praktisch loslegen willst. Dort stehen die konkreten "
                         "Befehle (SageMath, yafu, Python)."),
                _step(4, "**Finde die Flagge** im Format `crypto{…}` und trage sie ein. "
                         "Richtig? Dann schaltet sich die nächste Challenge frei."),
                _step(5, "**Stuck?** Jede Aufgabe hat gestaffelte **Hinweise** - sie "
                         "kosten ein paar Punkte, bringen dich aber weiter."),
                spacing="3", width="100%",
            ),

            rx.box(
                rx.markdown(
                    "**Tipp:** Die Challenges bauen aufeinander auf und schalten sich "
                    "der Reihe nach frei. Arbeite sie am besten von oben nach unten "
                    "durch - so ergibt jede neue Technik logisch Sinn."
                ),
                style={"margin": "18px 0", "padding": "12px 16px", "borderRadius": "10px",
                       "background": "rgba(239,159,39,0.08)",
                       "borderLeft": f"4px solid {_AMBER}", "width": "100%",
                       "boxSizing": "border-box"},
            ),

            # CTA
            rx.vstack(
                rx.text("Bereit? Deine erste Flagge wartet.",
                        style={"fontSize": "1.2rem", "fontWeight": "600"}),
                rx.text("Starte mit dem Kurs im Bereich „Road to Diffie-Hellman\".",
                        style={"opacity": "0.75"}),
                rx.link(
                    rx.button(
                        rx.icon(tag="arrow-big-right"),
                        "Los geht's",
                        size="3",
                        style={"background": _GRAD, "color": "#0a0e14",
                               "fontWeight": "700", "borderRadius": "999px",
                               "marginTop": "14px"},
                    ),
                    href=_KURS_URL,
                ),
                align_items="center", spacing="1",
                style={"textAlign": "center", "margin": "40px 0 10px 0", "padding": "28px",
                       "borderRadius": "16px", "background": "rgba(4,180,134,0.08)",
                       "border": f"1px solid rgba(4,180,134,0.3)", "width": "100%",
                       "boxSizing": "border-box"},
            ),

            spacing="2", width="100%",
            style={"maxWidth": "1000px", "margin": "0 auto", "padding": "20px"},
            align_items="stretch",
        )

    def page(self) -> rx.Component:
        return rx.vstack(
            rx.cond(
                CondState.is_ready & PlayerCardState.update_day_ready[1],
                rx.cond(
                    CondState.event_enabled,
                    self._content(),
                    rx.vstack(
                        self._hero(),
                        rx.box(
                            rx.markdown(
                                "**Das Event ist noch nicht gestartet.** Bitte warte, "
                                "bis der Spielleiter das Event für alle Teilnehmer "
                                "freischaltet - dann geht es hier los!"
                            ),
                            style={"maxWidth": "700px", "margin": "20px auto",
                                   "padding": "20px", "borderRadius": "12px",
                                   "background": "rgba(239,159,39,0.08)",
                                   "borderLeft": f"4px solid {_AMBER}",
                                   "textAlign": "center"},
                        ),
                        width="100%", align_items="center",
                    ),
                ),
                rx.vstack(rx.spinner(), align_items="center",
                          style={"marginTop": "80px", "width": "100%"}),
            ),
            width="100%",
        )

    def configure(self) -> None:
        self.url = "/challenge_01"
        self.name = "Willkommen"
        self.icon = "house"
        self.main_color = _TEAL
        self.is_standalone = True   # nicht in der Seitenleiste, aber Landing-Page
        self.hide_sidebar = False
        self.on_load = [
            CondState.reset_check_status,
            CondState.do_checks,
            CondState.do_check_cyberrange,
            PlayerCardState.update_day(1),
        ]
        self.background_class = "black"
        self.auth_required = True
        self.unlock_day = unlock_always