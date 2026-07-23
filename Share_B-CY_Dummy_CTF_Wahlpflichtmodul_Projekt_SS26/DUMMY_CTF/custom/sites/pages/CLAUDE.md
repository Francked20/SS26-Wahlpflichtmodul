# custom/sites/pages

Reflex pages for this event, each a class extending `AbstractSiteBuilder`
(`core/site/website/engine/site.py`) with a `page()` method (the UI) and a
`configure()` method (route/name/icon/color/auth requirements/unlock rules).
Registered automatically — `core/site/website/app.py` scans `CTF_WEBSITE_FOLDER`
(`.env`, default `/custom/sites/pages`) at startup.

- **challenge_01.py** / **challenge_02.py** — one page per day, `/challenge_01`
  and `/challenge_02` (`auth_required = True`). Body is nested `rx.cond(...)`
  blocks that only reveal task N+1 once `PlayerCardState.tasks_solved["day_XX_task_NN"]`
  is true (or `enable_test_mode`) — a manually hand-built linear unlock chain.
  Each task renders via `render_task(self.PAGE_ID, index, title, TaskWidget(task_XX_YY))`
  where `task_XX_YY` is imported from `../tasks/challenge_0X_tasks.py`.
  Content is currently placeholder ("Lorem Ipsum") — this is the dummy/template
  event, meant to be replaced per real event.

- **challenge_03.py** — `/challenge_03`, same unlock-chain pattern as above
  but with real content (FREAK-attack export-cipher chain, see
  `../tasks/challenge_03_tasks.py`). Also defines `MyVariantState` +
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

- **convo_01.py** / **convo_02.py** — `/char_01`, `/char_02`. Narrative/story
  pages ("Konversation") linked from the challenge pages.

- **login_chapter_selection.py** — `/login_chapter_selection`. Landing page
  users see to pick a day/chapter after login.

- **spielregeln.py** — `/spielregeln` ("the rules"). Static rules page, linked
  from `welcome.py` in `core/site`.

To add a new day: copy a `challenge_0X.py` + matching `tasks/challenge_0X_tasks.py`,
bump the page URL/day number, wire the unlock chain to the new task keys.
