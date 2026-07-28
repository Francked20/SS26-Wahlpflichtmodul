import os
import httpx
import asyncio
import logging
import json

from fastapi import APIRouter, HTTPException, Request, Security
from fastapi.params import Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi_jwt import JwtAuthorizationCredentials
from pydantic import BaseModel, field_validator

from database.models import *
from utils.security import access_security, require_admin_token

import hashlib

timeout = httpx.Timeout(
    connect=10.0,   # Verbindungsaufbau
    read=30.0,      # Zeit bis zur Antwort
    write=10.0,
    pool=10.0,
)

enable_cyber_range = os.getenv("ENABLE_CYBER_RANGE", "False").lower() == "true"
cyber_range_admin_key = os.getenv("CYBER_RANGE_ADMIN_KEY")
cyber_range_base_url = os.getenv("CYBER_RANGE_BASE_URL")
cyber_range_labid = os.getenv("CYBER_RANGE_LABID", "hiy")  # Default falls nicht gesetzt

MAX_RETRIES = 3
RETRY_DELAY = 1.0  # Sekunden

async def post_with_retry(url, headers, params, json_payload, effective_username, timeout=10.0):
    """Robuster POST mit Retry bei TLS/Transportfehlern."""
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                resp = await client.post(
                    url,
                    headers=headers,
                    params=params,
                    json=json_payload,
                )

            if resp.status_code == 200:
                logging.info(
                    f"[FLAG-INJECT] SUCCESS for user={effective_username}: "
                    f"{json.dumps(json_payload, indent=2)}"
                )
                return resp

            logging.error(
                f"[FLAG-INJECT] FAILED (HTTP {resp.status_code}) for user={effective_username}, "
                f"response={resp.text}"
            )
            return resp

        except (httpx.TransportError, httpx.ReadTimeout, httpx.ConnectError) as e:
            logging.warning(
                f"[FLAG-INJECT] Network error on attempt {attempt}/{MAX_RETRIES} "
                f"for user={effective_username}: {e}"
            )

            if attempt == MAX_RETRIES:
                logging.error(
                    f"[FLAG-INJECT] Giving up after {MAX_RETRIES} attempts for user={effective_username}"
                )
                raise

            await asyncio.sleep(RETRY_DELAY)

        except Exception as e:
            logging.exception(
                f"[FLAG-INJECT] Unexpected error for user={effective_username}: {e}"
            )
            raise


router = APIRouter()

def generate_subdomain(username: str) -> str:
    return hashlib.sha256(username.encode()).hexdigest()[:6]

async def _user_should_have_cyber_range(username: str) -> bool:
    username = (username or "").lower()

    # EventConfig laden
    event_config = await EventConfig.find_one({})
    if not event_config:
        return True  # Fallback: alle bekommen eine Range

    # Kein Team-Event → alle User bekommen eine Range
    if not event_config.event_teamevent_mode:
        return True

    # Team-Event, aber keine Leader-Regel → alle User bekommen eine Range
    if not event_config.event_teamevent_has_leaders:
        return True

    # Team-Event + Leader-Regel → nur Leader bekommen eine Range
    user = await User.find_one(User.username == username)
    if not user:
        return False  # Sicherheitshalber

    # Falls dein User-Modell "team_leader" heißt:
    return bool(getattr(user, "team_leader", False))

