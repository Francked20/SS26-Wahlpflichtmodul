import os
import reflex as rx
import logging
import json

from website.auth_lib import BackendRequests, AuthCookie, PageAuthState
from urllib.parse import quote
from rxconfig import production_mode

enable_cyber_range = os.getenv("ENABLE_CYBER_RANGE", "False").lower() == "true"

def button_overlay_hover(
    x: str,
    y: str,
    label: str,
    info: str = None,
    font_size: str = "1em",
    label_font_size: str = "1em",
    label_color: str = "white",
    info_color: str = "black",
    content_bg: str = "white",
    content_border_color: str = "black",
    button_width: str = None,
    button_height: str = None,
    z_index: int = 10,
    hover_enabled: bool = True,
    minimal_style: bool = False,
):
    base_style = {
        "position": "absolute",
        "top": y,
        "left": x,
        "z_index": z_index,
        "font_size": label_font_size,
        "white_space": "nowrap",
        "overflow": "hidden",
        "text_overflow": "ellipsis",
    }

    if button_width:
        base_style["width"] = button_width
    if button_height:
        base_style["height"] = button_height

    if not hover_enabled:
        return rx.text(
            label,
            color=label_color,
            bg="rgba(0,0,0,0.6)",
            padding="0.5em",
            border_radius="5px",
            **base_style
        )

    button_style = {
        **base_style,
        "color": label_color,
        "_hover": {"bg": "rgba(0,0,0,0.8)"},
    }

    if minimal_style:
        button_style["bg"] = "transparent"
        button_style["_hover"] = {}
    else:
        button_style["bg"] = "rgba(0,0,0,0.6)"
        button_style["padding"] = "0.5em"
        button_style["border_radius"] = "5px"

    return rx.hover_card.root(
        rx.hover_card.trigger(
            rx.button(
                label,
                **button_style
            )
        ),
        rx.hover_card.content(
            rx.markdown(info, color=info_color, font_size=font_size),
            bg=content_bg,
            padding="1em",
            border_radius="5px",
            box_shadow="lg",
            border=f"2px solid {content_border_color}",
        ),
    )

class CondState(AuthCookie, BackendRequests):
    event_enabled: bool = False
    team_event_mode: bool = False
    team_event_leader_mode: bool = False
    team_leader: bool = False
    username: str = "??"
    is_ready: bool = False
    code_server_running: bool = False
    code_server_domain: str = ""
    kali_server_running: bool = False
    kali_server_domain: str = ""

    cyber_range_running: bool = False
    cyber_range_exists: bool = False
    cyber_range_busy: bool = False
    cyber_range_stopped: bool = False
    cyber_range_domain: str = ""
    cyber_range_user: str = ""
    cyber_range_password: str = ""
    cyber_range_message: str = ""

    async def reset_check_status(self):
        self.is_ready = False

    async def do_checks(self):
        # local dev mode
        if not production_mode:
            self.is_ready = True
            self.event_enabled = True
            return

        if self.is_ready:
            return

        response = await self.get("/admin/event/status")
        status = response.json()
        self.event_enabled = status["enabled"]

        if (status["enabled"]):

            response = await self.get("/admin/event/teamevent_mode")
            status = response.json()
            self.team_event_mode = status["teamevent_mode"]

            if (status["teamevent_mode"]):

                response = await self.get("/admin/event/teamevent_leader_mode")
                status = response.json()
                self.team_event_leader_mode = status["teamevent_leader_mode"]

                if (status["teamevent_leader_mode"]):

                    safe_username = quote(self.get_username, safe="")
                    response = await self.get(f"/user/{safe_username}/team_leader")
                    status = response.json()
                    self.team_leader = status["team_leader"]

        await self.status_code_server()
        await self.status_kali_server()

#        if(enable_cyber_range):
#            await self.status_cyber_range()

        self.is_ready = True

    async def do_check_cyberrange(self):
        if(enable_cyber_range):
            await self.status_cyber_range()

    async def status_cyber_range(self):
        response = await self.get("/cyberrange/status", auth=self.auth_cookie)

        if response.status_code != 200:
            logging.warning(f"Failed to fetch status: {response.status_code}, {response.text}")
            return

        data = response.json()

        self.cyber_range_running = data.get("running", False)
        self.cyber_range_exists = data.get("exists", False)
        self.cyber_range_busy = data.get("busy", False)
        self.cyber_range_stopped = data.get("stopped", False)

        self.cyber_range_domain = data.get("url", "")
        self.cyber_range_user = data.get("user", "")
        self.cyber_range_password = data.get("password", "")

        self.cyber_range_message = data.get("message", "")

    async def reset_cyber_range(self):
        response = await self.post("/cyberrange/reset", auth=self.auth_cookie)

        if response.status_code == 200:
#            data = response.json()
            # Optional: Logging
#            print("Cyber Range reset:", data)

            self.cyber_range_running = False
            self.cyber_range_exists = False
            self.cyber_range_busy = True
            self.cyber_range_stopped = False

