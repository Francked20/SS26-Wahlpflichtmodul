# TODO: Werden hier nicht genutzt, daher löschen 
# import asyncio
# import dataclasses
# import json
import logging
import os
import typing

from beanie import init_beanie
from pymongo import AsyncMongoClient
# TODO: Werden hier nicht genutzt, daher löschen
# from fastapi import FastAPI, WebSocket, WebSocketDisconnect
# from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorChangeStream
# from pymongo.errors import PyMongoError


from database.models import *
# TODO: Funktion _badges_to_str aus websockets.py hier importieren
from endpoints.websockets import score_sockets, _badges_to_str


class MongoDB:
    instance: typing.Optional["MongoDB"] = None

    def __init__(self):
        uri = (
            f"mongodb://{os.getenv('MONGO_INITDB_ROOT_USERNAME')}:"
            f"{os.getenv('MONGO_INITDB_ROOT_PASSWORD')}@mongo/?authSource=admin"
        )
        self._client = AsyncMongoClient(uri)
        self._database = self._client.get_database(os.getenv("MONGO_DB"))

    async def ping(self):
        ping = await self._database.command('ping')
        logging.info(f"Pinged database: {{'ok': {ping['ok']}}}")

    async def connect_mapper(self):
        await init_beanie(
            database=self._database,
            document_models=[
                EventConfig,
                User,
                RunningChallenge,
                Challenge,
                CollectedData,
                OnRegisterUser,
                OnResetUserPW,
                OnPreRegisterUser
            ],
        )

    async def disconnect(self):
        await self._client.close()

    # alt: Version mit integrierter Badges-Funktion 
    # async def broadcast_score_update(self, user: User):

    #    raw_badges = getattr(user.stats, "badges", [])

    #    if isinstance(raw_badges, list):
    #        if not raw_badges:
    #            badges_str = ""
    #        elif all(isinstance(b, dict) and "emoji" in b for b in raw_badges):
    #            badges_str = "".join(b["emoji"] for b in raw_badges)
    #        elif all(isinstance(b, str) for b in raw_badges):
    #            badges_str = "".join(raw_badges)
    #        else:
    #            badges_str = str(raw_badges)
    #    elif isinstance(raw_badges, str):
    #        badges_str = raw_badges
    #    else:
    #        badges_str = ""

    #    update = {
    #        "email": user.email,
    #        "username": user.username,
    #        "team": user.team,
    #        "points": user.stats.points,
    #        "challenges_solved": user.stats.challenges_solved,
    #        "streak": user.stats.streak,
    #        "first_solves": user.stats.first_solves,
    #        "badges": badges_str
    #    }
    #    data = [update]
    #    logging.info(f"Broadcasting score update: {data}")

    #    # Problem hier: race condition beim Disconnect
    #    # Thread A: broadcast_score_update läuft
    #    for socket in score_sockets[:]:   # Kopie der Liste
    #        try:
    #            await socket.send_json(data)    # wirft Exception wenn tot
    #        except Exception as e:
    #            logging.warning(f"Removing dead socket during broadcast: {e}")
    #            # Thread B: Heartbeat-Loop merkt Verbindung ist tot → break
    #            score_sockets.remove(socket)
    #            # Socket wird entfernt, ABER broadcast hat schon eine Kopie der alten Liste

    # neu
    # TODO: schlankere broadcast_score_update-Datei --> ausgelagerte Badges-Funktion siehe in websockets.py
    async def broadcast_score_update(self, user: User):
        update = {
            "email": user.email,
            "username": user.username,
            "team": user.team,
            "points": user.stats.points,
            "challenges_solved": user.stats.challenges_solved,
            "streak": user.stats.streak,
            "first_solves": user.stats.first_solves,
            "badges": _badges_to_str(getattr(user.stats, "badges", [])),
        }
        data = [update]
        logging.info(f"Broadcasting score update: {data}")

        for socket in score_sockets[:]:
            try:
                await socket.send_json(data)
            except Exception as e:
                logging.warning(f"Removing dead socket during broadcast: {e}")
                score_sockets.remove(socket)
