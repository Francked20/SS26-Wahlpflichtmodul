# custom/challengebackend

FastAPI service ("Challenge Backend") for challenges that need
**dynamic/computed verification** instead of a static string match against
`Challenge.solutions` in Mongo (that static path is handled entirely by
`core/backend`, this service is never called for those tasks). Owns all
event-specific, stateful challenge logic — `core/backend` is meant to stay
generic/forkable, so anything challenge-specific belongs here, not there.

- `main.py` — app setup, `lifespan=challenge_backend_lifespan` (see
  `lifespan.py`), `/ping/` healthcheck, mounts routers from `endpoints/` under
  `/primes`, `/ecbcbcwtf`, `/ecb_oracle`, `/export_cipher`.
- `database.py` — Mongo/Beanie connection (via **Motor**, not pymongo's newer
  async client — this service pins `beanie==1.30.0`+`motor==3.7.1`, and 1.x
  beanie needs Motor). Only used by the export-cipher subsystem so far;
  `primes.py`/`ecbcbcwtf.py`/`ecb_oracle.py` remain fully stateless.
- `lifespan.py` — connects Mongo at startup, disconnects at shutdown.
- Most challenge endpoints have **no auth**: each route validates the
  player's submitted value server-side (primality test, correct decryption,
  etc.) and only returns a flag if the check passes. The export-cipher
  subsystem's *internal-only* endpoints (called by core/backend or the VM
  companion script, never by a player directly) are the exception — gated by
  `utils/security.py`'s `require_challenge_api_key` (`X-Challenge-Api-Key`
  header vs. the `CHALLENGE_API_KEY` env var, previously declared but unused).
  See `endpoints/CLAUDE.md`.
- Runs as the `challenge` service in docker-compose (`depends_on: mongo`),
  reverse-proxied by Caddy at `CHALLENGE_DOMAIN`.

## Export-cipher (day 3, FREAK-style) subsystem

- `utils/export_cipher_crypto.py` — pure-Python TLS 1.0 RSA_EXPORT handshake
  engine (RFC 2246): RSA keygen, minimal X.509 DER cert builder, RC4, the TLS
  1.0 PRF, handshake/record framing, `craft_variant()` (builds one variant's
  4 flight byte-blobs) and `decrypt_as_attacker()` (independently re-derives
  the master secret/flag from just the wire bytes + recovered factors — used
  by the verification script to prove the crafted bytes are genuinely
  decryptable, not just self-consistent by construction).
- `utils/export_cipher_pool.py` — generates one dataset entry (256-bit
  practice N/p/q, 512-bit N/p/q, flag, crafted flights) via the crypto
  engine; `variant_index_for_user(username)` (`sha256(username) % 100`, pure
  function, no persistence) links every stage of one player's chain to the
  same pool entry; the four `check_*` comparators used by
  `endpoints/export_cipher.py`.
- `utils/export_cipher_sender.py` — `send_variant_to_vm()`, called on demand
  by `endpoints/export_cipher.py`'s `POST /{index}/start_capture` (the
  player's "Gestartet" button on `challenge_03.py`): opens a real TCP
  connection to `EXPORT_CIPHER_VM_HOST:PORT` (env, unset by default), sends a
  2-byte variant-index preamble followed by that variant's client-role
  flights, so a participant can capture their own, self-contained live
  traffic on the training VM with Wireshark. No periodic/background sender
  anymore — replaced because a shared round-robin through all ~100 variants
  mixed other players' traffic into everyone's capture.
- `scripts/generate_export_cipher_pool.py` — one-off operator script,
  populates the ~100-entry `ExportCipherVariant` pool. Run manually:
  `docker compose exec challenge python3 scripts/generate_export_cipher_pool.py`.
- `scripts/verify_export_cipher_crypto.py` — standalone verification script
  (no test framework in this repo), run manually to sanity-check the crypto
  engine after any change to it.

To add a new dynamic challenge: add a module under `endpoints/`, define its
`router`, register it in `main.py`.