#            # Nach Reset Status neu laden
#            await self.status_cyber_range()
        else:
            logging.warning(
                f"Failed to reset cyber range: {response.status_code}, {response.text}"
            )

    async def custom_toast(self, title: str, description: str):
        return rx.toast.success(
            title,
            description=description,
            duration=5000,
            close_button=True,
        )

    async def cyber_range_user_toast(self):
        return rx.toast.info(
            f"Info",
            description="Benutzername in Zwischenablage kopiert",
            duration=5000,
            close_button=True,
        )

    async def cyber_range_pw_toast(self):
        return rx.toast.info(
            f"Info",
            description="Passwort in Zwischenablage kopiert",
            duration=5000,
            close_button=True,
        )

    async def status_code_server(self):
        response = await self.get("/container/code/status", auth=self.auth_cookie)
        if response.status_code == 200:
            self.code_server_running = response.json()["running"]
            self.code_server_domain = response.json().get("url") or ""
        else:
            logging.warning(f"Failed to fetch status: {response.status_code}, {response.text}")

    async def start_code_server(self):
        response = await self.post("/container/code/start", auth=self.auth_cookie)
        if response.status_code == 200:
            self.code_server_running = True
            self.code_server_domain = response.json().get("url") or ""
        else:
            logging.warning(f"Failed to start code server: {response.status_code}, {response.text}")
            return rx.toast.error("Fehler beim Starten von VSCode. Versuch es später nochmal.")

    async def stop_code_server(self):
        response = await self.post("/container/code/stop", auth=self.auth_cookie)
        if response.status_code == 200:
            self.code_server_running = False
            self.code_server_domain = ""
        else:
            logging.warning(f"Failed to stop code server: {response.status_code}, {response.text}")
            return rx.toast.error("Fehler beim Stoppen von VSCode. Versuch es später nochmal.")

#    async def inject_challenge(self, day: int, task: int, challenge_index: int):
#        response = await self.post(
#            "/container/code/inject_challenge",
#            params={
#                "day": day,
#                "task": task,
#                "challenge_index": challenge_index,
#            },
#            auth=self.auth_cookie,
#        )
#        if response.status_code == 200:
#            logging.info(f"Challenge {day}-{task}-{challenge_index} injected successfully")
#            return rx.toast.success(
#                f"Challenge wurde in den VSCode Container kopiert.",
#                duration=5000,
#                close_button=True,
#            )
#        elif response.status_code == 409:
#            logging.info(f"Challenge {day}-{task}-{challenge_index} recently injected")
#            return rx.toast.info(
#                f"Challenge wurde erst kürzlich kopiert. Cooldown aktiv!",
#                duration=5000,
#                close_button=True,
#            )
#        else:
#            logging.warning(
#                f"Failed to inject challenge {day}-{task}-{challenge_index}: "
#                f"{response.status_code}, {response.text}"
#            )
#            return rx.toast.error(
#                f"Kopieren der Challenge fehlgeschlagen!",
#                duration=5000,
#                close_button=True,
#            )

    async def inject_challenge(self, day_id: int, task_id: int, challenge_index: int):
        return await self.inject_challenge_pvc(day_id, task_id, challenge_index)

    async def inject_challenge_pvc(self, day_id: int, task_id: int, challenge_index: int):
        response = await self.post(
            "/container/code/inject_challenge_pvc",
            params={
                "day_id": day_id,
                "task_id": task_id,
                "challenge_index": challenge_index,
            },
            auth=self.auth_cookie,
        )

        if response.status_code == 200:
            logging.info(f"Challenge PVC {day_id}-{task_id}-{challenge_index} injected successfully")

            extend_resp = await self.post(
                "/container/code/extend",
                auth=self.auth_cookie,
            )
            if extend_resp.status_code == 200:
                logging.info("VSCode Container TTL erfolgreich verlängert")
                return rx.toast.success(
                    f"Challenge wurde in den VSCode Container kopiert.",
                    duration=5000,
                    close_button=True,
                )
            else:
                logging.warning(f"TTL-Extend fehlgeschlagen: {extend_resp.status_code}, {extend_resp.text}")
                return rx.toast.warning(
                    f"Challenge kopiert, aber TTL konnte nicht verlängert werden.",
                    duration=5000,
                    close_button=True,
                )

        elif response.status_code == 409:
            logging.info(f"Challenge PVC {day_id}-{task_id}-{challenge_index} recently injected")
            return rx.toast.info(
                f"Challenge wurde erst kürzlich kopiert. Cooldown aktiv!",
                duration=5000,
                close_button=True,
            )
        else:
            logging.warning(
                f"Failed to inject challenge PVC {day_id}-{task_id}-{challenge_index}: "
                f"{response.status_code}, {response.text}"
            )
            return rx.toast.error(
                f"Kopieren der Challenge fehlgeschlagen!",
                duration=5000,
                close_button=True,
            )


    # Kali Linux now
    async def status_kali_server(self):
        response = await self.get("/container/kali/status", auth=self.auth_cookie)
        if response.status_code == 200:
            self.kali_server_running = response.json()["running"]
            logging.info(f"Status running: {self.kali_server_running}")
            self.kali_server_domain = response.json().get("url") or ""
            logging.info(f"Status domain: {self.kali_server_domain}")
        else:
            logging.warning(f"Failed to fetch kali status: {response.status_code}, {response.text}")
    
    async def start_kali_server(self):
        response = await self.post("/container/kali/start", auth=self.auth_cookie)
        if response.status_code == 200:
            logging.info("starting kali server")
            self.kali_server_running = True
            self.kali_server_domain = response.json().get("url") or ""
            logging.info(f"{self.kali_server_domain}")
        else:
            logging.warning(f"Failed to start kali server: {response.status_code}, {response.text}")
            return rx.toast.error("Fehler beim Starten von Kali. Versuch es später nochmal.")

    async def stop_kali_server(self):
        response = await self.post("/container/kali/stop", auth=self.auth_cookie)
        if response.status_code == 200:
            logging.info("stopping kali server")
            self.kali_server_running = False
            self.kali_server_domain = ""
        else:
            logging.warning(f"Failed to stop kali server: {response.status_code}, {response.text}")
            return rx.toast.error("Fehler beim Stoppen von Kali. Versuch es später nochmal.")
