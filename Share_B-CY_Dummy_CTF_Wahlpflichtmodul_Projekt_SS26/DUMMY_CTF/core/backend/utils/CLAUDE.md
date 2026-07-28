# core/backend/utils

Cross-cutting backend infrastructure, not tied to one router.

- **security.py** — reads `JWT_SECRET` and `ADMIN_SECRET` from env at import
  time; raises `RuntimeError` if either is missing (the only startup secret
  validation in the app). Exposes `access_security` (`JwtAccessBearer`, expiry
  from `JWT_EXPIRY_HOURS`, default 18h) used as a FastAPI `Security` dependency
  for player auth, and `require_admin_token` (checks `X-Admin-Token` header
  against `ADMIN_SECRET`) for admin routes.

- **lifespan.py** — `fastapi_lifespan`, the app's async context manager
  (registered in `main.py`). On startup: connects `MongoDB.instance`, pings it,
  registers Beanie models, then loads Kubernetes config (in-cluster first,
  falls back to local kubeconfig, else runs without K8s support) and stores
  `k8s_core_v1`/`k8s_apps_v1` clients on `app.state`. On shutdown: closes the
  Mongo connection.

- **logger.py** — `configure_logger()`, called once in `main.py`. Reads
  `LOG_LEVEL` env var, sets up a single stdout `StreamHandler` on the root
  logger.

- **kubernetes.py** — pure builder functions (no I/O) that return `kubernetes`
  client objects for the per-user sandbox containers used by
  `endpoints/container.py`: `make_codeserver_{pvc,ingress,deployment,service}`
  (VSCode-in-browser instances) and `make_kali_{ingress,deployment,service}`
  (Kali Linux instances), plus job builders (`make_injector_job*`) for one-shot
  jobs that inject challenge files into a user's PVC. `sanitize_k8s_name`/
  `generate_subdomain` (sha256(username)[:6]) keep resource names valid and
  per-user-unique.

- **export_cipher_client.py** — thin httpx client for the day-3 export-cipher
  challenge (`database/models.py`'s `Challenge.check_answer()` calls
  `check_dynamic_answer()` when `dynamic_check` is set; `endpoints/challenges.py`'s
  `/solve` calls `get_reveal_factor()` after a correct `export_factor256`
  answer). All the actual crypto/variant-pool logic lives in
  `custom/challengebackend` now, reached over the internal `ctf-net` network
  (`http://challenge:8000`, `X-Challenge-Api-Key` header) — same
  call-an-external-service pattern already used for the Cyber-Range API in
  `endpoints/cyberrange.py`. Fails closed (returns `False`/`None`) on both a
  non-200 response and a transport-level error (unreachable/timeout), so an
  unreachable challenge backend never 500s `/solve`.
