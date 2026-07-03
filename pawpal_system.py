"""PawPal+ system classes.

Generated from diagrams/uml.mmd, then implemented.
Data classes: Owner, Pet, Task (+ Priority enum).
Logic class:  Scheduler -> produces a Schedule.
"""

from __future__ import annotations

from enum import Enum


class Priority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3


class Task:
    """A single care activity for a pet."""

    def __init__(
        self,
        name: str,
        duration: int,
        priority: Priority,
        frequency: str = "daily",
        completed: bool = False,
    ):
        self.name: str = name
        self.duration: int = duration          # minutes
        self.priority: Priority = priority
        self.frequency: str = frequency        # e.g. "daily", "weekly"
        self.completed: bool = completed
        self.pet: Pet | None = None            # back-reference, set by Pet.add_task()

    def edit(
        self,
        name: str = None,
        duration: int = None,
        priority: Priority = None,
        frequency: str = None,
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

    def mark_complete(self) -> None:
        self.completed = True

    def __repr__(self) -> str:
        return f"Task({self.name!r}, {self.duration}min, {self.priority.name})"


class Pet:
    """Stores pet details and its list of Tasks."""

    def __init__(self, name: str, species: str):
        self.name: str = name
        self.species: str = species
        self.tasks: list[Task] = []

    def add_task(self, task: Task) -> None:
        task.pet = self            # keep both sides of the link in sync
        self.tasks.append(task)

    def __repr__(self) -> str:
        return f"Pet({self.name!r}, {self.species!r})"


class Owner:
    """Manages multiple Pets and provides access to all their tasks."""

    def __init__(self, name: str, daily_minutes: int):
        self.name: str = name
        self.daily_minutes: int = daily_minutes
        self.pets: list[Pet] = []

    def add_pet(self, pet: Pet) -> None:
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
        self.items: list[Task] = []
        self.total_minutes: int = 0

    def add(self, task: Task) -> None:
        self.items.append(task)
        self.total_minutes += task.duration

    def display(self) -> str:
        if not self.items:
            return "No tasks scheduled."

        lines: list[str] = []
        clock = self.START_MINUTE
        for task in self.items:
            hh, mm = divmod(clock, 60)
            pet_name = task.pet.name if task.pet else "Unknown"
            lines.append(
                f"  {hh:02d}:{mm:02d} — {task.name} for {pet_name} "
                f"({task.duration} min) [priority: {task.priority.name.lower()}]"
            )
            clock += task.duration
        lines.append(f"\nTotal: {self.total_minutes} min")
        return "\n".join(lines)


class Scheduler:
    """The brain: retrieves, organizes, and selects Tasks across Pets."""

    def generate(self, owner: Owner) -> Schedule:
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

        return schedule
