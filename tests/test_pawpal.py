from datetime import date, timedelta

from pawpal_system import Task, Pet, Owner, Schedule, Scheduler, Priority


# ---------------------------------------------------------------------------
# mark_complete / recurrence
# ---------------------------------------------------------------------------

# mark_complete verification
def test_mark_complete():
    task = Task("Feeding", 5, Priority.HIGH)
    assert task.completed is False        # starts not done
    task.mark_complete()
    assert task.completed is True         # flipped to done


# recurring: completing a daily task spawns the next occurrence on the pet
def test_mark_complete_spawns_next_daily():
    pet = Pet("Ari", "Persian Cat")
    task = Task("Feeding", 5, Priority.HIGH, "daily", due_date=date(2024, 1, 31))
    pet.add_task(task)

    next_task = task.mark_complete()

    assert task.completed is True                    # original is done
    assert next_task is not None                     # a new one was created
    assert next_task.completed is False              # and it's not done yet
    assert next_task.due_date == date(2024, 2, 1)    # +1 day, month-end handled
    assert next_task in pet.tasks                    # attached to the same pet
    assert len(pet.tasks) == 2                       # original + next occurrence


# recurring: weekly adds 7 days
def test_mark_complete_spawns_next_weekly():
    pet = Pet("White", "Maltese Dog")
    task = Task("Nail trim", 10, Priority.LOW, "weekly", due_date=date(2024, 2, 26))
    pet.add_task(task)

    next_task = task.mark_complete()

    assert next_task.due_date == date(2024, 2, 26) + timedelta(days=7)  # leap year


# non-recurring: completing does NOT spawn anything
def test_mark_complete_non_recurring():
    pet = Pet("Ari", "Persian Cat")
    task = Task("Buy clothes", 120, Priority.LOW, "once a month")
    pet.add_task(task)

    next_task = task.mark_complete()

    assert task.completed is True
    assert next_task is None                # nothing spawned
    assert len(pet.tasks) == 1              # still just the original


# recurrence edge: the spawned task inherits the details but is a fresh copy
def test_spawned_task_inherits_fields_but_resets_completed():
    pet = Pet("Ari", "Persian Cat")
    task = Task("Walk", 15, Priority.MEDIUM, "daily",
                start_time="09:00", due_date=date(2024, 5, 1))
    pet.add_task(task)

    nxt = task.mark_complete()

    assert nxt.name == "Walk"
    assert nxt.duration == 15
    assert nxt.priority is Priority.MEDIUM
    assert nxt.frequency == "daily"
    assert nxt.start_time == "09:00"        # inherited
    assert nxt.completed is False           # but reset
    assert nxt.pet is pet                   # back-reference set


# recurrence edge: no due_date -> anchors on today (asserted relative to today)
def test_next_due_date_defaults_to_today():
    task = Task("Feeding", 5, Priority.HIGH, "daily")   # no due_date
    assert task.next_due_date() == date.today() + timedelta(days=1)


# recurrence edge: an orphan task (no pet) still returns a next task, adds nowhere
def test_mark_complete_orphan_task_no_pet():
    task = Task("Feeding", 5, Priority.HIGH, "daily", due_date=date(2024, 1, 1))
    nxt = task.mark_complete()              # never attached to a pet

    assert task.completed is True
    assert nxt is not None                  # still spawned
    assert nxt.pet is None                  # but attached to no pet


# recurrence edge: completing the spawned task advances the date again
def test_mark_complete_chains():
    pet = Pet("Ari", "Persian Cat")
    task = Task("Feeding", 5, Priority.HIGH, "daily", due_date=date(2024, 1, 1))
    pet.add_task(task)

    second = task.mark_complete()
    third = second.mark_complete()

    assert second.due_date == date(2024, 1, 2)
    assert third.due_date == date(2024, 1, 3)
    assert len(pet.tasks) == 3


# ---------------------------------------------------------------------------
# add_task
# ---------------------------------------------------------------------------

# add_task verification : adding task increases a pet's task count
def test_add_task_increases_count():
    pet = Pet("Ari", "Persian Cat")
    assert len(pet.tasks) == 0            # no tasks yet

    pet.add_task(Task("Feeding", 5, Priority.HIGH))
    assert len(pet.tasks) == 1            # count went up by 1

    pet.add_task(Task("Shower", 20, Priority.MEDIUM))
    assert len(pet.tasks) == 2            # and up again


# ---------------------------------------------------------------------------
# Sorting correctness  (Scheduler.sort_by_time)
# ---------------------------------------------------------------------------

# happy path: tasks come back in chronological order, earliest first
def test_sort_by_time_chronological():
    scheduler = Scheduler()
    tasks = [
        Task("C", 5, Priority.LOW, start_time="10:00"),
        Task("A", 5, Priority.LOW, start_time="08:00"),
        Task("B", 5, Priority.LOW, start_time="09:00"),
    ]
    ordered = scheduler.sort_by_time(tasks)
    assert [t.name for t in ordered] == ["A", "B", "C"]


