import os
import asyncio

import reflex as rx
import reflex_chakra as rc

from website.logger import create_logger
from website.auth_lib import BackendRequests, AuthCookie, PageAuthState

# from fastapi.encoders import jsonable_encoder
from urllib.parse import quote

enable_cyber_range = os.getenv("ENABLE_CYBER_RANGE", "False").lower() == "true"

logger = create_logger("task-engine")

class AccordionState(rx.State):
    accordion_index: dict[str, list[list[int]]] = {}

    def init(self, page_id: str, count: int):
        if page_id not in self.accordion_index:
            self.accordion_index[page_id] = [[0] for _ in range(count)]

    def toggle(self, page_id: str, idx: int):
        current = self.accordion_index[page_id][idx]
        self.accordion_index[page_id][idx] = [] if current == [0] else [0]

def render_task(page_id: str, idx: int, title: str, widget):
    return rc.accordion(
        rc.accordion_item(
            rc.accordion_button(
                rc.heading(
                    title,
                    size="sm",
#                    font_family="IBM Plex Sans",
#                    font_weight="600",
                ),
                rc.accordion_icon(),
                on_click=lambda: AccordionState.toggle(page_id, idx),
            ),
            rc.accordion_panel(widget),
        ),
        index=AccordionState.accordion_index[page_id][idx],
        allow_toggle=True,
        allow_multiple=True,
        width="100%",
    )

class PlayerCardState(AuthCookie, BackendRequests):
    initialized: bool = False
    challenges: int = -1
    max_challenges: int = -1
    percent: int = 0
#    badges: str = ""
    badges: list[dict] = []
    team_name: str = ""
    team_color: str = "rgba(14, 30, 37, 0.65)"
    team_mode: bool = False
    team_leader_mode: bool = False
    show_answers: bool = False
    allow_task_reset: bool = False

    enable_test_mode: bool | None = None

    tasks_solved: dict[str, bool] = {}
    update_day_ready: dict[int, bool] = {}

    enable_badges: bool = False
    enable_player_levels: bool = False
    player_points: int = 0
    player_level: int = 1
    player_rank: str = ""
    level_percent: int = 0

    enable_confetti: bool = False
    enable_toast: bool = False

    remaining_points: int = 0
    current_points: int = 0
    next_level_points: int = 0
    level_up_trigger: bool = False
    rank_names: list[str] = []
    rank_thresholds: list[int] = []
    _points_per_level: int = 500

    toast_old_level: int = 0
    toast_new_level: int = 0

    @rx.var
    def badge_indices(self) -> list[int]:
        return list(range(len(self.badges)))

    @rx.var
    def badge_emojis_text(self) -> list[str]:
        # erzwinge str, falls mal None auftaucht
        return [str(b.get("emoji", "")) for b in self.badges]

    @rx.var
    def badge_tooltips_text(self) -> list[str]:
        return [str(b.get("tooltip", "")) for b in self.badges]

    async def set_old_level(self):

        if not self.enable_player_levels:
            return

        """Merkt sich das aktuelle Level aus dem Backend"""
        safe_username = quote(self.get_username, safe="")
        try:
            resp_lvl = await self.get(f"/user/{safe_username}/level")
            data = resp_lvl.json()
            self.toast_old_level = int(data.get("level", 1))
        except Exception as e:
            logger.warning(f"[PlayerCardState] set_toast_old_level failed: {e}")
            self.toast_old_level = self.player_level  # Fallback: lokaler Wert

    async def check_new_level(self):
        if not self.enable_player_levels:
            return

        """Merkt sich das potentiell neue Level aus dem Backend"""
        safe_username = quote(self.get_username, safe="")
        try:
            resp_lvl = await self.get(f"/user/{safe_username}/level")
            data = resp_lvl.json()
            self.toast_new_level = int(data.get("level", 1))
            new_player_rank = str(data.get("rank", "")) or ""

            # Beschreibungstext (zweite Zeile)
            desc = f"Level: {self.toast_new_level}"
            if new_player_rank != "":
                desc += f" | Rang: {new_player_rank}"  # Zeilenumbruch ist optional; Radix trennt ohnehin Titel/Beschreibung

            if self.enable_toast:

                if self.toast_new_level > self.toast_old_level:
                    return rx.toast.success(
                        f"🎉 Level-Up!",
                        description=desc,
                        duration=5000,
                        close_button=True,
                    )
