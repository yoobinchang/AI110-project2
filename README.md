# PawPal+ (Project 2)

**PawPal+** is a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

## What the app does

- Enter basic owner and pet information
- Add and edit care tasks with a duration, priority, and optional start time
- Generate a daily plan that fits tasks into the owner's time budget by priority
- Display the plan clearly and warn about any scheduling conflicts

## ✨ Features

PawPal+ implements the following scheduling algorithms (all in `pawpal_system.py`):

- **Priority-based daily planning** — `Scheduler.generate()` greedily fills the owner's daily time budget, placing the highest-priority tasks first and breaking ties by shortest duration, so the most important care still fits when time is tight.
- **Sorting by time** — `Scheduler.sort_by_time()` orders tasks by their `"HH:MM"` start time using a **numeric** minute-of-day comparison (so `"9:00"` sorts before `"10:00"`, which a plain string sort gets wrong). Untimed tasks are pushed to the end.
- **Conflict warnings** — `Scheduler.detect_conflicts()` treats each task as a half-open interval `[start, start + duration)` and flags any overlap. It distinguishes a **same-pet** conflict ("Ari can't do two things at once") from a **cross-pet** one ("you can't be with Zimba and White at the same time"), and never crashes on missing/invalid times. A sweep-line early-exit keeps the common case near O(n log n).
- **Daily & weekly recurrence** — `Task.mark_complete()` auto-spawns the next occurrence of a `daily`/`weekly` task with a fresh due date computed by `Task.next_due_date()` (via `datetime.timedelta`, so month-ends and leap years are handled correctly). Non-recurring tasks spawn nothing.
- **Filtering** — `Scheduler.filter_tasks()` narrows tasks by pet name and/or completion status, combined with AND logic (each filter is optional).
- **Time-aware display** — `Schedule.display()` places each task at its own chosen start time rather than repacking from 08:00, and lists any conflict warnings beneath the plan.

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:

```
# e.g.:
# Daily plan for Biscuit (Golden Retriever):
#   08:00 — Morning walk (30 min) [priority: high]
#   09:00 — Feeding (10 min) [priority: high]
#   ...
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
python -m pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
============================= test session starts ==============================
platform darwin -- Python 3.14.0, pytest-9.0.3, pluggy-1.6.0
rootdir: .../ai110_project_2/AI110-project2
plugins: anyio-4.13.0
collected 32 items

tests/test_pawpal.py::test_mark_complete PASSED                          [  3%]
tests/test_pawpal.py::test_mark_complete_spawns_next_daily PASSED        [  6%]
tests/test_pawpal.py::test_mark_complete_spawns_next_weekly PASSED       [  9%]
tests/test_pawpal.py::test_mark_complete_non_recurring PASSED            [ 12%]
tests/test_pawpal.py::test_spawned_task_inherits_fields_but_resets_completed PASSED [ 15%]
tests/test_pawpal.py::test_next_due_date_defaults_to_today PASSED        [ 18%]
tests/test_pawpal.py::test_mark_complete_orphan_task_no_pet PASSED       [ 21%]
tests/test_pawpal.py::test_mark_complete_chains PASSED                   [ 25%]
tests/test_pawpal.py::test_add_task_increases_count PASSED               [ 28%]
tests/test_pawpal.py::test_sort_by_time_chronological PASSED             [ 31%]
tests/test_pawpal.py::test_sort_by_time_numeric_not_lexicographic PASSED [ 34%]
tests/test_pawpal.py::test_sort_by_time_empty PASSED                     [ 37%]
tests/test_pawpal.py::test_sort_by_time_midnight_before_untimed PASSED   [ 40%]
tests/test_pawpal.py::test_sort_by_time_untimed_and_malformed_last PASSED [ 43%]
tests/test_pawpal.py::test_sort_by_time_does_not_mutate_input PASSED     [ 46%]
tests/test_pawpal.py::test_detect_conflicts_overlap PASSED               [ 50%]
tests/test_pawpal.py::test_detect_conflicts_duplicate_time PASSED        [ 53%]
tests/test_pawpal.py::test_detect_conflicts_none PASSED                  [ 56%]
tests/test_pawpal.py::test_detect_conflicts_boundary_touch PASSED        [ 59%]
tests/test_pawpal.py::test_detect_conflicts_ignores_untimed PASSED       [ 62%]
tests/test_pawpal.py::test_detect_conflicts_empty PASSED                 [ 65%]
tests/test_pawpal.py::test_detect_conflicts_message_wording PASSED       [ 68%]
tests/test_pawpal.py::test_generate_orders_by_priority_then_duration PASSED [ 71%]
tests/test_pawpal.py::test_generate_excludes_completed PASSED            [ 75%]
tests/test_pawpal.py::test_generate_skips_too_big_keeps_smaller PASSED   [ 78%]
tests/test_pawpal.py::test_generate_exact_fit PASSED                     [ 81%]
tests/test_pawpal.py::test_generate_owner_no_pets PASSED                 [ 84%]
tests/test_pawpal.py::test_generate_zero_budget PASSED                   [ 87%]
tests/test_pawpal.py::test_generate_populates_conflict_warnings PASSED   [ 90%]
tests/test_pawpal.py::test_display_empty PASSED                          [ 93%]
tests/test_pawpal.py::test_display_places_timed_then_chains_untimed PASSED [ 96%]
tests/test_pawpal.py::test_display_task_without_pet PASSED               [100%]

============================== 32 passed in 0.02s ==============================
```

