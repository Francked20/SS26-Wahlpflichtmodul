import logging
import os
from pathlib import Path

import reflex as rx
from dotenv import load_dotenv

from .modules.scoreboard import main_table
from .modules.websocket_reader import ScoreBoardState

# === Environment Setup ===
load_dotenv()

log_level = os.getenv("LOG_LEVEL", "INFO").upper()
numeric_level = getattr(logging, log_level, logging.INFO)
logging.basicConfig(level=numeric_level, force=True)
logging.info(f"Logging initialized at {log_level} level.")


def get_css_paths() -> list[str]:
    css_dir = Path("./assets")
    if not css_dir.exists() or not css_dir.is_dir():
        raise FileNotFoundError(f"CSS directory not found: {css_dir.resolve()}")

    return [
        str(path.relative_to(css_dir))
        for path in css_dir.rglob("*.css")
    ]


# === Reflex App ===
app = rx.App(
    stylesheets=get_css_paths(),
    theme=rx.theme(appearance="dark"),
)

# === Main Page ===
app.add_page(
    main_table,  # <— WICHTIG: Funktion, nicht main_table()
    route="/",
    title="TCV CTF Scoreboard",
    description="Scoreboard for the TCV CTF competition.",
    image="./assets/favicon.ico",
    # alt
    #on_load=[ScoreBoardState.check_team_event, ScoreBoardState.get_states],
    # neu
    # TODO: check_team_event wird nun in websocket_reader.py Datei intern aufgerufen
    # Race Condition wird so verhindert!
    on_load=[ScoreBoardState.get_states],
)

logging.info("Created scoreboard app.")
