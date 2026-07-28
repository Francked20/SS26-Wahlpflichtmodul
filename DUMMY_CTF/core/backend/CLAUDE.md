# core/backend

FastAPI backend for the CTF platform ("Event Backend"). Entry point: `main.py`.

- Loads env vars via `dotenv.load_dotenv()` before anything else.
- `configure_logger()` (`utils/logger.py`) sets up stdout logging, level from `LOG_LEVEL`.
- `fastapi_lifespan` (`utils/lifespan.py`) connects to Mongo/Beanie and sets up
  Kubernetes API clients on `app.state` before serving requests.
- Routers mounted in `main.py`: `admin`, `container` (K8s sandboxes), `cyberrange`
  (only if `ENABLE_CYBER_RANGE=true`), `auth`, `challenges`, `users` (mounted at
  `/user/{username}`), `teams`, `websockets`.
- `/` redirects to `/docs` (FastAPI's auto-generated OpenAPI UI).

Subdirectories:
- `endpoints/` — route handlers, see `endpoints/CLAUDE.md`
- `database/` — Beanie/Mongo models and connection, see `database/CLAUDE.md`
- `utils/` — auth/security, logging, lifespan, Kubernetes helpers, see `utils/CLAUDE.md`

Auth model: player-facing routes require a JWT (`utils.security.access_security`,
`Authorization` header); admin-only routes require `X-Admin-Token: <ADMIN_SECRET>`
(`utils.security.require_admin_token`).
