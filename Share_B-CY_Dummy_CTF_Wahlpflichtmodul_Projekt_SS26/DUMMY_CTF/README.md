# CTF Template

This is a fully functional Template for the CTF Plattform.
This Repo contains a default config without any Challenges or Tasks.

# Architecture

```
.
├── cert/
├── core/ <- Submodule
├── custom/
│   ├── assets/
│   ├── sites/
│   ├── tasks/
│   └── task_conf.py
├── docs/
├── .env
└── docker-compose.yaml
```

The core folder contains the submodule with the code of the CTF Plattform.

The Custom Folder contains all of the Challenge, Task and Asset files for customization.
All of it is mounted into the Frontend Container at Startup.


# Running Locally

Set .env vars for using local urls to

```dotenv
# Main application
DOMAIN=app.localhost
# API
API_DOMAIN=api.localhost
# Scoreboard
SCR_DOMAIN=scr.localhost
```

Generate SSL certificates if not present yet

```bash
$ openssl req -x509 -newkey rsa:2048 -keyout ./certs/local.key -out ./certs/local.crt -sha256 -days 365 -nodes -subj "/CN=localhost"
```

Ensure that you have docker and docker compose installed

- **Starting**: 

  `$ docker compose up --build`

- **Starting without building**: 

  `$ docker compose up`

- **Stopping** (if in background): 

  `$ docker compose down`

- **Deleting all images**: 

  `$ docker compose down --rmi all`

- **Deleting all images and storage**: 

  `$ docker compose down --rmi all --volumes`