## Confidence level - ★★★★☆ (4 out of 5 stars)

The documented core behavior logics are well-covered and all passing across all the edge cases - recurrence, sorting, conflict detection. 32 deterministic tests in total run in 0.02s. For the parts under test, I feel confident.

However, there are some gaps in the test coverage that keep it from 5 stars. `filter_tasks()` has no tests, malformed times like `"25:00"` are parsed as valid instead of rejected, there's no input validation (negative durations/budgets, empty names), and one test reads the real system clock. So the documented core logic is proven reliable, but the edges of the input space aren't yet.


## 📐 Smarter Scheduling

Beyond the basic greedy plan, PawPal+ adds four scheduling features. All of them live in `pawpal_system.py`.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Sorting by time | `Scheduler.sort_by_time()` | Orders tasks by `start_time`, earliest first |
| Filtering | `Scheduler.filter_tasks()` | By pet name and/or completion status |
| Conflict detection | `Scheduler.detect_conflicts()` | Warns on overlapping time slots (never crashes) |
| Recurring tasks | `Task.mark_complete()` + `Task.next_due_date()` | Daily/weekly tasks respawn on completion |

### Sorting behavior — `Scheduler.sort_by_time()`

Returns a new list of tasks ordered by their `start_time` (an `"HH:MM"` string),
earliest first. It sorts on the shared `_time_key()` helper, which converts
`"HH:MM"` into minutes-of-day so the comparison is **numeric** — this is why
`"9:00"` correctly sorts *before* `"10:00"` (a plain string sort would not).
Tasks with no `start_time` are pushed to the end. The input list is left
unchanged. `Schedule.display()` uses the same key so the printed plan places each
task at its own chosen time instead of repacking from 08:00.

### Filtering behavior — `Scheduler.filter_tasks()`

```python
scheduler.filter_tasks(tasks, completed=False)              # only unfinished
scheduler.filter_tasks(tasks, pet_name="Zimba")            # only one pet
scheduler.filter_tasks(tasks, pet_name="Zimba", completed=False)  # both (AND)
```

Each filter is optional (`None` = "don't filter on this"). A task is kept only if
it passes **every** active filter, so filters combine with AND logic. Returns a
new list, so filters chain cleanly into `sort_by_time()`.

### Conflict detection logic — `Scheduler.detect_conflicts()`

