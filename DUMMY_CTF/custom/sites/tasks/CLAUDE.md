# custom/sites/tasks

Challenge **content** for this event. `challenge_01_tasks.py` = day 1 / 10
tasks; "Kapitel 02" (small-prime discrete-log, 34 tasks) is split across
`kap02_c1_tasks.py`, `kap02_c23_tasks.py`, `kap02_c45_tasks.py`,
`kap02_c6_tasks.py`, `kap02_c7_tasks.py`, `kap02_c8_tasks.py`,
`kap02_c910_tasks.py` (one file per `kap02_challenge_N.py` page, see
`../pages/CLAUDE.md`) — `challenge_02_tasks.py` is an orphaned flat leftover
from before that split and is not imported by any page; `challenge_03_tasks.py`
= day 3 / 6 tasks (export-cipher); `challenge_04_tasks.py` = day 4 / 7 tasks
(weak-Diffie-Hellman). Each task is a module-level `TaskData(...)` instance
(model defined in `core/site/website/engine/tasks/models.py`), imported by
the matching page in `../pages/` and rendered there via
`render_task(...)`/`TaskWidget(...)`.

Key `TaskData` fields actually used here:
- `day`, `points`, `task_type` (`"input"`/`"select"`/`"multiple"`/`"regex"`),
  `error_cost`, `allow_reset`, `allow_random_order`, `master_task`
- `answers` — list of `Correct.create("flag{...}")` (or nested list per
  randomized variant); this is what gets synced into the `Challenge.solutions`
  field in Mongo on site startup
- `question`/`question_further`/`placeholder_text`/`download_*`/`link_*` — one
  entry per randomized variant (parallel arrays, same length/order as `answers`)
- `hints` — list of `TaskHint.create(variant_index, text, point_multiplier)`

`vm_name`/`flag_type`/`allow_cyber_range` (Cyber-Range flag injection, see
`core/backend/endpoints/cyberrange.py`) and `allow_kali`/`allow_vscode`
(K8s sandbox containers, see `core/backend/endpoints/container.py`) exist on
the model but are **not used by any task in this event** — plain flag-string
answers only.

`dynamic_check` (`challenge_03_tasks.py` and `challenge_04_tasks.py`) is a
different mechanism from all of the above: some of their tasks set this field
(day 3: `"export_factor256"`/`"export_factor512"`/`"export_master_secret"`/`"export_flag"`;
day 4: `"dh_factors"`/`"dh_server_secret"`/`"dh_master_secret"`/`"dh_flag"`)
instead of relying on `answers`/`solutions` at all (they still declare a
placeholder single-entry `answers=[Correct.create("dynamic")]` purely to
satisfy the model's validators — it's never actually compared against).
`core/backend/database/models.py`'s `Challenge.check_answer()` sees this
field, dispatches on the `"export_"`/`"dh_"` prefix, and delegates the real
check to `custom/challengebackend` over HTTP instead — see that service's
`CLAUDE.md`. The remaining tasks in each chapter (intro, "identify the weak
key size", etc.) are ordinary static-answer tasks like any day 1/2 task,
since their answer doesn't depend on which pool variant a player was
assigned.

Flags here follow the pattern `hiy{...}` (day-1 intro tasks); crypto challenges
under `custom/challengebackend/` use `crypto{...}` instead and are verified
dynamically rather than via `answers`/`solutions`.
