import os
import asyncio
from typing import Literal, List, Dict

import argon2
from beanie.operators import NotIn
from fastapi import APIRouter, Response, Depends, HTTPException
from fastapi_jwt import JwtAuthorizationCredentials

from database.models import *
from utils.security import access_security, require_admin_token

from pydantic import EmailStr, BaseModel


router = APIRouter()

class EventStatus(BaseModel):
    enabled: bool

@router.post("/event/status")
async def set_event_status(
    status: EventStatus,
    _: None = Depends(require_admin_token),
):
    if status.enabled:
        await EventConfig.enable_event()
    else:
        await EventConfig.disable_event()
    return {"message": "Event status updated"}

@router.get("/event/status")
async def get_event_status():
    status = await EventConfig.get_event_status()
    return {"enabled": status}

class EventRegistrationStatus(BaseModel):
    enabled: bool

@router.post("/event/registration_status")
async def set_event_registration_status(
    status: EventRegistrationStatus,
    _: None = Depends(require_admin_token),
):
    if status.enabled:
        await EventConfig.enable_event_registration()
    else:
        await EventConfig.disable_event_registration()
    return {"message": "Event registration status updated"}

@router.get("/event/registration_status")
async def get_event_registration_status():
    status = await EventConfig.get_event_registration_status()
    return {"enabled": status}

class EventPreregisterMode(BaseModel):
    pre_registration: bool

@router.post("/event/preregister_mode")
async def set_event_preregister_mode(
    status: EventPreregisterMode,
    _: None = Depends(require_admin_token),
):
    if status.pre_registration:
        await EventConfig.enable_preregister_mode()
    else:
        await EventConfig.disable_preregister_mode()
    return {"message": "Event preregister mode updated"}

@router.get("/event/preregister_mode")
async def get_event_preregister_mode():
    pre_registration = await EventConfig.get_event_preregister_mode()
    return {"pre_registration": pre_registration}

class EventBadgesMode(BaseModel):
    badges_mode: bool

@router.post("/event/badges_mode")
async def set_event_badges_mode(
    status: EventBadgesMode,
    _: None = Depends(require_admin_token),
):
    if status.badges_mode:
        await EventConfig.enable_badges_mode()
    else:
        await EventConfig.disable_badges_mode()
    return {"message": "Event badges mode updated"}

@router.get("/event/badges_mode")
async def get_event_badges_mode():
    badges_mode = await EventConfig.get_event_badges_mode()
    return {"badges_mode": badges_mode}

class BadgeDef(BaseModel):
    emoji: str
    tooltip: str = ""

class EventBadgesList(BaseModel):
    badges: List[BadgeDef]

@router.post("/event/set_event_badges_list")
async def set_event_badges_list(
    badges_list: EventBadgesList,
    _: None = Depends(require_admin_token),
):
#    await EventConfig.set_event_badges_list(badges_list.badges)
    await EventConfig.set_event_badges_list(
        [badge.model_dump() for badge in badges_list.badges]
    )
    return {"message": "Event badges list updated successfully"}

@router.get("/event/get_event_badges_list")
async def get_event_badges_list():
#    badges_list = await EventConfig.get_event_badges_list()
#    return {"badges_list": badges_list}
    badges_list = await EventConfig.get_event_badges_list()
    return {"badges_list": [BadgeDef(**b) for b in badges_list]}

# ---------- NEU: Player Levels / Ranks ----------
class PlayerLevelsMode(BaseModel):
    player_levels_mode: bool

@router.post("/event/player_levels_mode")
async def set_player_levels_mode(
    status: PlayerLevelsMode,
    _: None = Depends(require_admin_token),
):
    if status.player_levels_mode:
        await EventConfig.enable_player_levels_mode()
    else:
        await EventConfig.disable_player_levels_mode()
    return {"message": "Player levels mode updated"}

@router.get("/event/player_levels_mode")
async def get_player_levels_mode():
    mode = await EventConfig.get_player_levels_mode()
    return {"player_levels_mode": mode}

class ConfettiMode(BaseModel):
    confetti: bool