if(enable_cyber_range):
    @router.get("/list-labs")
    async def list_labs():
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.get(f"{cyber_range_base_url}/labs/list")
            return resp.json()

    @router.get("/list-instances")
    async def list_instances():
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.get(f"{cyber_range_base_url}/labs/list-instances")
            return resp.json()

    @router.post("/create_cyber_ranges")
    async def create_cyber_ranges(
        _: None = Depends(require_admin_token),
    ):
        labid = cyber_range_labid
        results = []
        async with httpx.AsyncClient(timeout=timeout) as client:

            resp_list = await client.get(f"{cyber_range_base_url}/labs/list")
            available_labs = resp_list.json()

            if labid not in available_labs:
                return {
                    "status": "error",
                    "message": f"Lab '{labid}' existiert nicht auf der Cyber-Range.",
                    "available_labs": list(available_labs.keys())
                }

            users = await User.all().to_list()  # je nach ORM evtl. anders
            for user in users:

                if not await _user_should_have_cyber_range(user.username):
                    results.append({"user": user.username, "status": "skipped (no cyber range for user)"})
                    continue

                userid = generate_subdomain(user.username)

                # 1. Existenz prüfen
                resp_exists = await client.get(
                    f"{cyber_range_base_url}/labs/is-existing",
                    params={"labid": labid, "userid": userid},
                )
                exists = resp_exists.json().get("status", False)
                if exists:
                    # 2. Läuft?
                    resp_running = await client.get(
                        f"{cyber_range_base_url}/labs/is-running",
                        params={"labid": labid, "userid": userid},
                    )
                    running = resp_running.json().get("status", False)
                    if running:
                        results.append({"user": user.username, "status": "already running"})
                        continue

                # 3. Busy?
                resp_busy = await client.get(
                    f"{cyber_range_base_url}/labs/is-busy",
                    params={"labid": labid, "userid": userid},
                )
                busy = resp_busy.json().get("status", False)
                if busy:
                    results.append({"user": user.username, "status": "busy"})
                    continue

                # 4. Lab erstellen
                resp_create = await client.get(
                    f"{cyber_range_base_url}/labs/create",
                    headers={"X-API-Key": cyber_range_admin_key},
                    params={"labid": labid, "userid": userid, "autoflags": True},
#                    json={"labid": labid, "userid": userid, "autoflags": True},
                )
                results.append({
                    "user": user.username,
                    "status": f"created ({resp_create.status_code})"
                })

        return {"results": results}

    @router.post("/destroy_cyber_ranges")
    async def destroy_cyber_ranges(
        _: None = Depends(require_admin_token),
    ):
        labid = cyber_range_labid
        results = []
        async with httpx.AsyncClient(timeout=timeout) as client:

            resp_list = await client.get(f"{cyber_range_base_url}/labs/list")
            available_labs = resp_list.json()
            
            if labid not in available_labs:
                return {
                    "status": "error",
                    "message":
                    f"Lab '{labid}' existiert nicht auf der Cyber-Range.",
                    "available_labs": list(available_labs.keys())
                }

            users = await User.all().to_list()  # je nach ORM evtl. anders
            for user in users:

                if not await _user_should_have_cyber_range(user.username):
                    results.append({"user": user.username, "status": "skipped (no cyber range for user)"})
                    continue

                userid = generate_subdomain(user.username)

                # 1. Existenz prüfen
                resp_exists = await client.get(
                    f"{cyber_range_base_url}/labs/is-existing",
                    params={"labid": labid, "userid": userid},
                )
                exists = resp_exists.json().get("status", False)
                if exists:
                    # 2. Lab destroy
                    resp_destroy = await client.get(
                        f"{cyber_range_base_url}/labs/destroy",
                        headers={"X-API-Key": cyber_range_admin_key},
                        params={"labid": labid, "userid": userid},
#                        json={"labid": labid, "userid": userid},
                    )
                    results.append({
                        "user": user.username,
                        "status": f"destroyed ({resp_destroy.status_code})"
                    })

        return {"results": results}

    @router.get("/status")
    async def cyberrange_status(
        auth: JwtAuthorizationCredentials = Security(access_security),
    ):
        labid = cyber_range_labid
        username = auth.subject["username"].lower()
        userid = generate_subdomain(username)

        async with httpx.AsyncClient(timeout=timeout) as client:

            # --- 1. Lab-Liste prüfen ---
            resp_list = await client.get(f"{cyber_range_base_url}/labs/list")
            available_labs = resp_list.json()

            if labid not in available_labs:
                return {
                    "running": False,
                    "exists": False,
                    "busy": False,
                    "stopped": False,
                    "message": f"Lab '{labid}' existiert nicht auf der Cyber-Range."
                }

            # --- 2. Existenz prüfen ---
            resp_exists = await client.get(
                f"{cyber_range_base_url}/labs/is-existing",
                params={"labid": labid, "userid": userid},
            )
            exists = resp_exists.json().get("status", False)

            if not exists:
                return {
                    "running": False,
                    "exists": False,
                    "busy": False,
                    "stopped": False,
                    "message": "Für dich existiert noch kein Lab. Bitte zuerst deployen lassen."
                }

            # --- 3. Running prüfen ---
            resp_running = await client.get(
                f"{cyber_range_base_url}/labs/is-running",
                params={"labid": labid, "userid": userid},
            )
            running = resp_running.json().get("status", False)

            if running:
                # --- 4. Access holen ---
                resp_access = await client.get(
                    f"{cyber_range_base_url}/labs/get-access",
                    headers={"X-API-Key": cyber_range_admin_key},
                    params={"labid": labid, "userid": userid},
                )

                if resp_access.status_code == 200:
                    data = resp_access.json()
                    return {
                        "running": True,
                        "exists": True,
                        "busy": False,
                        "stopped": False,
                        "url": data.get("url"),
                        "user": data.get("user"),
                        "password": data.get("password"),
                        "message": "Lab läuft."
                    }

                return {
                    "running": True,
                    "exists": True,
                    "busy": False,
                    "stopped": False,
                    "message": "Lab läuft, aber Zugangsdaten konnten nicht abgerufen werden."
                }

            # --- 5. Busy prüfen ---
            resp_busy = await client.get(
                f"{cyber_range_base_url}/labs/is-busy",
                params={"labid": labid, "userid": userid},
            )
            busy = resp_busy.json().get("status", False)

            if busy:
                return {
                    "running": False,
                    "exists": True,
                    "busy": True,
                    "stopped": False,
                    "message": "Lab wird gerade erstellt oder gestartet."
                }

            # --- 6. Existiert, nicht busy, nicht running → stopped ---
            return {
                "running": False,
                "exists": True,
                "busy": False,
                "stopped": True,
                "message": "Lab existiert, läuft aber nicht."
            }

    @router.post("/reset")
    async def cyberrange_reset(
        auth: JwtAuthorizationCredentials = Security(access_security),
    ):
        labid = cyber_range_labid
        username = auth.subject["username"].lower()
        userid = generate_subdomain(username)

        async with httpx.AsyncClient(timeout=timeout) as client:

            resp = await client.get(
                f"{cyber_range_base_url}/labs/reset",
                headers={"X-API-Key": cyber_range_admin_key},
                params={"labid": labid, "userid": userid},
            )

            if resp.status_code != 200:
                return {
                    "status": "error",
                    "message": f"Reset fehlgeschlagen ({resp.status_code})",
                    "details": resp.text,
                }

            return resp.json()

    @router.post("/admin_reset")
    async def admin_cyberrange_reset(
        username: str,
        _: None = Depends(require_admin_token),
    ):
        labid = cyber_range_labid
        userid = generate_subdomain(username.lower())

        async with httpx.AsyncClient(timeout=timeout) as client:

            resp = await client.get(
                f"{cyber_range_base_url}/labs/reset",
                headers={"X-API-Key": cyber_range_admin_key},
                params={"labid": labid, "userid": userid},
            )

            if resp.status_code != 200:
                return {
                    "status": "error",
                    "message": f"Reset fehlgeschlagen ({resp.status_code})",
                    "details": resp.text,
                }

            return resp.json()

    @router.post("/inject_flag")
    async def inject_flag(
        username: str,
        vm_name: str,
        flag_type: str,
        flag: str,
        auth: JwtAuthorizationCredentials = Security(access_security),
    ):
        labid = cyber_range_labid
        userid = generate_subdomain(username)

        # JSON body exactly as required
        payload = {
            vm_name: {
                flag_type: flag
            }
        }

        url = f"{cyber_range_base_url}/flags/write-flags"
        headers = {"X-API-Key": cyber_range_admin_key}
        params = {"labid": labid, "userid": userid}

        try:
            resp = await post_with_retry(
                url=url,
                headers=headers,
                params=params,
                json_payload=payload,
                effective_username=username,
                timeout=timeout,
            )
        except Exception as e:
            return {
                "status": "error",
                "message": "Flag injection failed after retries",
                "details": str(e),
            }

        if resp.status_code != 200:
            return {
                "status": "error",
                "message": f"Flag injection failed ({resp.status_code})",
                "details": resp.text,
            }

        return resp.json()

#        async with httpx.AsyncClient(timeout=timeout) as client:
#            resp = await client.post(
#                f"{cyber_range_base_url}/flags/write-flags",
#                headers={"X-API-Key": cyber_range_admin_key},
#                params={"labid": labid, "userid": userid},
#                json=payload,
#            )
#
#            if resp.status_code != 200:
#                return {
#                    "status": "error",
#                    "message": f"Flag injection failed ({resp.status_code})",
#                    "details": resp.text,
#                }
#
#            return resp.json()

