# core/backend/endpoints

Route handlers, one module per router (all mounted in `main.py`).

- **auth.py** — `/register`, `/register_complete/{token}`, `/reset_pw`,
  `/reset_password/{token}`, `/login`, `/login/token_valid`. Email-token
  registration flow (link sent via SMTP, `send_registration_token_SMTP_SSL`),
  argon2 password hashing (password arrives base64-encoded from the client,
  decoded then hashed), JWT issued on login (`utils.security.access_security`).

- **admin.py** — `X-Admin-Token`-protected GET/POST pairs for every
  `EventConfig` flag (event enabled, registration open, preregister mode,
  badges, player levels/ranks, stats/scoreboard display options, team-event
  mode, show-answers, task-reset, test mode) plus `/event/preregister_user`.
  This is what `CTF_Utils/event_config_script.py` drives.

- **challenges.py** — `/challenges/solve`, `/reset`, `/hint`, `/all_ch_data`,
  `/export_cipher_reveal_factor`. Thin wrappers around `Challenge` methods in
  `database/models.py` (JWT-authed, username taken from the token, not the
  request body). `/solve` adds a `reveal_factor` key to its response when the
  solved task is the day-3 export-cipher chain's `export_factor256` stage —
  fetched from `custom/challengebackend` via
  `utils/export_cipher_client.get_reveal_factor()`, same "extra work after a
  successful solve" pattern as the cyber-range flag injection in
  `reset_challenge` below. `/export_cipher_reveal_factor?day=&task=` lets a
  player re-fetch that same reward after a page reload (checks
  `RunningChallenge.solved` for the given day/task before calling out again —
  `/solve`'s `reveal_factor` is otherwise only ever seen once, transiently).
  The day-4 weak-DH chain uses the same `Challenge.check_answer()` dispatch
  (see `database/CLAUDE.md`) but has no reveal-on-solve reward of its own, so
  it doesn't touch this response-shaping logic at all.

- **users.py** — largest module. Mounted at `/user/{username}`. Score/rank/level
  lookup (`/score`, `/level`, `/get_stats`), team info, `/initialize_challenges`
  (creates `RunningChallenge` docs for a user + optionally pushes flags to the
  Cyber Range), `/challenges_dataset/{day}/{task}` (the main per-task payload
  the frontend renders: question, options, hints unlocked, solution text once
  solved — handles master/slave "assemble flag from other flags" tasks).
  Team-leader mode: `_resolve_effective_username` redirects a non-leader's
  progress/answers to their team leader's `RunningChallenge` records.

- **teams.py** — single endpoint, `/{team_name}/leader_exists`.

- **websockets.py** — `/ws/subscribe/scores` websocket. Pushes full scoreboard
  state on connect, then a heartbeat every 10s; `database/connection.py` calls
  back into `_badges_to_str`/the socket list here to broadcast live score
  updates on solve/reset.

- **container.py** — JWT-protected `/container/code/*` and `/container/kali/*`
  (start/stop/status/extend/inject_challenge_pvc). Provisions per-user
  Deployment+PVC+Ingress in Kubernetes via `utils/kubernetes.py` builders,
  TTL-based (6h) auto-expiry baked into resource annotations.

- **cyberrange.py** — only registered if `ENABLE_CYBER_RANGE=true`. Talks to an
  external "Cyber Range" HTTP API (`CYBER_RANGE_BASE_URL`, `X-API-Key` header)
  to create/destroy/reset per-user lab instances and inject per-task flags
  (`/inject_flag`, called from `challenges.py`'s `/reset` too).

Shared helper duplicated across `challenges.py`/`users.py`/`database/models.py`:
`assemble_master_flag`/`extract_word_from_flag` — builds a "master" flag out of
words extracted from other ("slave") challenges' flags for that day.
