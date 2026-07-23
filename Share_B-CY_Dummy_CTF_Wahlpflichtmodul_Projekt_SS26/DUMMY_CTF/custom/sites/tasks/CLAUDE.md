# custom/sites/tasks

Challenge **content** for this event, one file per day
(`challenge_01_tasks.py` = day 1 / 10 tasks, `challenge_02_tasks.py` = day 2 /
7 tasks, `challenge_03_tasks.py` = day 3 / 6 tasks). Each task is a
module-level `TaskData(...)` instance (model defined in
`core/site/website/engine/tasks/models.py`), imported by the matching page
in `../pages/` and rendered there via `render_task(...)`/`TaskWidget(...)`.

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

`dynamic_check` (day 3 only, `challenge_03_tasks.py`) is a different
mechanism from all of the above: 4 of its 6 tasks set this field
(`"export_factor256"`/`"export_factor512"`/`"export_master_secret"`/`"export_flag"`)
instead of relying on `answers`/`solutions` at all (they still declare a
placeholder single-entry `answers=[Correct.create("dynamic")]` purely to
satisfy the model's validators — it's never actually compared against).
`core/backend/database/models.py`'s `Challenge.check_answer()` sees this
field and delegates the real check to `custom/challengebackend` over HTTP
instead — see that service's `CLAUDE.md`. The other 2 tasks (day-3 intro,
"identify the weak key size") are ordinary static-answer tasks like any day
1/2 task, since their answer doesn't depend on which pool variant a player
was assigned.

Flags here follow the pattern `hiy{...}` (day-1 intro tasks); crypto challenges
under `custom/challengebackend/` use `crypto{...}` instead and are verified
dynamically rather than via `answers`/`solutions`.