# DEBUG only - this can only happen in Allow Task Reset Modes:
                if self.toast_new_level < self.toast_old_level:
                    return rx.toast.warning(
                        f"⚠️ Level-Down!",
                        description=desc,
                        duration=5000,
                        close_button=True,
                    )

        except Exception as e:
            logger.warning(f"[PlayerCardState] set_toast_new_level failed: {e}")
            self.toast_new_level = self.player_level  # Fallback: lokaler Wert

#    def reset_confetti(self):
#        # State-Flag zurücksetzen
#        self.level_up_trigger = False
#        # globales JS-Flag zurücksetzen
#        return rx.script("window.confettiOnce = false;")

    def reset_confetti(self):
        self.level_up_trigger = False
        return rx.call_script("window.confettiOnce = false;")


#    def _compute_next_level_info(self) -> None:
#        """Gibt (remaining_points, current_points, next_level_points) zurück"""
#        current_points = max(0, int(self.player_points or 0))
#        ppl = max(1, int(self._points_per_level or 500))
#        next_level_points = self.player_level * ppl
#        remaining = max(0, next_level_points - current_points)
#        self.remaining_points = remaining
#        self.current_points = current_points
#        self.next_level_points = next_level_points

    def _compute_next_level_info(self) -> None:
        points = max(0, int(self.player_points or 0))

        # Threshold-basierte Logik
        if self.rank_thresholds and len(self.rank_thresholds) == len(self.rank_names) - 1:
            thresholds = self.rank_thresholds

            # Level bestimmen
            level = 1
            for t in thresholds:
                if points >= t:
                    level += 1
                else:
                    break

            # Basis- und Zielpunkte
            if level == 1:
                base = 0
                next_ = thresholds[0]
            elif level - 2 < len(thresholds):
                base = thresholds[level - 2]
                next_ = thresholds[level - 1]
            else:
                base = thresholds[-1]
                next_ = base + (thresholds[-1] - thresholds[-2])

            self.current_points = points - base
            self.next_level_points = next_ - base
            self.remaining_points = max(0, next_ - points)
            return

        # Fallback: linear
        ppl = max(1, int(self._points_per_level or 500))
        next_level_points = self.player_level * ppl
        remaining = max(0, next_level_points - points)

        self.remaining_points = remaining
        self.current_points = points
        self.next_level_points = next_level_points


