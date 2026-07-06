from datetime import date, timedelta

from pawpal_system import Task, Pet, Priority

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


# add_task verification : adding task increases a pet's task count
def test_add_task_increases_count():
    pet = Pet("Ari", "Persian Cat")
    assert len(pet.tasks) == 0            # no tasks yet

    pet.add_task(Task("Feeding", 5, Priority.HIGH))
    assert len(pet.tasks) == 1            # count went up by 1

    pet.add_task(Task("Shower", 20, Priority.MEDIUM))
    assert len(pet.tasks) == 2            # and up again
