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

    return {"answer_correct": res}


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
