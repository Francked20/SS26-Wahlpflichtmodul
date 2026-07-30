import asyncio
import typing
import urllib.parse
import json
import logging
import os

import httpx
import reflex as rx
import websockets
from websockets.exceptions import (
    ConnectionClosed,
    ConnectionClosedError,
    ConnectionClosedOK,
)

# TODO: alten Import von legacy entfernen und durch neuen ersetzen!
# from websockets.legacy.client import WebSocketClientProtocol

# TODO: neu 
# Websocket migration auf 15.0.1 
from websockets import WebSocketClientProtocol

# TODO: logging.INFO hardcoded --> Anzeige der logging.DEBUG so nicht möglich
#logging.basicConfig(
#    level=logging.INFO,
#    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
#    handlers=[logging.StreamHandler()],
#)

# TODO: 
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),  # ← aus .env
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)

api_url = "http://api:8000"
websocket_url = f"ws://api:8000"


class BackendRequests:

    def build_url(self, path: str, **params: typing.Any) -> str:
        query = "&".join(
            [urllib.parse.urlencode({k: v}) for k, v in params.items()]
        )
        return f"{api_url}{path}{'?' if params else ''}{query}"

    @staticmethod
    def _get_headers(auth: typing.Optional[str]) -> dict:
        headers: dict = {
            "accept": "application/json",
            "Content-Type": "application/json",
        }
        if auth:
            headers |= {"Authorization": f"Bearer {auth}"}
        return headers

    async def get(
        self,
        path: str,
        params: typing.Optional[dict] = None,
        auth: typing.Optional[str] = None,
    ) -> httpx.Response:
        headers = self._get_headers(auth)
        async with httpx.AsyncClient(timeout=3, headers=headers) as client:
            return await client.get(self.build_url(path, **(params or {})))

    async def post(
        self,
        path: str,
        params: typing.Optional[dict] = None,
        auth: typing.Optional[str] = None,
    ) -> httpx.Response:
        headers = self._get_headers(auth)
        async with httpx.AsyncClient(timeout=3, headers=headers) as client:
            return await client.post(self.build_url(path), json=params)

    async def delete(self):
        ...

# TODO: loop entfernen!
# loop = asyncio.get_event_loop()
# url = f"wss://{os.getenv('API_DOMAIN')}"


