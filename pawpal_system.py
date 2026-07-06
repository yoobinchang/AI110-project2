"""PawPal+ system classes.

Generated from diagrams/uml.mmd, then implemented.
Data classes: Owner, Pet, Task (+ Priority enum).
Logic class:  Scheduler -> produces a Schedule.
"""

# Treat type hints as strings so classes can reference each other before
# they are defined (e.g. Task hints "Pet" while Pet is defined further down).
from __future__ import annotations

from datetime import date, timedelta
from enum import Enum


class Priority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3


# How many days until the next occurrence, per frequency. Only these
# frequencies auto-repeat; anything else (e.g. "once") does not recur.
RECURRENCE_DAYS = {
    "daily": 1,
    "weekly": 7,
}


def start_minute(task: "Task") -> int | None:
    """Convert a task's "HH:MM" start_time into minutes-of-day.

    Returns None if the task has no start_time or it can't be parsed, so
    callers can treat "untimed" tasks uniformly (never crashes). Shared by
    Schedule (placement) and Scheduler (sorting / conflict detection).
    """
    if not task.start_time:
        return None
    try:
        hh, mm = task.start_time.split(":")
        return int(hh) * 60 + int(mm)
    except (ValueError, AttributeError):
        return None


def _time_key(task: "Task") -> tuple[bool, int]:
    """Sort key for tasks by clock time: timed first (by minute), untimed last.

    Calls start_minute() once (not twice) and returns a tuple so the primary
    sort is "has a time?" and the secondary is the minute-of-day.
    """
    m = start_minute(task)
    return (m is None, m or 0)


class Task:
    """A single care activity for a pet."""

    def __init__(
        self,
        name: str,
        duration: int,
        priority: Priority,
        frequency: str = "daily",
        completed: bool = False,
        start_time: str | None = None,
        due_date: date | None = None,
    ):
        """Create a care task with a duration, priority, and frequency."""
        self.name: str = name
        self.duration: int = duration          # minutes
        self.priority: Priority = priority
        self.frequency: str = frequency        # e.g. "daily", "weekly"
        self.completed: bool = completed
        self.start_time: str | None = start_time  # "HH:MM", or None if unset
        self.due_date: date | None = due_date  # when this occurrence is due
        self.pet: Pet | None = None            # back-reference, set by Pet.add_task()

    def edit(
        self,
        name: str = None,
        duration: int = None,
        priority: Priority = None,
        frequency: str = None,
        start_time: str = None,
    ) -> None:
        """Update only the fields that are provided."""
        if name is not None:
            self.name = name
        if duration is not None:
            self.duration = duration
        if priority is not None:
            self.priority = priority
        if frequency is not None:
            self.frequency = frequency
        if start_time is not None:
            self.start_time = start_time

    def is_recurring(self) -> bool:
        """True if this task's frequency should auto-repeat (daily/weekly)."""
        return self.frequency in RECURRENCE_DAYS

    def next_due_date(self) -> date:
        """Return the due date of the next occurrence, using timedelta.

        Anchored on this task's due_date (falls back to today if unset), so a
        daily task lands on due_date + 1 day and a weekly one on + 7 days.
        timedelta handles month-end and leap years automatically.
        """
        anchor = self.due_date if self.due_date is not None else date.today()
        return anchor + timedelta(days=RECURRENCE_DAYS[self.frequency])

    def mark_complete(self) -> Task | None:
        """Mark this task done; if recurring, spawn the next occurrence.

        Returns the newly created Task for the next occurrence (already added
        to the same pet), or None if this task does not recur.
        """
        self.completed = True

        if not self.is_recurring():
            return None

        # Build the next occurrence: same details, not yet done, new due date.
        next_task = Task(
            name=self.name,
            duration=self.duration,
            priority=self.priority,
            frequency=self.frequency,
            completed=False,
            start_time=self.start_time,
            due_date=self.next_due_date(),
        )
        # Attach it to the same pet so the scheduler picks it up next time.
        if self.pet is not None:
            self.pet.add_task(next_task)
        return next_task

    def __repr__(self) -> str:
        """Return a short developer-friendly representation."""
        return f"Task({self.name!r}, {self.duration}min, {self.priority.name})"


class Pet:
    """Stores pet details and its list of Tasks."""

    def __init__(self, name: str, species: str):
        """Create a pet with a name and species and an empty task list."""
        self.name: str = name
        self.species: str = species
        self.tasks: list[Task] = []

    def add_task(self, task: Task) -> None:
        """Attach a task to this pet and link the task back to it."""
        task.pet = self            # keep both sides of the link in sync
        self.tasks.append(task)

    def __repr__(self) -> str:
        """Return a short developer-friendly representation."""
        return f"Pet({self.name!r}, {self.species!r})"