# sorting is numeric, not string: "9:00" comes before "10:00"
def test_sort_by_time_numeric_not_lexicographic():
    scheduler = Scheduler()
    tasks = [
        Task("ten", 5, Priority.LOW, start_time="10:00"),
        Task("nine", 5, Priority.LOW, start_time="9:00"),
    ]
    ordered = scheduler.sort_by_time(tasks)
    assert [t.name for t in ordered] == ["nine", "ten"]


# edge: empty list sorts to an empty list (a pet / owner with no tasks)
def test_sort_by_time_empty():
    assert Scheduler().sort_by_time([]) == []


# edge: midnight "00:00" sorts before an untimed task (falsy-zero trap)
def test_sort_by_time_midnight_before_untimed():
    scheduler = Scheduler()
    midnight = Task("midnight", 5, Priority.LOW, start_time="00:00")
    untimed = Task("untimed", 5, Priority.LOW)
    ordered = scheduler.sort_by_time([untimed, midnight])
    assert [t.name for t in ordered] == ["midnight", "untimed"]


# edge: untimed / unparseable times sort to the end, keeping relative order
def test_sort_by_time_untimed_and_malformed_last():
    scheduler = Scheduler()
    timed = Task("timed", 5, Priority.LOW, start_time="08:00")
    bad = Task("bad", 5, Priority.LOW, start_time="abc")
    none = Task("none", 5, Priority.LOW)
    ordered = scheduler.sort_by_time([bad, none, timed])
    assert ordered[0].name == "timed"           # the only real time is first
    assert {ordered[1].name, ordered[2].name} == {"bad", "none"}


# edge: sorting returns a new list; the input is left untouched
def test_sort_by_time_does_not_mutate_input():
    scheduler = Scheduler()
    a = Task("A", 5, Priority.LOW, start_time="09:00")
    b = Task("B", 5, Priority.LOW, start_time="08:00")
    original = [a, b]
    scheduler.sort_by_time(original)
    assert original == [a, b]                    # unchanged


# ---------------------------------------------------------------------------
# Conflict detection  (Scheduler.detect_conflicts)
# ---------------------------------------------------------------------------

# happy path: two overlapping tasks produce exactly one warning
def test_detect_conflicts_overlap():
    scheduler = Scheduler()
    a = Task("A", 30, Priority.LOW, start_time="08:00")   # 08:00–08:30
    b = Task("B", 30, Priority.LOW, start_time="08:15")   # overlaps
    warnings = scheduler.detect_conflicts([a, b])
    assert len(warnings) == 1


# conflict: two tasks at the EXACT same time are flagged
def test_detect_conflicts_duplicate_time():
    scheduler = Scheduler()
    a = Task("A", 30, Priority.LOW, start_time="08:00")
    b = Task("B", 30, Priority.LOW, start_time="08:00")
    warnings = scheduler.detect_conflicts([a, b])
    assert len(warnings) == 1


# happy path: non-overlapping tasks produce no warnings
def test_detect_conflicts_none():
    scheduler = Scheduler()
    a = Task("A", 30, Priority.LOW, start_time="08:00")   # 08:00–08:30
    b = Task("B", 30, Priority.LOW, start_time="09:00")   # 09:00–09:30
    assert scheduler.detect_conflicts([a, b]) == []


# edge: exact boundary touch is NOT a conflict (half-open interval)
def test_detect_conflicts_boundary_touch():
    scheduler = Scheduler()
    a = Task("A", 30, Priority.LOW, start_time="08:00")   # ends 08:30
    b = Task("B", 30, Priority.LOW, start_time="08:30")   # starts 08:30
    assert scheduler.detect_conflicts([a, b]) == []


# edge: untimed tasks are skipped, never producing false conflicts
def test_detect_conflicts_ignores_untimed():
    scheduler = Scheduler()
    a = Task("A", 30, Priority.LOW)                        # no time
    b = Task("B", 30, Priority.LOW)                        # no time
    assert scheduler.detect_conflicts([a, b]) == []


# edge: empty input -> no warnings
def test_detect_conflicts_empty():
    assert Scheduler().detect_conflicts([]) == []


# edge: same pet vs. different pets produce different wording
def test_detect_conflicts_message_wording():
    scheduler = Scheduler()
    pet = Pet("Ari", "Persian Cat")

    # same pet, two overlapping tasks
    a = Task("A", 30, Priority.LOW, start_time="08:00")
    b = Task("B", 30, Priority.LOW, start_time="08:10")
    pet.add_task(a)
    pet.add_task(b)
    same = scheduler.detect_conflicts([a, b])[0]
    assert "can't do two things at once" in same

    # different pets, two overlapping tasks
    other = Pet("White", "Maltese Dog")
    c = Task("C", 30, Priority.LOW, start_time="08:00")
    d = Task("D", 30, Priority.LOW, start_time="08:10")
    pet.add_task(c)
    other.add_task(d)
    cross = scheduler.detect_conflicts([c, d])[0]
    assert "at the same time" in cross


