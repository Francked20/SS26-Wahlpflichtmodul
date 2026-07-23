# DUMMY_CTF

Runnable CTF platform (docker-compose stack). `core/` is a git submodule (generic
platform code, upstream: TH Deggendorf GitLab). `custom/` holds this event's
content (challenge text, flags, assets, site pages) and is bind-mounted
read-only into `site`/`scoreboard` at startup — that's the customization boundary.

## Services (docker-compose.yaml)

All on one internal `ctf-net` network, fronted by Caddy (`webserver`, TLS,
subdomain routing via `DOMAIN`/`API_DOMAIN`/`SCR_DOMAIN`/`CHALLENGE_DOMAIN`):

- `mongo` — single DB, auth enabled, port 27017 also exposed to host (dev only)
- `api` (`core/backend`) — FastAPI backend, see `core/backend/CLAUDE.md`
- `site` (`core/site` + `custom/`) — Reflex player-facing frontend
- `scoreboard` (`core/scoreboard` + `custom/`) — Reflex live scoreboard
- `challenge` (`custom/challengebackend`) — FastAPI dynamic challenge
  verification, see `custom/challengebackend/CLAUDE.md`. Owns all
  event-specific stateful challenge logic (currently: the day-3 export-cipher
  chain) — has its own Mongo/Beanie connection (`depends_on: mongo`), unlike
  `api`'s generic platform DB.

## Environment variables / secrets

- Single `.env` at repo root, injected into every service via `env_file: - .env`
  in docker-compose. No secrets manager/vault/Docker secrets.
- Every Python service calls `dotenv.load_dotenv()` at startup and reads values
  with plain `os.getenv(...)`.
- Secrets: `JWT_SECRET` (generate with `CTF_Utils/generate_JWT_SECRET.py`),
  `ADMIN_SECRET` (protects `core/backend`'s `/admin` router) /
  `CHALLENGE_API_KEY` (protects `custom/challengebackend`'s internal-only
  export-cipher endpoints — `core/backend` and
  `CTF_Utils/export_cipher_vm_listener.py` are the only two callers),
  `MONGO_INITDB_ROOT_USERNAME/PASSWORD`, `SMTP_SSL_*`.
- `core/backend/utils/security.py` and `custom/challengebackend/utils/security.py`
  both hard-fail at import time (`RuntimeError`) if their respective secrets
  (`JWT_SECRET`/`ADMIN_SECRET`; `CHALLENGE_API_KEY`) are missing — the only
  startup validation.
- `EXPORT_CIPHER_VM_HOST`/`_PORT` — day-3 export-cipher challenge's
  training-VM target; unset by default. Each player's "Gestartet" button on
  `challenge_03.py` triggers an on-demand send of THEIR variant to this
  host/port (`POST /export_cipher/{index}/start_capture`); if unset, that
  endpoint returns 503.
- `docs/DEPLOYMENT.md` says to rotate the JWT secret and the three credentials,
  and flip `SET_PRODUCTION_MODE=True`, before going live — this is a template
  meant to be forked per event.
- ⚠️ `.env` is NOT in `.gitignore` (which only excludes `cert/*` and pycache).
  Current `.env` values here are dummy/local only. Add `.env` to `.gitignore`
  before this ever gets committed to a real repo.

## Admin/ops tooling

`../CTF_Utils/` (outside this folder) drives the running platform via the
`admin` router (`X-Admin-Token` header = `ADMIN_SECRET`) — see its own CLAUDE.md.
