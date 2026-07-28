# CTF_Utils

Standalone admin/ops scripts run *against* a running `DUMMY_CTF` deployment
(not part of the docker-compose stack itself, not deployed anywhere).

- **event_config_script.py** — CLI wrapping the `admin` router
  (`core/backend/endpoints/admin.py`) at `https://api.localhost/admin/event`
  (`BASE_URL`, hardcoded — edit for a real deployment). Auth via
  `ADMIN_API_TOKEN` env var, sent as `X-Admin-Token` (must match the backend's
  `ADMIN_SECRET`). Subcommands: `read` (dumps every `EventConfig` flag),
  `preregister`/`preregister_batch`, `set` (bulk-configure event flags/teams/
  badges/ranks/stats/scoreboard options in one call, several `--*_file` flags
  accept one of the `dummy_*.json` files below as input).

- **generate_JWT_SECRET.py** — prints a random 256-byte hex string
  (`secrets.token_hex`) to stdout; paste the output into `.env`'s `JWT_SECRET`.
  Referenced by `DUMMY_CTF/docs/DEPLOYMENT.md`'s "rotate the JWT secret" step.

- **user_inserts_helper.py** — generates `db.users.insertOne({...})` Mongo
  shell commands with a correctly argon2-hashed `pw_hash` (same hasher config
  as `core/backend/endpoints/auth.py`: `time_cost=3, memory_cost=65536,
  parallelism=4`), for manually seeding test/demo accounts + teams without
  going through the email-registration flow. Output pattern mirrors
  `Beispiel_Dummy_CTF_User_Inserts.txt`.

- **reset_task_progress.py** — connects directly to Mongo (`pymongo`, host's
  published `27017`, `MONGO_INITDB_ROOT_USERNAME`/`_PASSWORD`/`MONGO_DB` env
  vars) and deletes `user_challenges` (RunningChallenge) docs for a given
  `--day` (optionally `--username`), `--dry_run` to preview. Needed because
  `core/site/website/engine/tasks/meta.py`'s `MetaTask` identifies each task
  by a content hash: editing a task's text/points/etc in `custom/sites/tasks/`
  changes its hash, and if that edit lands while the sync's checksum set is
  incomplete (e.g. mid-edit reload), the old `challenges` doc gets deleted
  and recreated with a new ObjectId. Any pre-existing `user_challenges` doc
  still holds a DBRef to the old, now-gone ObjectId — `core/backend/endpoints/
  users.py`'s `get_uniform_challenge_status` doesn't null-check the resolved
  link and crashes with `AttributeError: 'NoneType' object has no attribute
  'allow_random_order'` (500, which the frontend then can't parse as JSON —
  the challenge page hangs/won't load). Run this after editing existing task
  content for a day a test user has already started; it clears their stale
  links so the next page load recreates them against the current `challenges`
  docs. Rule of thumb: run it for any day whose task file you just edited.

- **export_cipher_vm_listener.py** — companion script for the day-3
  export-cipher (FREAK-style) challenge's training VM, run manually once that
  VM exists (see `DUMMY_CTF/custom/challengebackend/CLAUDE.md`). Plays the
  "server" role of a mock TLS handshake back to `custom/challengebackend`'s
  on-demand sender (which plays "client", triggered per-player by the
  "Gestartet" button on `challenge_03.py`) — a dumb byte-blob player, fetches
  precomputed reply bytes once via `GET /export_cipher/vm_replay_data`
  (`CHALLENGE_API_KEY` env var, same value as in `DUMMY_CTF/.env`), no crypto
  of its own. Each connection starts with a 2-byte big-endian variant index
  sent by the sender, before any TLS bytes, so this script replies with the
  matching variant's server flights (not a round-robin guess) — needed
  because triggers are now on-demand/per-player rather than one shared
  sequential loop. Stdlib-only (`urllib`/`socket`) so it needs nothing
  installed on the VM beyond Python 3.

- **pcap_generator.py** — proof-of-concept, not wired into the challenge flow
  yet. Offline alternative to `export_cipher_vm_listener.py`'s live capture:
  writes a single `.pcap` (via `scapy`) containing one real TCP conversation
  with the day-3 export-cipher challenge's full 4-flight TLS handshake for a
  given `--index`, plus a couple of synthetic decoy conversations (plain
  HTTP, one DNS query/response) so the TLS flow isn't the only traffic in the
  capture. The challenge backend's HTTP API only ever exposes server-role
  flight hex (`GET /export_cipher/vm_replay_data`) — client-role flights
  never leave `custom/challengebackend/utils/export_cipher_sender.py`, so
  this instead reads the `export_cipher_variants` Mongo collection directly
  (`pymongo`, same host/port/env-var convention as `reset_task_progress.py`)
  to get all 4 flight fields for one variant at once.

- **dummy_badges.json** / **dummy_rank_config.json** /
  **dummy_scoreboard_options.json** / **dummy_stats_options.json** — example
  payloads for `event_config_script.py set --badges_file/--rank_config_file/
  --scoreboard_options_file/--stats_options_file`.

- **TCV CTF - HowTo.pdf** — human-readable setup/usage doc (not read by tooling).
