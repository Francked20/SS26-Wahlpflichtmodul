"""Main entry point for the FastAPI application."""

import os

from dotenv import load_dotenv

# Load environment variables as early as possible
load_dotenv()

from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from utils.logger import configure_logger
from utils.lifespan import fastapi_lifespan

# Configure logging
configure_logger()

enable_cyber_range = os.getenv("ENABLE_CYBER_RANGE", "False").lower() == "true"

# Initialize FastAPI with lifespan context
app = FastAPI(title="Event Backend", lifespan=fastapi_lifespan)

# Redirect / to /docs
@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/docs")

# Routers
from endpoints import (
    admin,
    auth,
    challenges,
    users,
    teams,
    websockets,
    container,
    cyberrange,
)

# Register routers
app.include_router(admin.router, prefix="/admin", tags=["admin"])
app.include_router(container.router, prefix="/container", tags=["kubernetes"])
if(enable_cyber_range):
    app.include_router(cyberrange.router, prefix="/cyberrange", tags=["cyberrange"])
app.include_router(auth.router, tags=["auth"])
app.include_router(challenges.router, prefix="/challenges", tags=["challenges"])
app.include_router(users.router, prefix="/user/{username}", tags=["userdata"])
app.include_router(teams.router, prefix="/teams", tags=["teams"])
app.include_router(websockets.router, prefix="/ws/subscribe", tags=["websockets"])

# ToDo: Add rate limiter / API throttling
# ToDo: Add prefix for auth

# ToDo: fix login
# ToDo: unlock page on day, dummy story
# ToDo: setup docker frontend + nginx
# ToDo: data collect endpoint
# ToDo: 12x avatar selection
# ToDo: password reset?
# ToDo: docker compose