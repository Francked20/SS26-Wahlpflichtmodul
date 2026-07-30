"""Muster-Loeser-Panel fuer Kapitel 02 Sub-pages"""

import reflex as rx
from website.widgets.typography import code_block

SAGECELL_URL = "https://sagecell.sagemath.org/"


def muster_panel(color: str, code: str) -> rx.Component:
    """Renders the Anleitung + starter code (copyable) + SageCell button"""
    return rx.box(
        rx.hstack(
            rx.icon("terminal", size=20),
            rx.heading("Muster-Löser (SageMathCell)", size="4", color=color),
            align_items="center", spacing="2",
        ),
        rx.markdown(
            "So kommst du an die Flagge, ohne alles selbst zu programmieren:\n\n"
            "1. Öffne **SageMathCell** über den Button unten (öffnet in neuem Tab).\n"
            "2. **Kopiere den Code** unten und füge ihn in SageCell ein.\n"
            "3. Ersetze die mit `# TODO` markierten Werte durch **deine** Werte "
            "aus der heruntergeladenen Capture.\n"
            "4. Klicke in SageCell auf **Evaluate** — die Flagge erscheint unten "
            "in der Ausgabe.",
            style={"marginTop": "8px"},
        ),
        rx.box(
            code_block(code, language="python", show_lines=True),
            style={"marginTop": "12px", "maxHeight": "440px", "overflow": "auto",
                   "borderRadius": "10px"},
        ),
        rx.el.a(
            rx.hstack(
                rx.icon("external-link", size=18),
                rx.text("SageMathCell öffnen", font_weight="500"),
                align_items="center", spacing="2",
            ),
            href=SAGECELL_URL,
            target="_blank",
            rel="noopener",
            style={
                "display": "inline-flex", "margin": "12px 0 0 0",
                "padding": "10px 18px", "borderRadius": "10px",
                "background": "rgba(4, 180, 134, 0.18)",
                "border": f"1px solid {color}", "color": color,
                "textDecoration": "none", "cursor": "pointer",
            },
        ),
        style={
            "maxWidth": "1200px", "width": "100%", "margin": "16px auto",
            "padding": "20px", "borderRadius": "12px",
            "background": "rgba(180, 210, 255, 0.06)",
            "border": "1px solid rgba(255,255,255,0.14)",
            "borderLeft": f"4px solid {color}", "boxSizing": "border-box",
        },
    )