@router.post("/event/confetti_mode")
async def set_confetti_mode(
    status: ConfettiMode,
    _: None = Depends(require_admin_token),
):
    if status.confetti:
        await EventConfig.enable_confetti_mode()
    else:
        await EventConfig.disable_confetti_mode()
    return {"message": "Confetti Mode status updated"}

@router.get("/event/confetti_mode")
async def get_confetti_mode():
    confetti = await EventConfig.get_confetti_mode()
    return {"confetti": confetti}

class ToastMode(BaseModel):
    toast: bool

@router.post("/event/toast_mode")
async def set_toast_mode(
    status: ToastMode,
    _: None = Depends(require_admin_token),
):
    if status.toast:
        await EventConfig.enable_toast_mode()
    else:
        await EventConfig.disable_toast_mode()
    return {"message": "Toast Mode status updated"}

@router.get("/event/toast_mode")
async def get_toast_mode():
    toast = await EventConfig.get_toast_mode()
    return {"toast": toast}

class RankConfigIn(BaseModel):
    rank_names: List[str]
    rank_thresholds: List[int]
    points_per_level: int = 500

@router.post("/event/set_rank_config")
async def set_rank_config(
    payload: RankConfigIn,
    _: None = Depends(require_admin_token),
):
    try:
        await EventConfig.set_event_rank_config(
            rank_names=payload.rank_names,
            rank_thresholds=payload.rank_thresholds,
            points_per_level=payload.points_per_level,
        )
        return {"message": "Rank configuration updated successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/event/get_rank_config")
async def get_rank_config():
    cfg = await EventConfig.get_event_rank_config()
    return cfg

class EventPlayerStatsOptions(BaseModel):
    finish_time: bool = False
    day: bool = False
    task: bool = False
    points: bool = False
    tries: bool = False
    hints: bool = False
    resets: bool = False
    first_blood: bool = False

@router.post("/event/stats/options")
async def set_event_stats_options(
    options: EventPlayerStatsOptions,
    _: None = Depends(require_admin_token),
):
    await EventConfig.set_event_stats_options(
        finish_time=options.finish_time,
        day=options.day,
        task=options.task,
        points=options.points,
        tries=options.tries,
        hints=options.hints,
        resets=options.resets,
        first_blood=options.first_blood,
    )
    return {"message": "Event player stats options updated"}

@router.get("/event/stats/options")
async def get_event_stats_options():
    options = await EventConfig.get_event_stats_options()
    return options

class EventScoreboardStatsOptions(BaseModel):
    tug_of_war: bool = False
    further_progress_bars: bool = False
    scoreboards: bool = False
    player_with_points_only: bool = False
    position: bool = False
    name: bool = False
    email: bool = False
    points: bool = False
    solved: bool = False
    badges: bool = False
    first_blood: bool = False

@router.post("/event/scoreboard/options")
async def set_event_scoreboard_options(
    options: EventScoreboardStatsOptions,
    _: None = Depends(require_admin_token),
):
    await EventConfig.set_event_scoreboard_options(
        tug_of_war=options.tug_of_war,
        further_progress_bars=options.further_progress_bars,
        scoreboards=options.scoreboards,
        player_with_points_only=options.player_with_points_only,
        position=options.position,
        name=options.name,
        email=options.email,
        points=options.points,
        solved=options.solved,
        badges=options.badges,
        first_blood=options.first_blood,
    )
    return {"message": "Event scoreboard options updated"}

@router.get("/event/scoreboard/options")
async def get_event_scoreboard_options():
    options = await EventConfig.get_event_scoreboard_options()
    return options

class EventTeamEventMode(BaseModel):
    team_event: bool

@router.post("/event/teamevent_mode")
async def set_event_teamevent_mode(
    status: EventTeamEventMode,
    _: None = Depends(require_admin_token),
):
    if status.team_event:
        await EventConfig.enable_teamevent_mode()
    else:
        await EventConfig.disable_teamevent_mode()
    return {"message": "Event teamevent mode updated"}

@router.get("/event/teamevent_mode")
async def get_event_teamevent_mode():
    teamevent_mode = await EventConfig.get_event_teamevent_mode()
    return {"teamevent_mode": teamevent_mode}

class EventTeamEventLeaderMode(BaseModel):
    team_event_leader: bool