# ---------------------------------------------------------------------------
# Budget / priority selection  (Scheduler.generate)
# ---------------------------------------------------------------------------

# happy path: all tasks fit; highest priority first, then shortest duration
def test_generate_orders_by_priority_then_duration():
    owner = Owner("Yoobin", daily_minutes=120)
    pet = Pet("Ari", "Persian Cat")
    owner.add_pet(pet)
    low = Task("low", 10, Priority.LOW)
    high_long = Task("high_long", 30, Priority.HIGH)
    high_short = Task("high_short", 10, Priority.HIGH)
    for t in (low, high_long, high_short):
        pet.add_task(t)

    schedule = Scheduler().generate(owner)
    assert [t.name for t in schedule.items] == ["high_short", "high_long", "low"]
    assert schedule.total_minutes == 50


# generate: completed tasks are excluded from the plan
def test_generate_excludes_completed():
    owner = Owner("Yoobin", daily_minutes=120)
    pet = Pet("Ari", "Persian Cat")
    owner.add_pet(pet)
    done = Task("done", 10, Priority.HIGH, completed=True)
    todo = Task("todo", 10, Priority.HIGH)
    pet.add_task(done)
    pet.add_task(todo)

    schedule = Scheduler().generate(owner)
    assert [t.name for t in schedule.items] == ["todo"]


# edge: a task that doesn't fit is skipped, a smaller later task still fits
def test_generate_skips_too_big_keeps_smaller():
    owner = Owner("Yoobin", daily_minutes=30)
    pet = Pet("Ari", "Persian Cat")
    owner.add_pet(pet)
    big = Task("big", 40, Priority.HIGH)      # doesn't fit
    small = Task("small", 20, Priority.LOW)   # fits
    pet.add_task(big)
    pet.add_task(small)

    schedule = Scheduler().generate(owner)
    assert [t.name for t in schedule.items] == ["small"]
    assert schedule.total_minutes == 20


# edge: task duration exactly equal to the budget still fits
def test_generate_exact_fit():
    owner = Owner("Yoobin", daily_minutes=30)
    pet = Pet("Ari", "Persian Cat")
    owner.add_pet(pet)
    pet.add_task(Task("exact", 30, Priority.HIGH))

    schedule = Scheduler().generate(owner)
    assert schedule.total_minutes == 30


# edge: an owner with no pets (and no tasks) yields an empty schedule
def test_generate_owner_no_pets():
    owner = Owner("Yoobin", daily_minutes=120)
    schedule = Scheduler().generate(owner)
    assert schedule.items == []
    assert schedule.total_minutes == 0


# edge: zero budget schedules nothing
def test_generate_zero_budget():
    owner = Owner("Yoobin", daily_minutes=0)
    pet = Pet("Ari", "Persian Cat")
    owner.add_pet(pet)
    pet.add_task(Task("feeding", 5, Priority.HIGH))

    schedule = Scheduler().generate(owner)
    assert schedule.items == []


# generate: overlapping selected tasks surface as warnings on the schedule
def test_generate_populates_conflict_warnings():
    owner = Owner("Yoobin", daily_minutes=120)
    pet = Pet("Ari", "Persian Cat")
    owner.add_pet(pet)
    pet.add_task(Task("A", 30, Priority.HIGH, start_time="08:00"))
    pet.add_task(Task("B", 30, Priority.HIGH, start_time="08:15"))

    schedule = Scheduler().generate(owner)
    assert len(schedule.warnings) == 1


# ---------------------------------------------------------------------------
# Schedule.display
# ---------------------------------------------------------------------------

# edge: an empty schedule reports "No tasks scheduled."
def test_display_empty():
    assert Schedule().display() == "No tasks scheduled."


# happy path: a timed task shows at its time; an untimed one chains after it
def test_display_places_timed_then_chains_untimed():
    pet = Pet("Ari", "Persian Cat")
    timed = Task("timed", 30, Priority.HIGH, start_time="10:00")
    untimed = Task("untimed", 15, Priority.LOW)
    pet.add_task(timed)
    pet.add_task(untimed)

    schedule = Schedule()
    schedule.add(timed)
    schedule.add(untimed)
    out = schedule.display()

    assert "10:00 — timed" in out
    assert "10:30 — untimed" in out          # chains off the timed task's end


# edge: a task with no pet renders as "Unknown" rather than crashing
def test_display_task_without_pet():
    task = Task("orphan", 10, Priority.LOW, start_time="08:00")
    schedule = Schedule()
    schedule.add(task)
    assert "for Unknown" in schedule.display()
