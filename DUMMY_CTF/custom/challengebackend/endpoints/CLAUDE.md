# custom/challengebackend/endpoints

Each module (except `dh_export.py`/`export_cipher.py`) is a standalone crypto
challenge with its own hardcoded key/flag list, indexed by `{index}` in the
URL (one variant per team/player to prevent flag sharing) — no shared code
between modules.

- **primes.py** — `GET /{index}/prime/{prime}/` and `/{index}/safe_prime/{safe_prime}/`.
  Player submits a number as a decimal string; server checks exact bit-length
  (`4120+index` / `1120+index` bits) and primality (Miller-Rabin,
  `is_probable_prime`, k=10 rounds) — for safe primes also checks `(p-1)/2` is
  prime. Returns `FLAGS_PRIME[index]` / `FLAGS_SAFEPRIME[index]` on success.

- **ecbcbcwtf.py** — AES challenge. `GET /{index}/decrypt/{ciphertext}/` decrypts
  hex ciphertext with a fixed per-index AES-ECB key (no auth — the whole point
  is that ECB is deterministic/malleable). `GET /{index}/encrypt_flag/` encrypts
  that index's flag with AES-CBC + random IV (`iv_hex + ciphertext_hex`) so the
  player can compare ECB vs CBC behavior.

- **ecb_oracle.py** — classic ECB byte-at-a-time oracle. `GET /{index}/encrypt/{plaintext}/`
  takes hex-encoded player-chosen plaintext, appends the secret flag, encrypts
  with AES-ECB, returns the ciphertext hex — the flag itself is never returned
  directly, it must be recovered via the oracle.

All three sets of `KEYS`/`FLAGS` arrays are plain hardcoded constants in the
module (dummy/example values for this template) — replace per-event when
forking.

- **dh_export.py** — day-4 weak-Diffie-Hellman (Logjam-style) challenge chain,
  backed by Mongo. Same shape as `export_cipher.py` below: `GET /variant/{username}`
  and `POST /{index}/start_capture` are public, `POST /check_answer` and
  `GET /vm_replay_data` are internal-only (`require_challenge_api_key`),
  called by `core/backend`'s `Challenge.check_answer()` via
  `core/backend/utils/dh_export_client.py`. `start_capture` targets
  `DH_EXPORT_VM_HOST`/`_PORT`, which aren't set in `.env` (pre-existing gap),
  so it currently always 503s. No reveal-factor endpoint (unlike export-cipher).

- **export_cipher.py** — day-3 FREAK-style challenge chain, backed by Mongo
  (unlike the other three modules). `GET /variant/{username}` and
  `POST /{index}/start_capture` are public (a player's own N, and the trigger
  for their own on-demand live-capture handshake, keyed by their deterministic
  variant index — see `../CLAUDE.md`). `start_capture` sends that variant to
  `EXPORT_CIPHER_VM_HOST/PORT` via `utils/export_cipher_sender.py`'s
  `send_variant_to_vm()` — 503 if the training VM isn't configured, 502 if
  unreachable. `GET /reveal_factor/{username}`, `POST /check_answer`,
  `GET /vm_replay_data` are internal-only, gated by `require_challenge_api_key`
  (`utils/security.py`) — called by `core/backend`'s `Challenge.check_answer()`
  (via `core/backend/utils/export_cipher_client.py`) and by
  `CTF_Utils/export_cipher_vm_listener.py` respectively, never by a player
  directly.
