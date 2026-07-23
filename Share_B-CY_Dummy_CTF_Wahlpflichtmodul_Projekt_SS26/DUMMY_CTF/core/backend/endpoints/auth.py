import os
import asyncio
import base64
import json
import logging
import secrets
from datetime import datetime, timedelta

import argon2  # noqa
import pydantic
from fastapi import APIRouter, HTTPException, Response, Security, BackgroundTasks
from fastapi_jwt import JwtAuthorizationCredentials

from starlette.responses import JSONResponse
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
#from pydantic import BaseModel
from pydantic import EmailStr, BaseModel
from typing import List

from database.models import *
from utils.security import access_security

preregister_mode = os.getenv("SET_PREREGISTER_MODE")

router = APIRouter(tags=["auth"])
DEFAULT_TEAM_SHADOW = "rgba(14, 30, 37, 0.65)"

class EmailSchema(BaseModel):
    email: List[EmailStr]

class UserAuth(BaseModel):
    username: str
    password: str
    team: str
    team_leader: bool

class RegisterAuth(UserAuth):
    avatar: str | int

class ResetPWAuth(BaseModel):
    password: str

class AccessToken(BaseModel):
    access_token: str
    access_token_expires: timedelta

@router.post("/register")
async def register_new_user(
        email: EmailStr,
        age_above_16: bool,
):
    email: str = email.lower()

    preregister_mode = await EventConfig.get_event_preregister_mode()

#    if(preregister_mode == "True"):
    if(preregister_mode):
        prereg_user = await OnPreRegisterUser.find_one(OnPreRegisterUser.email == email)
        if not prereg_user:
            raise HTTPException(status_code=413, detail="Du bist leider nicht für das Event vorangemeldet und kannst dich deshalb nicht registrieren")

    if not age_above_16:
        raise HTTPException(status_code=412, detail="Mindestalter zum Erstellen eines Accounts ist 16 Jahre")

    if pending_user := await OnRegisterUser.find_one(OnRegisterUser.email == email):
        if pending_user.timeout < datetime.now():
            await pending_user.delete()  # noqa
        else:
            return Response(status_code=208)

    if user := await User.find_one(User.email == email):
        raise HTTPException(status_code=409, detail="Diese E-Mail wird bereits verwendet")
#        # delete old user if timeout is over
#        if user.timeout < datetime.now():
#            await user.delete()  # noqa
#        else:
#            raise HTTPException(status_code=409, detail="Diese E-Mail wird bereits verwendet")

    token = secrets.token_urlsafe(64)
    timeout = datetime.now() + timedelta(days=1)

    user = OnRegisterUser(email=email, token=token, timeout=timeout)
    await user.create()

    link = f"https://{os.getenv('DOMAIN')}/complete_register/?token={token}"
    logging.info(f"Registering token: {link}")
    await send_registration_token_SMTP_SSL(email,link)
    
    return Response(status_code=202)


@router.post("/reset_pw")
async def reset_user_pw(
        email: EmailStr,
):
    email: str = email.lower()

    if pending_user_pw_reset := await OnResetUserPW.find_one(OnResetUserPW.email == email):
        if pending_user_pw_reset.timeout < datetime.now():
            await pending_user_pw_reset.delete()  # noqa
        else:
            return Response(status_code=208)

    if user := await User.find_one(User.email == email):
        token = secrets.token_urlsafe(64)
        timeout = datetime.now() + timedelta(days=1)
        user = OnResetUserPW(email=email, token=token, timeout=timeout)
        await user.create()

        link = f"https://{os.getenv('DOMAIN')}/reset_password/?token={token}"
        logging.info(f"Reset Password token: {link}")
        await send_pw_reset_token_SMTP_SSL(email,link)
    else:
        await asyncio.sleep(1)
    
    return Response(status_code=202)

