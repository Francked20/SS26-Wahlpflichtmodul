import reflex as rx
from pathlib import Path
import asyncio
import os

from website.engine.site import load_pages, logger as site_logger
from website.engine.tasks.meta import MetaTask


# === CSS Loader ===
def get_css_paths() -> list[str]:
    """
    Return a list of relative CSS paths for all .css files inside './assets/css',
    rewritten to be served under './css'.
    """
    css_dir = Path("./assets")
    if not css_dir.exists() or not css_dir.is_dir():
        raise FileNotFoundError(f"CSS directory not found: {css_dir.resolve()}")

    # /app/assets/css/
    return [
        str(path.relative_to(css_dir))
        for path in css_dir.rglob("*.css")
    ]


app = rx.App(
    stylesheets=get_css_paths(),
    theme=rx.theme(appearance="dark"),
    head_components=[
        # Confetti-Library laden
        rx.script(
            src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.6.0/dist/confetti.browser.min.js",
        ),
        # Globale Flags setzen
        rx.script(
            """
            window.confettiReady = true;
            window.confettiOnce = false;
            """
        ),
    ],
)


def safe_load_pages():
    loop = asyncio.get_event_loop()

    async def setup():
        # load default pages
        default_pages = os.sep.join([os.getcwd(), "website", "sites"])
        await load_pages(app, default_pages)

        if custom_paths := os.getenv("CTF_WEBSITE_FOLDER", os.sep.join(["sites", "pages"])):
            for path in custom_paths.split(":"):
                await load_pages(app, path, warn_missing_builder=True)

        if  not os.getenv("CTF_SKIP_SYNC_CHALLENGES"):
            site_logger.info("Synchronizing challenges to db...")
            await MetaTask.propagate_backend()

    if loop.is_running():
        loop.create_task(setup())
    else:
        asyncio.run(setup())


safe_load_pages()
