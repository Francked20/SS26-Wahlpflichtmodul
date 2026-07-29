# custom/sites/pages

Reflex pages for this event, each a class extending `AbstractSiteBuilder`
(`core/site/website/engine/site.py`) with a `page()` method (the UI) and a
`configure()` method (route/name/icon/color/auth requirements/unlock rules).
Registered automatically — `core/site/website/app.py` scans `CTF_WEBSITE_FOLDER`
(`.env`, default `/custom/sites/pages`) at startup.

- **challenge_01.py** — `/challenge_01` (`auth_required = True`). Body is
  nested `rx.cond(...)` blocks that only reveal task N+1 once
  `PlayerCardState.tasks_solved["day_XX_task_NN"]` is true (or
  `enable_test_mode`) — a manually hand-built linear unlock chain. Each task
  renders via `render_task(self.PAGE_ID, index, title, TaskWidget(task_XX_YY))`
  where `task_XX_YY` is imported from `../tasks/challenge_01_tasks.py`.

- **kap02_kurs.py** / **kap02_challenge_1.py**...**kap02_challenge_10.py** —
  "Kapitel 02" (small-prime discrete-log chain), `PAGE_ID = "challenge_02"`
  shared across all 11 pages (task-day namespace `day_02_task_XX`, 34 tasks
  total). Routes are `/challenge_02_kurs` (the landing/theory page) and
  `/challenge_02_c1`...`/challenge_02_c10` (NOT `/challenge_02` — there is no
  page at that exact route; `login_chapter_selection.py`'s "/challenge_02"
  redirect button is a pre-existing dangling link, not something introduced by
  merging in day-3/day-4). Shared story/theory text and DH-variant download
  helpers live in `kap02_shared/`. Tasks come from `../tasks/kap02_c*_tasks.py`
  (NOT `challenge_02_tasks.py` — that flat file is orphaned leftover from
  before this chapter was split into kap02_challenge_1..10, no page imports
  from it).

- **challenge_03.py** — `/challenge_03`, same unlock-chain pattern as
  `challenge_01.py` but with real content (day-3 FREAK-attack export-cipher
  chain, see `../tasks/challenge_03_tasks.py`). Also defines `MyVariantState` +
  `ChallengeBackendRequests` (a `BackendRequests` subclass pointed at
  `http://challenge:8000` instead of core/backend's `api:8000`) — fetches a
  player's assigned practice 256-bit N directly from `custom/challengebackend`
  (unauthenticated, keyed by username), since that data is per-player and
  can't go through the generic static `download_path` mechanism the other
  days use. The "Gestartet" button (`MyVariantState.trigger_capture`, a
  background event) calls `POST /export_cipher/{index}/start_capture` on the
  challenge backend, which sends that player's variant to the training VM on
  demand — the player is expected to have their own Wireshark capture running
  there first, so what they get is a real, self-captured, self-contained TLS
  conversation instead of a downloadable pcap. `MyVariantState` also
  re-fetches the `export_factor256` reward (a factor of the 512-bit N) from
  core/backend's `/challenges/export_cipher_reveal_factor` on every page load,
  so it survives a reload — `widget.py`'s `revealed_secret` only shows it
  once, transiently, right after solving.

- **challenge_04.py** — `/challenge_04`, day-4 weak-Diffie-Hellman
  (Logjam-style) chain, see `../tasks/challenge_04_tasks.py`. Structurally
  parallel to `challenge_03.py` (own per-player variant fetched from
  `custom/challengebackend`'s `dh_export` router instead of `export_cipher`),
  but has no reveal-on-solve reward UI.

- **challenge_03_beginner.py** — `/challenge_03_beginner`, `PAGE_ID =
  "challenge_03_beginner"`, own `day=95` task namespace (see
  `../tasks/CLAUDE.md`). Beginner-friendly walkthrough of the same day-3
  FREAK/export-cipher attack as `challenge_03.py` (same crypto, same
  variant pool/backend endpoints, unmodified) but with a "Was ist X?"
  `explain_box()` per concept, heavy step-by-step Wireshark instructions,
  and only 1-2 real conceptual gaps left in the provided code skeletons
  (everything else given). Own local UI helpers (`box`/`h`/`explain_box`/
  `checkpoint`/`success_box`/`pcap_download_button`, not shared with
  `challenge_03.py` — separate file, separate small helper set, see
  `kap02_shared/`'s note above on when sharing is/isn't worth it) and its
  own `BeginnerExportCipherState` (mirrors `MyVariantState`, calls the same
  unmodified `/export_cipher/variant/{username}` and
  `/export_cipher/{index}/start_capture` endpoints — `/variant/{username}`
  additionally returns `n512`, added for this page, see
  `../../challengebackend/CLAUDE.md`). Sidebar `group = "3_Beginner"`,
  `position_priority = 20`.

- **challenge_04_beginner.py** — `/challenge_04_beginner`, `PAGE_ID =
  "challenge_04_beginner"`, own `day=94` task namespace. Same
  beginner-walkthrough pattern as `challenge_03_beginner.py` above, but for
  the day-4 weak-Diffie-Hellman/Logjam chain (`challenge_04.py`'s
  underlying crypto/backend, unmodified) — own `BeginnerDhVariantState`,
  own local UI helpers (separate copy, not shared with the export-cipher
  beginner page). Sidebar `group = "3_Beginner"`, `position_priority = 10`
  (sorts above the export-cipher beginner page within the same group).

- **convo_01.py** / **convo_02.py** — `/char_01`, `/char_02`. Narrative/story
  pages ("Konversation") linked from the challenge pages.

- **login_chapter_selection.py** — `/login_chapter_selection`. Landing page
  users see to pick a day/chapter after login.

- **spielregeln.py** — `/spielregeln` ("the rules"). Static rules page, linked
  from `welcome.py` in `core/site`.

To add a new day: copy `challenge_03.py`/`challenge_04.py` + matching
`tasks/challenge_0X_tasks.py`, bump the page URL/day number/`PAGE_ID`, wire
the unlock chain to the new task keys. Pick an unused `PAGE_ID`/task-day
namespace — `kap02_*` already occupies `"challenge_02"`.
