import asyncio
import logging

# Wird hier nicht benötigt
#from beanie.operators import NotIn
from fastapi import APIRouter, Security, WebSocket, WebSocketDisconnect   # Security-Zusatz könnte hier theoretisch weggelöscht werden!
# Wird hier nicht benötigt
#from fastapi_jwt import JwtAuthorizationCredentials

from database.models import *
# Wird hier nicht benötigt
#from utils.security import access_security

router = APIRouter()

score_sockets: list[WebSocket] = []

# TODO: ausgelagerte Hilsfunktion, die auch in connection.py verwendet wird

def _badges_to_str(raw_badges) -> str:
    """Hilfsfunktion – wird sowohl in websockets.py als auch in connection.py genutzt."""
    if isinstance(raw_badges, list):
        if not raw_badges:
            return ""
        elif all(isinstance(b, dict) and "emoji" in b for b in raw_badges):
            return "".join(b["emoji"] for b in raw_badges)
        elif all(isinstance(b, str) for b in raw_badges):
            return "".join(raw_badges)
        else:
            return str(raw_badges)
    elif isinstance(raw_badges, str):
        return raw_badges
    return ""


async def _build_full_state() -> list[dict]:
    """Vollständigen State aller User aufbauen."""
    users = await User.all().sort(
        "-stats.points", "-stats.challenges_solved"
    ).to_list()

    items = []
    for user in users:
        items.append({
            "email": user.email,
            "username": user.username,
            "team": user.team,
            "points": user.stats.points,
            "challenges_solved": user.stats.challenges_solved,
            "streak": user.stats.streak,
            "first_solves": user.stats.first_solves,
            "badges": _badges_to_str(getattr(user.stats, "badges", [])),
        })
    return items

# neu
# TODO: überarbeitete Funktion mit parallelem Heartbeat und Disconnect

@router.websocket("/scores")
async def listen_to_scores(websocket: WebSocket):
    """WebSocket for scoreboard updates with heartbeat support."""

    await websocket.accept()
    score_sockets.append(websocket)
    logging.info(f"Client connected. {len(score_sockets)} clients connected.")

    try:
        # Initial state senden
        items = await _build_full_state()
        await websocket.send_json({"full_state": items})
        logging.info(f"Initial scoreboard state sent ({len(items)} players)")

        # Heartbeat und Disconnect-Detection parallel
        # receive() nun vorhanden
        async def heartbeat():
            while True:
                await asyncio.sleep(10)
                await websocket.send_json({"heartbeat": True})

        async def receive_loop():
            while True:
                await websocket.receive_text()

        heartbeat_task = asyncio.create_task(heartbeat())
        receive_task = asyncio.create_task(receive_loop())

        done, pending = await asyncio.wait(
            [heartbeat_task, receive_task],
            return_when=asyncio.FIRST_COMPLETED,
        )
        for task in pending:
            task.cancel()

    except WebSocketDisconnect:
        pass
    except Exception as e:
        logging.warning(f"WebSocket error: {e}")
    finally:
        if websocket in score_sockets:
            score_sockets.remove(websocket)
        logging.info(f"Client disconnected. {len(score_sockets)} clients connected.")

# alt
#@router.websocket("/scores")
#async def listen_to_scores(websocket: WebSocket):
#    """WebSocket for scoreboard updates with heartbeat support."""

#    await websocket.accept()
#    score_sockets.append(websocket)
#    logging.info(f"Client connected. {len(score_sockets)} clients connected.")

#    try:
#        # Initial state
#        current_state = await User.all().sort("-stats.points", "-stats.challenges_solved").to_list()

#        items = []
#        for user in current_state:
#            raw_badges = getattr(user.stats, "badges", [])
#            if isinstance(raw_badges, list):
#                if not raw_badges:
#                    badges_str = ""
#                elif all(isinstance(b, dict) and "emoji" in b for b in raw_badges):
#                    badges_str = "".join(b["emoji"] for b in raw_badges)
#                elif all(isinstance(b, str) for b in raw_badges):
#                    badges_str = "".join(raw_badges)
#                else:
#                    badges_str = str(raw_badges)
#            elif isinstance(raw_badges, str):
#                badges_str = raw_badges
#            else:
#                badges_str = ""

#            items.append({
#                "email": user.email,
#                "username": user.username,
#                "team": user.team,
#                "points": user.stats.points,
#                "challenges_solved": user.stats.challenges_solved,
#                "streak": user.stats.streak,
#                "first_solves": user.stats.first_solves,
#                "badges": badges_str,
#            })

##        await websocket.send_json(items)
#        await websocket.send_json({"full_state": items})
#        logging.info(f"Initial scoreboard state sent ({len(items)} players)")

        # Heartbeat loop blockiert aktuell alles
        # kein receive_loop() enthalten: tote sockets blieben im score_socket bis der nächste Heartbeat fehlschlug
#        while True:
#            await asyncio.sleep(10)
#            try:
#                await websocket.send_json({"heartbeat": True})
#            except Exception:
#                break

#    except WebSocketDisconnect:
#        pass

#    finally:
#        if websocket in score_sockets:
#            score_sockets.remove(websocket)
#        logging.info(f"Client disconnected. {len(score_sockets)} clients connected.")