class EventHolders:
    mapping_ws: dict[str, WebSocketClientProtocol] = {}  # {token: Websocket}
    # TODO: Hier wird die IP als Mapping verwendet, wird aktuell auf Session_ID umgestellt
    #mapping_ip: dict[str, str] = {}  # {ip: token}
    # TODO: Auf Verwendung der Session_ID zurückgreifen, um Kollisionen der Nutzer zu verhindern
    mapping_sid: dict[str, str] = {}   
    # TODO: neu Cancellation-Flag
    mapping_active: dict[str, bool] = {}

    # TODO: Hier wird die IP zum mappen verwendet, aktuell wird auf Session_ID gemappt
    #async def start_stream(self, token: str, ip: str):
    #    # Falls IP schon verbunden → alte Verbindung schließen
    #    if ip in self.mapping_ip:
    #        old_token = self.mapping_ip[ip]
    #        if old_token in self.mapping_ws:
    #            await self.mapping_ws[old_token].close()

    #    self.mapping_ip[ip] = token
    #    # neu
    #    # TODO: Cancellation-Flag ergänzen -> Reconnect-Loop stoppt sobald Client weg ist
    #    self.mapping_active[token] = True

    # TODO: Mapping auf Session_ID umstellen, um Kollisionen der Nutzer zu verhindern
    async def start_stream(self, token: str, sid: str):  # ← ip → sid
        if sid in self.mapping_sid:
            old_token = self.mapping_sid[sid]
            if old_token in self.mapping_ws:
                await self.mapping_ws[old_token].close()

        self.mapping_sid[sid] = token  # ← mapping_ip → mapping_sid
        self.mapping_active[token] = True

        conn = f"{websocket_url}/ws/subscribe/scores"

        # alt
        # TODO: alte Websocket-API herauslöschen!
        #while True:  # Reconnect-Schleife
        #    try:
        #        websocket = await websockets.connect(
        #            conn,
        #            ping_interval=20,
        #            ping_timeout=20,
        #            close_timeout=5,
        #            max_queue=32,
        #        )
        #        self.mapping_ws[token] = websocket
        #        logging.info(f"Starting stream for {token} on {ip}")

        #        timeout_counter = 0

        #        try:
        #            initial_data = await asyncio.wait_for(
        #                websocket.recv(), timeout=10
        #            )
        #            initial_state = json.loads(initial_data)
        #            yield initial_state
        #            logging.info(
        #                f"[WS] Full-State delivered after connect "
        #                f"({len(initial_state)} items)"
        #            )
        #        except Exception as e:
        #            logging.error(
        #                f"[WS] Failed to receive initial state: {e}"
        #            )
        #            await websocket.close()
        #            await asyncio.sleep(2)
        #            continue

        #        while True:
        #            try:
        #                data = await asyncio.wait_for(
        #                    websocket.recv(), timeout=30
        #                )
        #                msg = json.loads(data)

        #                # Heartbeat
        #                if isinstance(msg, dict) and msg.get("heartbeat"):
        #                    timeout_counter = 0
        #                    continue

        #                timeout_counter = 0
        #                yield msg  # Delta-Update

        #            except asyncio.TimeoutError:
        #                timeout_counter += 1
        #                logging.warning(
        #                    f"WS timeout for {token} ({timeout_counter}/3), "
        #                    f"sending ping…"
        #                )

        #                try:
        #                    await websocket.ping()
        #                except Exception:
        #                    logging.warning(
        #                        f"Ping failed for {token}, forcing reconnect…"
        #                    )
        #                    break

        #                if timeout_counter >= 3:
        #                    logging.warning(
        #                        f"Too many timeouts for {token}, "
        #                        f"forcing reconnect…"
        #                    )
        #                    break

        #            except (
        #                ConnectionClosed,
        #                ConnectionClosedError,
        #                ConnectionClosedOK,
        #            ):
        #                logging.warning(
        #                    f"WS closed for {token}, reconnecting…"
        #                )
        #                break

        #    except Exception as e:
        #        logging.error(f"WS connection error for {token}: {e}")

        #    await asyncio.sleep(2)  # Reconnect delay

        # neu 
        # TODO: neue Websocket-API + Einbindung Cancellation-Flag
        # Sauberes Stoppen der Schleife durch Cancellation-Flag
        while self.mapping_active.get(token, False):
            try:
                async with websockets.connect(
                    conn,
                    ping_interval=20,
                    ping_timeout=20,
                    close_timeout=5,
                    max_queue=32,
                ) as websocket:
                    self.mapping_ws[token] = websocket
                    # TODO: Hier ist noch auf IP gemappt, d.h. entfernen, wenn auf Session_ID geändert!
                    #logging.info(f"Starting stream for {token} on {ip}")
                    # TODO: Logging auf Session_ID
                    logging.info(f"Starting stream for {token} on {sid}")

                    timeout_counter = 0

                    try:
                        initial_data = await asyncio.wait_for(
                            websocket.recv(), timeout=10
                        )
                        initial_state = json.loads(initial_data)
                        yield initial_state
                        logging.info(
                            f"[WS] Full-State delivered after connect "
                            f"({len(initial_state)} items)"
                        )
                    except Exception as e:
                        logging.error(
                            f"[WS] Failed to receive initial state: {e}"
                        )
                        await asyncio.sleep(2)
                        continue

                    while self.mapping_active.get(token, False):
                        try:
                            data = await asyncio.wait_for(
                                websocket.recv(), timeout=30
                            )
                            msg = json.loads(data)

                            # Heartbeat
                            if isinstance(msg, dict) and msg.get("heartbeat"):
                                timeout_counter = 0
                                continue

                            timeout_counter = 0
                            yield msg

                        except asyncio.TimeoutError:
                            timeout_counter += 1
                            logging.warning(
                                f"WS timeout for {token} ({timeout_counter}/3), "
                                f"sending ping…"
                            )

                            try:
                                await websocket.ping()
                            except Exception:
                                logging.warning(
                                    f"Ping failed for {token}, forcing reconnect…"
                                )
                                break

                            if timeout_counter >= 3:
                                logging.warning(
                                    f"Too many timeouts for {token}, "
                                    f"forcing reconnect…"
                                )
                                break

                        except (
                            ConnectionClosed,
                            ConnectionClosedError,
                            ConnectionClosedOK,
                        ):
                            logging.warning(
                                f"WS closed for {token}, reconnecting…"
                            )
                            break

            except Exception as e:
                logging.error(f"WS connection error for {token}: {e}")

            await asyncio.sleep(2)

    # TODO: Hinzufügen der Cancellation-Flag + Aufräumen der Dicts
    # Vermeidung, dass Dicts nach dem Disconnect trotzdem unbegrenzt wachsen (Stichwort Memory Leak)
    async def stop_stream(self, token: str):
        # TODO: neu mit Cancellation-Flag
        self.mapping_active[token] = False
        if token in self.mapping_ws:
            await self.mapping_ws[token].close()
            # Hinzufügen des Cleanings
            del self.mapping_ws[token]
        # mapping_sid aufräumen
        for sid, t in list(self.mapping_sid.items()):
            if t == token:
                del self.mapping_sid[sid]
                break
        # mapping_active aufräumen
        if token in self.mapping_active:
            del self.mapping_active[token]


