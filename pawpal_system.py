"""PawPal+ system classes (skeleton).

Generated from diagrams/uml.mmd. Attributes are initialized in __init__;
method bodies are left as stubs to be implemented later.
"""

from __future__ import annotations

from enum import Enum


class Priority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3


class Owner:
    def __init__(self, name: str, daily_minutes: int):
        self.name: str = name
        self.daily_minutes: int = daily_minutes
        self.pets: list[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        pass


class Pet:
    def __init__(self, name: str, species: str):
        self.name: str = name
        self.species: str = species
        self.tasks: list[Task] = []

    def add_task(self, task: Task) -> None:
        pass


class Task:
    def __init__(self, name: str, duration: int, priority: Priority):
        self.name: str = name
        self.duration: int = duration
        self.priority: Priority = priority

    def edit(self, name: str = None, duration: int = None, priority: Priority = None) -> None:
        pass


class Schedule:
    def __init__(self):
        self.items: list[Task] = []
        self.total_minutes: int = 0

    def display(self) -> str:
        pass


class Scheduler:
    def generate(self, owner: Owner) -> Schedule:
        pass
