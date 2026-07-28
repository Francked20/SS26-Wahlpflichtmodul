# core/backend/database

Beanie (async Mongo ODM) models and the DB connection singleton.

- **connection.py** — `MongoDB` class, single instance (`MongoDB.instance`, set
  up in `utils/lifespan.py`). Builds the Mongo URI from
  `MONGO_INITDB_ROOT_USERNAME`/`_PASSWORD` + `MONGO_DB` env vars. `connect_mapper()`
  registers all Document models with Beanie. `broadcast_score_update(user)` pushes
  a score update to every connected websocket (`endpoints/websockets.py`'s
  `score_sockets` list) — called after every solve/reset.

- **models.py** — all Document/embedded models:
  - `EventConfig` — single-document collection holding every event-wide toggle
    (event enabled, registration, preregister mode, badges, player levels/ranks,
    team-event mode, stats/scoreboard display flags, show-answers, task-reset,
    test mode). One classmethod pair (`enable_x`/`disable_x` or `get_x`/`set_x`)
    per flag — this is what `endpoints/admin.py` exposes over HTTP.
  - `User` — username/email/pw_hash/team/avatar + embedded `UserStats` (points,
    challenges_solved, streak, first_solves, badges).
  - `Challenge` — the static definition of a task (day/task id, points, question
    text, options, `solutions` (str | list[str] | list[list[str]] depending on
    randomization), hints, `task_type` in {input, select, multiple, regex}).
    Answer-checking logic lives here: `check_answer()`, `delete_answer()` (reset),
    `request_hint()`, `request_random_index()`. Supports per-user randomized
    variants (`allow_random_order` → `random_index`) and "master tasks" whose
    flag is assembled from words extracted from other ("slave") challenges'
    flags via `assemble_master_flag`/`extract_word_from_flag`. First-blood is
    awarded with an atomic conditional update to avoid race conditions on
    simultaneous solves. Optional `dynamic_check` field (day-3 export-cipher
    challenge): when set, `check_answer()` skips the normal `solutions[]`
    comparison and instead awaits `utils/export_cipher_client.check_dynamic_answer()`
    — an HTTP call to `custom/challengebackend`, which owns the actual variant
    data/verification logic — then falls through into the same
    points/streak/first-blood/broadcast path as every other task.
  - `RunningChallenge` — per-(user, challenge) progress: tries, resets, solved,
    points_earned, hints_gotten, random_index. Created lazily (and in bulk via
    `endpoints/users.py`'s `/initialize_challenges`).
  - `OnRegisterUser` / `OnResetUserPW` / `OnPreRegisterUser` — short-lived token
    documents for the email-verification registration/reset flow.
  - `CollectedData` — empty placeholder Document (collection exists, unused).

`regex` is a declared `task_type` but `check_answer()` raises
`NotImplementedError` for it — not implemented yet.