Each task occupies the interval `[start, start + duration)`. Two tasks conflict
when their intervals overlap. The method returns a list of human-readable warning
strings (empty if there are none) and **never raises** — tasks with a missing or
invalid `start_time` are simply skipped. It distinguishes a same-pet conflict
("Ari can't do two things at once") from a cross-pet one ("you can't be with Ari
and Zimba at the same time"). For efficiency the timed tasks are sorted by start
time so the inner scan stops early once a later task starts after the current one
ends, keeping the common case close to O(n log n). `Scheduler.generate()` runs
this automatically and stores the result in `Schedule.warnings`, which
`Schedule.display()` prints under the plan.

### Recurring task logic — `Task.mark_complete()` + `Task.next_due_date()`

When a `daily` or `weekly` task is marked complete, `mark_complete()` creates the
next occurrence automatically: a fresh `Task` with the same details,
`completed=False`, and a new due date, attached to the same pet. The new date is
computed by `next_due_date()` using `datetime.timedelta` (`+1` day for daily,
`+7` for weekly), which handles month-ends and leap years correctly (e.g.
`2024-01-31` → `2024-02-01`). The `RECURRENCE_DAYS` map defines which frequencies
repeat; non-recurring tasks (e.g. `"once a month"`) return `None` and spawn
nothing.

## 🎬 Demo Walkthrough

### The interface

Launch the app with `streamlit run app.py`. The page is organized top-to-bottom as a single workflow:

- **Owner** — set the owner's name and a **daily time budget** (in minutes). The budget is the constraint the planner fits tasks into.
- **Add a pet** — enter a name and pick a species, then **Add pet**. You can add as many pets as you like.
- **Tasks** — choose a pet, then add a task with a title, duration, priority (low/medium/high), and an **optional fixed start time**. The start time is what enables time-sorting and conflict detection; leave it off for a flexible "untimed" task.
- **Current tasks** — a live table of every task, with dropdowns to **filter by pet** and **by status** (all / incomplete / completed). The table is always sorted by start time.
- **Build Schedule** — press **Generate schedule** to produce the day's plan as a table, with **Planned time vs. Daily budget** shown as metrics and any **conflict warnings** listed directly beneath.

### Example workflow

1. Set the owner's daily budget to `120` minutes.
2. **Add a pet** — "Ari" (cat).
3. **Add a task** — "Feeding", 5 min, high priority, start time `08:00`.
4. **Add another task** — "Medicine", 10 min, high priority, also `08:00`.
5. Open **Current tasks** and filter to **Incomplete** — both tasks appear, sorted by time.
6. Press **Generate schedule** — the plan table appears, and because both tasks start at 08:00, an **amber conflict warning** shows underneath: *"Ari can't do two things at once."*
7. Edit one task's start time to `08:10` and regenerate — the warning clears and you get a green **"No scheduling conflicts"** confirmation.

### Key Scheduler behaviors on display

- **Sorting** — tasks entered out of order (e.g. `19:30`, `08:00`, `07:15`) come back earliest-first, with untimed tasks last.
- **Filtering** — the status/pet dropdowns call `filter_tasks()` to show just what you asked for.
- **Priority + budget** — the plan fits the highest-priority tasks into the budget first; anything that doesn't fit is skipped.
- **Conflict warnings** — overlapping times are flagged as same-pet or cross-pet, in plain language.
- **Recurrence** — completing a daily/weekly task spawns its next occurrence automatically.

### Sample CLI output

`main.py` is a scripted end-to-end demo that seeds three pets with intentionally out-of-order, overlapping, and pre-completed tasks, then exercises each Scheduler method. Running it (`python main.py`) produces:

```text
1) Sorted by time:
  [ ]  7:15  Walking (Zimba)
  [ ] 08:00  Feeding (Ari)
  [ ] 08:00  Medicine (Ari)
  [x]  9:00  Feeding (White)
  [ ] 10:30  Nail trim (White)
  [ ] 12:00  Brushing (Zimba)
  [ ] 12:10  Vet visit (White)
  [ ] 16:45  Playing (White)
  [x] 18:00  Feeding (Zimba)
  [ ] 19:30  Shower (Ari)
  [ ]  None  Buy clothes (Ari)

5) Zimba's incomplete tasks, sorted by time:
  [ ]  7:15  Walking (Zimba)
  [ ] 12:00  Brushing (Zimba)

6) Conflict check (all tasks):
  ⚠️  Conflict: 'Feeding' (08:00, 5 min) overlaps 'Medicine' (08:00, 10 min) — Ari can't do two things at once.
  ⚠️  Conflict: 'Brushing' (12:00, 15 min) overlaps 'Vet visit' (12:10, 30 min) — you can't be with Zimba and White at the same time.

Daily plan for Yoobin Chang (budget: 120 min):

  07:15 — Walking for Zimba (30 min) [priority: high]
  08:00 — Feeding for Ari (5 min) [priority: high]
  08:00 — Medicine for Ari (10 min) [priority: high]
  12:00 — Brushing for Zimba (15 min) [priority: medium]
  12:10 — Vet visit for White (30 min) [priority: high]
  16:45 — Playing for White (10 min) [priority: medium]
  19:30 — Shower for Ari (20 min) [priority: medium]

Total: 120 min

Warnings:
  ⚠️  Conflict: 'Feeding' (08:00, 5 min) overlaps 'Medicine' (08:00, 10 min) — Ari can't do two things at once.
  ⚠️  Conflict: 'Brushing' (12:00, 15 min) overlaps 'Vet visit' (12:10, 30 min) — you can't be with Zimba and White at the same time.
```

*(Sections 0, 2, 3, and 4 — raw insertion order and the other filter combinations — are omitted here for brevity; run `python main.py` to see the full output.)*
