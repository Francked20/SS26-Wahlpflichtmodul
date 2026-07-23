# CTF Platform

This repository contains the core codebase for the CTF platform.
It is intended to be used as a Git submodule in CTF projects.

All logic and programming related to the platform's functionality should be done within this repository.

## Architecture

The platform consists of four Docker containers:

1. Backend
    The backend container runs a FastAPI application that provides endpoints for actions such as submitting solutions, user authentication, and all other database-modifying operations.

2. Database
    A MongoDB container serves as the database, primarily storing user and challenge data.
    The backend interacts with it to perform data retrieval and updates.

3. Frontend
    The frontend is built using the Reflex framework, a Python-based abstraction for frontend development.
    Reflex consists of a backend that pushes updates to the client via WebSockets, and a frontend that serves the compiled HTML, CSS, and JavaScript.
    On startup, the frontend also connects to the database to update the challenge data.

4. Scoreboard
    The scoreboard is also implemented using the Reflex framework.
    When users visit the site, it connects to a WebSocket endpoint exposed by the backend.
    This allows real-time updates of the scoreboard as new solves are submitted.

```
                           ┌────────────────────────┐
                           │      Scoreboard        │
                           │ (Reflex Web Frontend)  │
                           └────────┬───────────────┘
                                    │
                                    ▼  WebSocket (solves)
                           ┌────────────────────────┐
                           │        Backend         │◄────┐
                           │     (FastAPI API)      │     │
                           └───────┬────────────────┘     │
              REST API (auth,      │    ▲                 │
            submit, etc.)          ▼    │                 │
                           ┌────────────┴───────────┐     │
                           │       Frontend         │     │
                           │    (Reflex Website)    │     │
                           └────────┬───────────────┘     │
                                    │                     │
                        CHALLENGE INIT (on startup)       │
                                    ▼                     │
                           ┌────────────────────────┐     │
                           │       Database         │◄────┘
                           │        (MongoDB)       │
                           └────────────────────────┘

```