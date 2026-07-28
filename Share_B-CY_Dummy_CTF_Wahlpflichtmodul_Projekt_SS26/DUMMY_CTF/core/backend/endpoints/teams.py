import json
import logging
import string
from tabnanny import check

from beanie.operators import NotIn, And, Eq
from fastapi import APIRouter, Security
from fastapi_jwt import JwtAuthorizationCredentials
# from profanity_check import predict

from database.models import *
from utils.security import access_security

router = APIRouter()

@router.get("/{team_name}/leader_exists")
async def does_team_leader_exist(team_name: str):
    team_leader_exists = await User.find_one(User.team == team_name, User.team_leader == True)
    return {"team_leader_exists": team_leader_exists is not None}