#@router.post("/email")
async def send_registration_token_SMTP_SSL(email: str, link: str) -> JSONResponse:

    simple_send_port = os.getenv("SMTP_SSL_PORT")
    simple_send_password = os.getenv("SMTP_SSL_PASSWORD")    
    simple_send_username = os.getenv("SMTP_SSL_USERNAME")
    simple_send_server = os.getenv("SMTP_SSL_SERVER")
    simple_send_sender_email = os.getenv("SMTP_SSL_SENDER_EMAIL")
    simple_send_receiver_email = email
    
    message = MIMEMultipart("alternative")
    message["Subject"] = f"Deine Registrierung beim {os.getenv('BRANDING')}"
    message["From"] = simple_send_sender_email
    message["To"] = simple_send_receiver_email
    
    simple_send_message = f"""\
    <html>
      <body>
        <p>Hallo!<br>
            Vielen Dank für dein Interesse am {os.getenv('BRANDING')}.<br>
            Um die Anmeldung abzuschließen, klicke bitte auf den folgenden Link:<br>
            <a href="{link}">Registrierung abschließen</a><br>
            Viel Spaß beim Event!
        </p>
  </body>
</html>
"""

    body = MIMEText(simple_send_message, "html")

    # Add HTML/plain-text parts to MIMEMultipart message
    # The email client will try to render the last part first
    message.attach(body)

    # Create a secure SSL context
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(simple_send_server, int(simple_send_port), context=context) as server:
        server.login(simple_send_username, simple_send_password)
        server.sendmail(simple_send_sender_email, simple_send_receiver_email, message.as_string())

    return JSONResponse(status_code=200, content={"message": "email has been sent"})

async def send_pw_reset_token_SMTP_SSL(email: str, link: str) -> JSONResponse:

    simple_send_port = os.getenv("SMTP_SSL_PORT")
    simple_send_password = os.getenv("SMTP_SSL_PASSWORD")    
    simple_send_username = os.getenv("SMTP_SSL_USERNAME")
    simple_send_server = os.getenv("SMTP_SSL_SERVER")
    simple_send_sender_email = os.getenv("SMTP_SSL_SENDER_EMAIL")
    simple_send_receiver_email = email
    
    message = MIMEMultipart("alternative")
    message["Subject"] = f"Zurücksetzen des Passwortes beim {os.getenv('BRANDING')}"
    message["From"] = simple_send_sender_email
    message["To"] = simple_send_receiver_email
    
    simple_send_message = f"""\
    <html>
      <body>
        <p>Hallo!<br>
            Das Zurücksetzen deines Passwortes beim {os.getenv('BRANDING')} wurde ausgelöst.<br>
            Sollte das Passwort tatsächlich zurückgesetzt werden wollen, bitte auf folgenden Link klicken:<br>
            <a href="{link}">Passwort zurücksetzen</a><br>
            Sollte das Zurücksetzen des Passwortes nicht beabsichtigt sein, ignoriere diese E-Mail.<br>
            Weiterhin viel Spaß!
        </p>
  </body>
</html>
"""

    body = MIMEText(simple_send_message, "html")

    # Add HTML/plain-text parts to MIMEMultipart message
    # The email client will try to render the last part first
    message.attach(body)

    # Create a secure SSL context
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(simple_send_server, int(simple_send_port), context=context) as server:
        server.login(simple_send_username, simple_send_password)
        server.sendmail(simple_send_sender_email, simple_send_receiver_email, message.as_string())

    return JSONResponse(status_code=200, content={"message": "email has been sent"})