eHolder = EventHolders()

# === ScoreBoard-State ===
class ScoreBoardState(rx.State, BackendRequests):
    _items: dict[str, dict] = {}
    is_ready: bool = False

    team_event_mode: bool = True
    team_event_leader_mode: bool = False
    more_than_two_teams: bool = False
    teams: list[str] = []
    team_colors: list[str] = []

    show_tug_of_war: bool = True
    show_further_progress_bars: bool = True
    show_scoreboards: bool = True
    show_player_with_points_only: bool = True
    show_position: bool = True
    show_name: bool = True
    show_email: bool = False
    show_points: bool = True
    show_solved: bool = True
    show_badges: bool = False
    show_first_blood: bool = True

    # === Diverse abgeleitete Views ===
    @rx.var
    def top_two_players(self) -> list[str]:
        vals = sorted(
            self._items.values(),
            key=lambda x: x.get("points", 0),
            reverse=True,
        )
        return [v["username"] for v in vals[:2]]

    @rx.var
    def top_two_player_scores(self) -> list[int]:
        vals = sorted(
            self._items.values(),
            key=lambda x: x.get("points", 0),
            reverse=True,
        )
        return [v.get("points", 0) for v in vals[:2]]

    @rx.var
    def top_two_pcts(self) -> list[int]:
        vals = sorted(
            self._items.values(),
            key=lambda x: x.get("points", 0),
            reverse=True,
        )
        if len(vals) < 2:
            return [100] if vals else []
        s0, s1 = vals[0].get("points", 0), vals[1].get("points", 0)
        denom = (s0 + s1) or 1
        return [int(s0 / denom * 100), int(s1 / denom * 100)]

    @rx.var
    def solo_sorted(self) -> list[dict]:
        return sorted(
            self._items.values(),
            key=lambda p: p.get("points", 0),
            reverse=True,
        )

    @rx.var
    def solo_ranks(self) -> list[int]:
        ranks: list[int] = []
        current_rank = 1
        for i, player in enumerate(self.solo_sorted):
            if (
                i > 0
                and player.get("points", 0)
                == self.solo_sorted[i - 1].get("points", 0)
            ):
                ranks.append(ranks[-1])
            else:
                ranks.append(current_rank)
            current_rank = len(ranks) + 1
        return ranks

    @rx.var
    def solo_sorted_filtered(self) -> list[dict]:
        if not self.show_player_with_points_only:
            return self.solo_sorted
        return [pl for pl in self.solo_sorted if pl.get("points", 0) > 0]

    @rx.var
    def solo_ranks_filtered(self) -> list[int]:
        if not self.show_player_with_points_only:
            return self.solo_ranks
        return [
            rank
            for (pl, rank) in zip(self.solo_sorted, self.solo_ranks)
            if pl.get("points", 0) > 0
        ]

    @rx.var
    def solo_bottom_players(self) -> list[str]:
        if len(self.solo_sorted_filtered) <= 2:
            return []
        return [p["username"] for p in self.solo_sorted_filtered[2:]]

    @rx.var
    def solo_bottom_scores(self) -> list[int]:
        if len(self.solo_sorted_filtered) <= 2:
            return []
        return [p["points"] for p in self.solo_sorted_filtered[2:]]

    @rx.var
    def solo_bottom_pcts(self) -> list[int]:
        if len(self.solo_sorted_filtered) <= 2:
            return []
        top_score = self.solo_sorted_filtered[0]["points"] or 1
        return [
            int((p["points"] / top_score) * 100)
            for p in self.solo_sorted_filtered[2:]
        ]

    @rx.var
    def team_scores(self) -> dict[str, int]:
        return {
            team: sum(
                item.get("points", 0)
                for item in self._items.values()
                if item.get("team") == team
            )
            for team in self.teams
        }

    @rx.var
    def ranking(self) -> list[str]:
        return sorted(
            self.teams, key=lambda t: self.team_scores.get(t, 0), reverse=True
        )

    @rx.var
    def team_color_map(self) -> dict[str, str]:
        return {team: self.team_colors[i] for i, team in enumerate(self.teams)}

    @rx.var
    def top_two_teams(self) -> list[str]:
        return self.ranking[:2]

    @rx.var
    def tug_pcts(self) -> list[int]:
        r = self.ranking
        if len(r) < 2:
            return [100] if r else []
        s0, s1 = self.team_scores[r[0]], self.team_scores[r[1]]
        denom = (s0 + s1) or 1
        return [int(s0 / denom * 100), int(s1 / denom * 100)]

    @rx.var
    def top_two_scores(self) -> list[int]:
        return [self.team_scores[t] for t in self.top_two_teams]

    @rx.var
    def top_two_colors(self) -> list[str]:
        return [self.team_color_map[t] for t in self.top_two_teams]

    @rx.var
    def bottom_teams(self) -> list[str]:
        return self.ranking[2:]

    @rx.var
    def bottom_pcts(self) -> list[int]:
        r = self.ranking
        if not r:
            return []
        s0 = self.team_scores[r[0]]
        denom = s0 or 1
        return [int(self.team_scores[t] / denom * 100) for t in r[2:]]

    @rx.var
    def bottom_scores(self) -> list[int]:
        return [self.team_scores[t] for t in self.bottom_teams]

    @rx.var
    def bottom_colors(self) -> list[str]:
        return [self.team_color_map[t] for t in self.bottom_teams]

    @rx.var
    def team_configs(self) -> list[dict[str, str]]:
        return [
            {"team": team, "color": self.team_colors[i]}
            for i, team in enumerate(self.teams)
        ]

    @rx.var
    def sorted_map(self) -> dict[str, list[dict]]:
        return {
            team: sorted(
                [
                    item
                    for item in self._items.values()
                    if item.get("team") == team
                ],
                key=lambda p: p.get("points", 0),
                reverse=True,
            )
            for team in self.teams
        }

    @rx.var
    def rank_map(self) -> dict[str, list[int]]:
        rank_map: dict[str, list[int]] = {}
        for team, players in self.sorted_map.items():
            ranks: list[int] = []
            current_rank = 1
            for i, player in enumerate(players):
                if (
                    i > 0
                    and player.get("points", 0)
                    == players[i - 1].get("points", 0)
                ):
                    ranks.append(ranks[-1])
                else:
                    ranks.append(current_rank)
                current_rank = len(ranks) + 1
            rank_map[team] = ranks
        return rank_map

    @rx.var
    def sorted_map_filtered(self) -> dict[str, list[dict]]:
        if not self.show_player_with_points_only:
            return self.sorted_map
        return {
            team: [pl for pl in players if pl.get("points", 0) > 0]
            for team, players in self.sorted_map.items()
        }

    @rx.var
    def rank_map_filtered(self) -> dict[str, list[int]]:
        if not self.show_player_with_points_only:
            return self.rank_map
        out: dict[str, list[int]] = {}
        for team, players in self.sorted_map.items():
            ranks = self.rank_map[team]
            filtered = [
                rank
                for (pl, rank) in zip(players, ranks)
                if pl.get("points", 0) > 0
            ]
            out[team] = filtered
        return out

    def recalc(self):
        self._items = {**self._items}

    async def check_team_event(self):
        response = await self.get("/admin/event/scoreboard/options")
        status = response.json()

        self.show_tug_of_war = status["tug_of_war"]
        self.show_further_progress_bars = status["further_progress_bars"]
        self.show_scoreboards = status["scoreboards"]
        self.show_player_with_points_only = status["player_with_points_only"]
        self.show_position = status["position"]
        self.show_name = status["name"]
        self.show_email = status["email"]
        self.show_points = status["points"]
        self.show_solved = status["solved"]
        self.show_badges = status["badges"]
        self.show_first_blood = status["first_blood"]

        response = await self.get("/admin/event/teamevent_mode")
        status = response.json()
        self.team_event_mode = status["teamevent_mode"]

        if status["teamevent_mode"]:
            response = await self.get("/admin/event/teamevent_leader_mode")
            status = response.json()
            self.team_event_leader_mode = status["teamevent_leader_mode"]

            response = await self.get("/admin/event/get_event_teams_list")
            status = response.json()
            self.teams = status["teams_list"]
            if len(status["teams_list"]) > 2:
                self.more_than_two_teams = True

            response = await self.get(
                "/admin/event/get_event_team_colors_list"
            )
            status = response.json()
            self.team_colors = status["team_colors"]

        self.is_ready = True

    @rx.event(background=True)
    async def get_states(self):
        """Startet den WS-Stream und haelt den State aktuell"""
        # TODO: check_team_event hier mit try/execpt absichern
        async with self:
            try:
                await self.check_team_event()
            except Exception as e:
                logging.error(f"check_team_event failed: {e}")
    
        # alt
        #token = f"scoreboard-{self.router.session.client_ip}"
        #stream = eHolder.start_stream(token, self.router.session.client_ip)

        # neu
        # TODO: Um gleichzeitiges Zugreifen auf die IP und Kollisionen der Nutzer zu verhindern
        # statt zugriff auf die IP, lieber Zugriff auf die Session ID
        token = f"scoreboard-{self.router.session.session_id}"
        stream = eHolder.start_stream(token, self.router.session.session_id)

        # 1) Initialen Full-State holen
        initial_state = await stream.__anext__()

        # Full-State erkennen
        if isinstance(initial_state, dict) and "full_state" in initial_state:
            initial_state = initial_state["full_state"]

        async with self:
            self._items = {item["username"]: item for item in initial_state}
            logging.info(
                f"[SCOREBOARD] Initial state loaded: "
                f"{len(self._items)} players"
            )

        # 2) Laufende Updates
        try:
            async for update in stream:
                # FULL STATE
                if isinstance(update, dict) and "full_state" in update:
                    full = update["full_state"]
                    async with self:
                        self._items = {
                            item["username"]: item for item in full
                        }
                    logging.info(
                        "[SCOREBOARD] Full-State refresh applied"
                    )
                    continue

                # DELTA UPDATE
                if isinstance(update, list):
                    changes = update
                else:
                    logging.warning(
                        f"[SCOREBOARD] Unknown WS message: {update}"
                    )
                    continue

                async with self:
                    items = dict(self._items)

                    usernames = [c["username"] for c in changes]
                    logging.info(
                        f"[SCOREBOARD] WS update received: "
                        f"{len(changes)} changes → {usernames}"
                    )

                    for change in changes:
                        items[change["username"]] = change

                    self._items = items
                    logging.info(
                        f"[SCOREBOARD] State size after update: "
                        f"{len(self._items)} players"
                    )

        except StopAsyncIteration:
            logging.info("[SCOREBOARD] WebSocket iterator stopped")