#    def _compute_level_from_points_dynamic(self) -> None:
#        """
#        Berechnet player_level & level_percent aus player_points anhand der konfigurierten
#        Punkte-pro-Level (linear). Robust gegen leere/ungültige Werte
#        """
#        points = max(0, int(self.player_points or 0))
#        ppl = max(1, int(self._points_per_level or 500))
#
#        # Level 1 startet bei 0 Punkten; linear
#        level = max(1, points // ppl + 1)
#        base = (level - 1) * ppl
#        next_ = level * ppl
#        denom = max(1, next_ - base)
#        percent = int(100 * (points - base) / denom)
#
#        self.player_level = level
#        self.level_percent = max(0, min(100, percent))

    def _compute_level_from_points_dynamic(self) -> None:
        """Berechnet Level & Prozent, linearer Fallback ohne Thresholds"""
        points = max(0, int(self.player_points or 0))

        # Wenn Thresholds existieren → thresholds-basierte Level-Logik
        if self.rank_thresholds and len(self.rank_thresholds) == len(self.rank_names) - 1:
            thresholds = self.rank_thresholds

            # Level bestimmen
            level = 1
            for t in thresholds:
                if points >= t:
                    level += 1
                else:
                    break

            # Progressbar bestimmen
            if level == 1:
                base = 0
                next_ = thresholds[0]
            elif level - 2 < len(thresholds):
                base = thresholds[level - 2]
                next_ = thresholds[level - 1]
            else:
                base = thresholds[-1]
                next_ = base + (thresholds[-1] - thresholds[-2])

            percent = int(100 * (points - base) / max(1, next_ - base))

            self.player_level = level
            self.level_percent = max(0, min(100, percent))
            return

        # Fallback: linear
        ppl = max(1, int(self._points_per_level or 500))
        level = max(1, points // ppl + 1)
        base = (level - 1) * ppl
        next_ = level * ppl
        percent = int(100 * (points - base) / max(1, next_ - base))

        self.player_level = level
        self.level_percent = max(0, min(100, percent))

    def _compute_rank_from_points_dynamic(self) -> None:
        points = max(0, int(self.player_points or 0))

        # Wenn Thresholds gesetzt sind → nutze sie
        if self.rank_thresholds and len(self.rank_thresholds) == len(self.rank_names) - 1:
            thresholds = self.rank_thresholds
            names = self.rank_names
        else:
            # Keine Thresholds → nur Levelsystem, keine Ränge
            self.player_rank = ""
            return

        idx = 0
        for t in thresholds:
            if points >= t:
                idx += 1
            else:
                break
        idx = min(idx, len(names) - 1)
        self.player_rank = names[idx]

    async def update_levels(self) -> None:
        """Laedt Feature-Flag + Leveldaten, Fallback auf lokale Berechnung"""
        if not self.enable_player_levels:
            return
        
        events = []
        
        if self.enable_confetti:
            events.append(self.reset_confetti())
            #self.reset_confetti()

        old_level = self.player_level

#        # 1) Feature-Flag laden
#        try:
#            resp_flag = await self.get("/admin/event/player_levels_mode")
#            self.enable_player_levels = bool(resp_flag.json().get("player_levels_mode", False))
#        except Exception as e:
#            logger.warning(f"[PlayerCardState] fetch player_levels_mode failed: {e}")
#            self.enable_player_levels = False
#
#        # Wenn das Feature nicht aktiv ist, keine weiteren Leveldaten nötig
#        if not self.enable_player_levels:
#            return
#
#        # 2) Rank-Config laden und im State cachen
#        try:
#            resp_cfg = await self.get("/admin/event/get_rank_config")
#            cfg = resp_cfg.json()
#            self.rank_names = cfg.get("rank_names", []) or []
#            self.rank_thresholds = cfg.get("rank_thresholds", []) or []
#            ppl = int(cfg.get("points_per_level", 500) or 500)
#            self._points_per_level = max(1, ppl)
#        except Exception as e:
#            logger.info(f"[PlayerCardState] fetch rank config failed, using fallback: {e}")
#            self.rank_names = []
#            self.rank_thresholds = []
#            self._points_per_level = 500

        # 3) Leveldaten des Users laden
        safe_username = quote(self.get_username, safe="")
        try:
            resp_lvl = await self.get(f"/user/{safe_username}/level")
            data = resp_lvl.json()
            self.player_points = int(data.get("points", 0))
            self.player_rank = str(data.get("rank", ""))
            self.player_level = int(data.get("level", 1))
            self.level_percent = int(data.get("level_percent", 0))

            self._compute_next_level_info()
        except Exception as e:
            logger.info(f"[PlayerCardState] fetch user level failed, falling back to local calc: {e}")

            # Fallback: Punkte via /score, Rest lokal DYNAMISCH berechnen
            try:
                resp_score = await self.get(f"/user/{safe_username}/score")
                s = resp_score.json()
                self.player_points = int(s.get("points", 0))
            except Exception as e2:
                logger.warning(f"[PlayerCardState] fetch score failed for level fallback: {e2}")
                self.player_points = 0

            # Dynamische Berechnungen anhand der (geladenen) Config
            self._compute_level_from_points_dynamic()
            self._compute_rank_from_points_dynamic()
            self._compute_next_level_info()

        if not self.initialized:
            # erster Aufruf → nur initialisieren, kein Confetti
            self.initialized = True
            return

        # 4) Level-Up prüfen
        if self.enable_confetti:
            if self.player_level > old_level:
                self.level_up_trigger = True

        return events

    @rx.event
    async def reset_day_ready(self, day: int):
        self.update_day_ready[day] = False
        await self.update_day(day)

    async def reset_day(self, day: int):
        safe_username = quote(self.username, safe="")
        response = await self.get(f"/user/{safe_username}/reset_challenges_data/{day}",auth=self.auth_cookie)

        await self.reset_day_ready(day)

    @rx.event(background=True)
    async def update_each_page(self):
        if self.enable_test_mode is None:
            response = await self.get("/admin/event/enable_test_mode")
            status = response.json()

            async with self:
                self.enable_test_mode = status["enable_test_mode"]

    async def update_on_first_load(self):
        safe_username = quote(self.get_username, safe="")

        response = await self.get("/admin/event/show_answers_mode")
        status = response.json()
        self.show_answers = status["show_answers"]

        response = await self.get("/admin/event/allow_task_reset_mode")
        status = response.json()
        self.allow_task_reset = status["allow_task_reset"]

        response = await self.get("/admin/event/enable_test_mode")
        status = response.json()
        self.enable_test_mode = status["enable_test_mode"]

        response = await self.get("/admin/event/teamevent_mode")
        status = response.json()
        team_event_mode: bool = status["teamevent_mode"]
        self.team_mode = team_event_mode

        response = await self.get("/admin/event/badges_mode")
        status = response.json()
        event_with_badges: bool = status["badges_mode"]
        self.enable_badges = event_with_badges

        response = await self.get("/admin/event/player_levels_mode")
        status = response.json()
        event_with_player_levels: bool = status["player_levels_mode"]
        self.enable_player_levels = event_with_player_levels

        if(event_with_player_levels):

            try:
                resp_cfg = await self.get("/admin/event/get_rank_config")
                cfg = resp_cfg.json()
                self.rank_names = cfg.get("rank_names", []) or []
                self.rank_thresholds = cfg.get("rank_thresholds", []) or []
                ppl = int(cfg.get("points_per_level", 500) or 500)
                self._points_per_level = max(1, ppl)
            except Exception as e:
                logger.info(f"[PlayerCardState] fetch rank config failed, using fallback: {e}")
                self.rank_names = []
                self.rank_thresholds = []
                self._points_per_level = 500

            response = await self.get("/admin/event/confetti_mode")
            status = response.json()
            event_with_confetti: bool = status["confetti"]
            self.enable_confetti = event_with_confetti

            response = await self.get("/admin/event/toast_mode")
            status = response.json()
            event_with_toast: bool = status["toast"]
            self.enable_toast = event_with_toast

        if(team_event_mode):

            response = await self.get("/admin/event/teamevent_leader_mode")
            status = response.json()
            team_event_leader_mode: bool = status["teamevent_leader_mode"]
            self.team_leader_mode = team_event_leader_mode

            response = await self.get(f"/user/{safe_username}/get_team_info")

# Not needed any longer?
#            if(team_event_leader_mode):
#                data = response.json().get("team_leader_name", None)
#                if data is not None:
#                    username: str = str(data)
#                    safe_username = quote(username, safe="")

            data = response.json()
            self.team_name = data["team_name"]
            self.team_color = data["team_color"]

# Init all challenges:
        await self.post(f"/user/{safe_username}/initialize_challenges",auth=self.auth_cookie)

        response1 = await self.get(f"/user/{safe_username}/score")
        response2 = await self.get("/challenges/all_ch_data")
        data1 = response1.json()
        data2 = response2.json()
        self.challenges = data1["challenges"]
        self.max_challenges = data2["challenges"]

        if(event_with_badges):
#            response3 = await self.get(f"/user/{safe_username}/badges")
#            data3 = response3.json()
#            self.badges = data3["badges"]
            response3 = await self.get(f"/user/{safe_username}/badges")
            data3 = response3.json()
            self.badges = data3.get("badges", [])

        try:
            self.percent = min(round(self.challenges / self.max_challenges * 100), 100)
        except ZeroDivisionError:
            self.percent = 0

        # Fetch the data from your endpoint
        response = await self.get(f"/user/{safe_username}/tasks_solved")
        data = response.json()
        # Dynamisch speichern
        for key, value in data.items():
            self.tasks_solved[key] = value

        #await self.update_levels()
        events = await self.update_levels()
        return events

    @rx.event
    async def update_day(self, day: int):

        if self.update_day_ready.get(day, False):
            return  # Guard: schon geladen

        self.update_day_ready[day] = True

        safe_username = quote(self.get_username, safe="")

        response1, response2, response3 = await asyncio.gather(
            self.get(f"/user/{safe_username}/score"),
            self.get("/challenges/all_ch_data"),
            self.get(f"/user/{safe_username}/badges")
        )

        data1 = response1.json()
        data2 = response2.json()
        data3 = response3.json()

        self.challenges = data1["challenges"]
        self.max_challenges = data2["challenges"]
#        self.badges = data3["badges"]
        self.badges = data3.get("badges", [])

        try:
            self.percent = min(round(self.challenges / self.max_challenges * 100), 100)
        except ZeroDivisionError:
            self.percent = 0

        # Fetch the data from your endpoint
        response = await self.get(f"/user/{safe_username}/tasks_solved/{day}")
        data = response.json()

        for key, value in data.items():
            self.tasks_solved[key] = value

        events = await self.update_levels()

        return events