@router.post("/event/teamevent_leader_mode")
async def set_event_teamevent_leader_mode(
    status: EventTeamEventLeaderMode,
    _: None = Depends(require_admin_token),
):
    if status.team_event_leader:
        await EventConfig.enable_teamevent_leader_mode()
    else:
        await EventConfig.disable_teamevent_leader_mode()
    return {"message": "Event teamevent leader mode updated"}

@router.get("/event/teamevent_leader_mode")
async def get_event_teamevent_leader_mode():
    teamevent_leader_mode = await EventConfig.get_event_teamevent_leader_mode()
    return {"teamevent_leader_mode": teamevent_leader_mode}

class EventTeamsList(BaseModel):
    teams: List[str]

@router.post("/event/set_event_teams_list")
async def set_event_teams_list(
    teams_list: EventTeamsList,
    _: None = Depends(require_admin_token),
):
    await EventConfig.set_event_teams_list(teams_list.teams)
    return {"message": "Event teams list updated successfully"}

@router.get("/event/get_event_teams_list")
async def get_event_teams_list():
    teams_list = await EventConfig.get_event_teams_list()
    return {"teams_list": teams_list}


class EventTeamColorsList(BaseModel):
    team_colors: List[str]

@router.post("/event/set_event_team_colors_list")
async def set_event_team_colors_list(
    team_color_list: EventTeamColorsList,
    _: None = Depends(require_admin_token),
):
    await EventConfig.set_event_team_colors_list(team_color_list.team_colors)
    return {"message": "Event team colors updated successfully"}

@router.get("/event/get_event_team_colors_list")
async def get_event_team_colors_list():
    team_colors = await EventConfig.get_event_team_colors_list()
    return {"team_colors": team_colors}

class EventShowAnswersMode(BaseModel):
    show_answers: bool

@router.post("/event/show_answers_mode")
async def set_event_show_answers_mode(
    status: EventShowAnswersMode,
    _: None = Depends(require_admin_token),
):
    if status.show_answers:
        await EventConfig.enable_show_answers_mode()
    else:
        await EventConfig.disable_show_answers_mode()
    return {"message": "Event Show Answers mode updated"}

@router.get("/event/show_answers_mode")
async def get_event_show_answers_mode():
    show_answers = await EventConfig.get_event_show_answers_mode()
    return {"show_answers": show_answers}


class EventEnableTaskResetMode(BaseModel):
    allow_task_reset: bool

@router.post("/event/allow_task_reset_mode")
async def set_event_allow_task_reset_mode(
    status: EventEnableTaskResetMode,
    _: None = Depends(require_admin_token),
):
    if status.allow_task_reset:
        await EventConfig.enable_allow_task_reset_mode()
    else:
        await EventConfig.disable_allow_task_reset_mode()
    return {"message": "Event Enable Task Reset mode updated"}

@router.get("/event/allow_task_reset_mode")
async def get_event_allow_task_reset_mode():
    allow_task_reset = await EventConfig.get_event_allow_task_reset_mode()
    return {"allow_task_reset": allow_task_reset}

class EventEnableTestMode(BaseModel):
    enable_test_mode: bool

@router.post("/event/enable_test_mode")
async def set_event_enable_test_mode(
    status: EventEnableTestMode,
    _: None = Depends(require_admin_token),
):
    if status.enable_test_mode:
        await EventConfig.enable_test_mode()
    else:
        await EventConfig.disable_test_mode()
    return {"message": "Event Enable Test mode updated"}

@router.get("/event/enable_test_mode")
async def get_event_enable_test_mode():
    enable_test_mode = await EventConfig.get_event_enable_test_mode()
    return {"enable_test_mode": enable_test_mode}


@router.get("/event/preregister_user")
async def preregister_user(
    email: EmailStr,
    _: None = Depends(require_admin_token),
):
    email: str = email.lower()
    
    if user := await OnPreRegisterUser.find_one(OnPreRegisterUser.email == email):
        raise HTTPException(status_code=409, detail="Diese E-Mail wurde bereits registriert")

    user = OnPreRegisterUser(email=email)
    await user.create()

    return Response("Ok", status_code=201)