class Owner:
    """Manages multiple Pets and provides access to all their tasks."""

    def __init__(self, name: str, daily_minutes: int):
        """Create an owner with a daily time budget and no pets yet."""
        self.name: str = name
        self.daily_minutes: int = daily_minutes
        self.pets: list[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        """Register a pet with this owner."""
        self.pets.append(pet)

    def all_tasks(self) -> list[Task]:
        """Flatten every task across every pet (Owner -> pets -> tasks)."""
        tasks: list[Task] = []
        for pet in self.pets:
            tasks.extend(pet.tasks)
        return tasks


class Schedule:
    """The result produced by the Scheduler: an ordered plan of tasks."""

    START_MINUTE = 8 * 60  # plan starts at 08:00

    def __init__(self):
        """Create an empty schedule with no tasks, zero time, no warnings."""
        self.items: list[Task] = []
        self.total_minutes: int = 0
        self.warnings: list[str] = []   # conflict warnings, filled by Scheduler

    def add(self, task: Task) -> None:
        """Append a task to the plan and update the running total time."""
        self.items.append(task)
        self.total_minutes += task.duration

    def display(self) -> str:
        """Return the plan as text, placing each task at its own start_time.

        User intent first: a task with a start_time is shown AT that time
        (not repacked). Untimed tasks fall into the running clock after the
        last placed task. Any conflict warnings are listed at the end.
        """
        if not self.items:
            return "No tasks scheduled."

        # Order by clock time; untimed tasks (None) come last.
        ordered = sorted(self.items, key=_time_key)

        lines: list[str] = []
        clock = self.START_MINUTE
        for task in ordered:
            sm = start_minute(task)
            if sm is not None:
                clock = sm            # honor the user's chosen time
            hh, mm = divmod(clock, 60)
            pet_name = task.pet.name if task.pet else "Unknown"
            lines.append(
                f"  {hh:02d}:{mm:02d} — {task.name} for {pet_name} "
                f"({task.duration} min) [priority: {task.priority.name.lower()}]"
            )
            clock += task.duration
        lines.append(f"\nTotal: {self.total_minutes} min")

        if self.warnings:
            lines.append("\nWarnings:")
            lines.extend(f"  {w}" for w in self.warnings)

        return "\n".join(lines)


class Scheduler:
    """The brain: retrieves, organizes, and selects Tasks across Pets."""

    def sort_by_time(self, tasks: list[Task]) -> list[Task]:
        """Return tasks ordered by start_time ("HH:MM"), earliest first.

        Sorts on _time_key, which converts "HH:MM" to minutes-of-day so the
        comparison is numeric (so "9:00" sorts before "10:00") and pushes tasks
        with no start_time to the end. Returns a new list; the input is unchanged.
        """
        return sorted(tasks, key=_time_key)

    def detect_conflicts(self, tasks: list[Task]) -> list[str]:
        """Return a warning for each pair of tasks whose times overlap.

        Lightweight: never raises. Each task occupies [start, start+duration);
        two tasks conflict when their intervals overlap. Tasks with no/invalid
        start_time are skipped (they aren't pinned to a clock time). Returns an
        empty list when there are no conflicts.

        The timed tasks are sorted by start time so the inner scan can stop
        early: once a later task starts at/after the current task ends, no
        further task can overlap it. This keeps the common case (few overlaps)
        close to O(n log n) instead of always comparing all n^2 pairs.
        """
        warnings: list[str] = []

        # Keep only tasks with a usable start time, as (start, end, task),
        # sorted by start so we can stop scanning early (sweep-line).
        timed = sorted(
            (
                (start_minute(t), start_minute(t) + t.duration, t)
                for t in tasks
                if start_minute(t) is not None
            ),
            key=lambda span: (span[0], span[1]),   # by start, then end (never compares Task)
        )

        for i, (start_a, end_a, task_a) in enumerate(timed):
            for start_b, end_b, task_b in timed[i + 1:]:
                # Sorted by start: once B starts at/after A ends, nothing
                # further can overlap A either, so stop scanning.
                if start_b >= end_a:
                    break
                warnings.append(self._conflict_message(task_a, task_b))

        return warnings

    @staticmethod
    def _conflict_message(a: Task, b: Task) -> str:
        """Build a human-readable warning for two overlapping tasks."""
        pet_a = a.pet.name if a.pet else "Unknown"
        pet_b = b.pet.name if b.pet else "Unknown"
        same_pet = a.pet is not None and a.pet is b.pet
        who = (
            f"{pet_a} can't do two things at once"
            if same_pet
            else f"you can't be with {pet_a} and {pet_b} at the same time"
        )
        return (
            f"⚠️  Conflict: '{a.name}' ({a.start_time}, {a.duration} min) overlaps "
            f"'{b.name}' ({b.start_time}, {b.duration} min) — {who}."
        )

    def filter_tasks(
        self,
        tasks: list[Task],
        completed: bool | None = None,
        pet_name: str | None = None,
    ) -> list[Task]:
        """Return the tasks matching the given filters.

        Each filter is optional (None = "don't filter on this"):
          - completed: keep only tasks whose .completed equals this bool
          - pet_name:  keep only tasks belonging to a pet with this name
        A task is kept only if it passes every active filter (AND logic).
        """
        result = tasks
        if completed is not None:
            result = [t for t in result if t.completed == completed]
        if pet_name is not None:
            result = [t for t in result if t.pet is not None and t.pet.name == pet_name]
        return result

    def generate(self, owner: Owner) -> Schedule:
        """Build a plan: incomplete tasks by priority, fit within the budget."""
        schedule = Schedule()

        # 1. retrieve all incomplete tasks across every pet
        tasks = [t for t in owner.all_tasks() if not t.completed]

        # 2. organize: highest priority first, then shortest duration
        tasks.sort(key=lambda t: (-t.priority.value, t.duration))

        # 3. select: greedily fit tasks within the owner's available time
        remaining = owner.daily_minutes
        for task in tasks:
            if task.duration <= remaining:
                schedule.add(task)
                remaining -= task.duration
            # if it doesn't fit, skip it and keep trying smaller tasks

        # 4. warn (don't crash) if any selected tasks overlap in time
        schedule.warnings = self.detect_conflicts(schedule.items)

        return schedule
