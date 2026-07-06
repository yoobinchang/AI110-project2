# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

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
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
# Paste your pytest output here
```

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

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
