import logging
import os

from fastapi import APIRouter, Security, HTTPException
from fastapi.params import Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi_jwt import JwtAuthorizationCredentials
from pydantic import BaseModel, field_validator

from database.models import *
from utils.security import access_security


security = HTTPBasic()

router = APIRouter()

class ChallengeReset(BaseModel):
    day: int
    task: int

class ChallengeSolve(BaseModel):
    day: int
    task: int
    solution: str | int


class ChallengeHint(BaseModel):
    day: int
    task: int

@router.post("/reset")
async def reset_challenge(
        ch_data: ChallengeReset,
        auth: JwtAuthorizationCredentials = Security(access_security)
):
    username: str = auth.subject["username"].lower()

    ch = await Challenge.get_challenge(ch_data.day, ch_data.task)
    res = await ch.delete_answer(username)

    # Challenge neu laden (inkl. random_index)
    rc = await RunningChallenge.find_one(
        RunningChallenge.username == username,
        RunningChallenge.challenge.id == ch.id,
        fetch_links=True
    )

    # Challenge-Dokument sicher laden
    challenge_obj = rc.challenge
    if hasattr(challenge_obj, "fetch"):
        challenge_obj = await challenge_obj.fetch()

    # Wenn Cyber-Range-Flag vorhanden → inject_flag aufrufen
    if challenge_obj and challenge_obj.vm_name and challenge_obj.flag_type:
        from endpoints.cyberrange import inject_flag
        flag_value = challenge_obj.solutions[rc.random_index]
        await inject_flag(
            username=username,
            vm_name=challenge_obj.vm_name,
            flag_type=challenge_obj.flag_type,
            flag=flag_value
        )

    return {"task_reset": res}

@router.post("/solve")
async def solve_challenge(
        ch_data: ChallengeSolve,
        auth: JwtAuthorizationCredentials = Security(access_security)
):
    username: str = auth.subject["username"].lower()

    ch = await Challenge.get_challenge(ch_data.day, ch_data.task)
    res = await ch.check_answer(username, ch_data.solution)

    response = {"answer_correct": res}

    # Reward for correctly factoring the 256-bit practice modulus: reveal one
    # factor of the "captured" 512-bit N (data lives in custom/challengebackend).
    if res and ch.dynamic_check == "export_factor256":
        from utils.export_cipher_client import get_reveal_factor
        response["reveal_factor"] = await get_reveal_factor(username)

    return response


@router.get("/export_cipher_reveal_factor")
async def get_export_cipher_reveal_factor_if_solved(
        day: int,
        task: int,
        auth: JwtAuthorizationCredentials = Security(access_security)
):
    """Lets a player re-fetch their already-earned export-cipher reward after
    a page reload - /solve's `reveal_factor` is only included once, transiently,
    in the response to the solving request itself."""
    username: str = auth.subject["username"].lower()

    ch = await Challenge.get_challenge(day, task)
    if ch.dynamic_check != "export_factor256":
        raise HTTPException(status_code=400, detail="Not an export-cipher factor256 task")

    rc = await RunningChallenge.find_one(
        RunningChallenge.username == username,
        RunningChallenge.challenge.id == ch.id,
    )
    if not rc or not rc.solved:
        return {"reveal_factor": None}

    from utils.export_cipher_client import get_reveal_factor
    return {"reveal_factor": await get_reveal_factor(username)}


@router.post("/hint")
async def unlock_hint(
        hi_data: ChallengeHint,
        auth: JwtAuthorizationCredentials = Security(access_security)
):
    username: str = auth.subject["username"].lower()
    ch = await Challenge.get_challenge(hi_data.day, hi_data.task)
    res = await ch.request_hint(username)

    return {"hint_unlocked": res}


@router.get("/all_ch_data")
async def get_all_points():
    chs = await Challenge.all().to_list()
    return {"points": sum(ch.points for ch in chs), "challenges": len(chs)}