@router.post("/register_complete/{token}")
async def register_new_user_complete(token: str, data: RegisterAuth):
    register_user = await OnRegisterUser.find_one(OnRegisterUser.token == token)
    if register_user is None:
        raise HTTPException(status_code=404, detail="Invalider Token")

    if register_user.timeout < datetime.now():
        raise HTTPException(status_code=403, detail="Token abgelaufen, fordere einen neuen an")

    if await User.find_one(User.username == data.username.lower()):
        raise HTTPException(status_code=409, detail="Benutzername bereits vergeben")

    if(data.team_leader):
        team_leader_exists = await User.find_one(User.team == data.team, User.team_leader == True)
        if team_leader_exists is not None:
            raise HTTPException(status_code=412, detail="Team hat bereits einen Leader")

    decoded_pw = base64.urlsafe_b64decode(data.password).decode()
    pw_hash = await asyncio.get_event_loop().run_in_executor(None, argon2.PasswordHasher().hash, decoded_pw)

    config = await EventConfig.find_one({})
    if config and getattr(config, "event_team_colors", None):
        teams  = config.event_teams
        colors = config.event_team_colors
        try:
            idx = teams.index(data.team)
            selected_color = colors[idx]
        except (ValueError, IndexError):
            selected_color = DEFAULT_TEAM_SHADOW

    new_user = User(
        username=data.username.lower(),
        username_display=data.username,
        email=register_user.email,
        avatar_index=str(data.avatar),
        pw_hash=pw_hash,
        team=data.team,
        team_leader=data.team_leader,
        team_color= selected_color,
    )

    await new_user.create()
    asyncio.create_task(register_user.delete())  # noqa

    login_data = await login_user(UserAuth(
        username=data.username.lower(), password=data.password, team=data.team, team_leader=data.team_leader
    ))

    return Response(
        content=json.dumps(login_data),
        status_code=201
    )

@router.post("/reset_password/{token}")
async def reset_password_complete(token: str, data: ResetPWAuth):
    
    reset_pw_user = await OnResetUserPW.find_one(OnResetUserPW.token == token)
    if reset_pw_user is None:
        raise HTTPException(status_code=404, detail="Invalider Token")

    if reset_pw_user.timeout < datetime.now():
        raise HTTPException(status_code=403, detail="Token abgelaufen, fordere einen neuen an")

    existing_user = await User.find_one(User.email == reset_pw_user.email)
    if existing_user is None:
        raise HTTPException(status_code=402, detail="User nicht registriert") # sollte nie vorkommen

    decoded_pw = base64.urlsafe_b64decode(data.password).decode()
    pw_hash = await asyncio.get_event_loop().run_in_executor(None, argon2.PasswordHasher().hash, decoded_pw)

    existing_user.pw_hash = pw_hash

#    change_user = User(
#        username=existing_user.username,
#        username_display=existing_user.username_display,
#        email=reset_pw_user.email,
#        avatar_index=existing_user.avatar_index,
#        pw_hash=pw_hash,
#    )

#    await change_user.create()
    await existing_user.save()
    
    asyncio.create_task(reset_pw_user.delete())  # noqa

    login_data = await login_user(UserAuth(
        username=existing_user.username.lower(), password=data.password, team=existing_user.team, team_leader=existing_user.team_leader
    ))

    return Response(
        content=json.dumps(login_data),
        status_code=201
    )





@router.post("/login")
async def login_user(data: UserAuth):
    user = await User.find_one(User.username == data.username.lower())
    if user is None:
        raise HTTPException(status_code=401, detail="Benutzername oder Passwort ist inkorrekt")

    try:
        decoded_pw = base64.urlsafe_b64decode(data.password).decode()
        await asyncio.get_event_loop().run_in_executor(
            None, argon2.PasswordHasher().verify, user.pw_hash, decoded_pw
        )
    except argon2.exceptions.VerifyMismatchError:
        raise HTTPException(status_code=401, detail="Benutzername oder Passwort ist inkorrekt")

    # username and password match:
    token = access_security.create_access_token(
        {"username": user.username.lower()},
        unique_identifier=user.username,
    )

    return {
        "token": token,
        "display_name": user.username_display,
        "avatar_index": user.avatar_index,
        "team": user.team,
        "team_leader": user.team_leader,
    }


@router.get("/login/token_valid")
async def check_username(
        auth: JwtAuthorizationCredentials = Security(access_security)
) -> str:
    return auth.subject.get("username", "??")
