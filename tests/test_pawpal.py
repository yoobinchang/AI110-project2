from pawpal_system import Task, Pet, Priority

# mark_complete verification
def test_mark_complete():
    task = Task("Feeding", 5, Priority.HIGH)
    assert task.completed is False        # starts not done
    task.mark_complete()
    assert task.completed is True         # flipped to done


# add_task verification : adding task increases a pet's task count
def test_add_task_increases_count():
    pet = Pet("Ari", "Persian Cat")
    assert len(pet.tasks) == 0            # no tasks yet

    pet.add_task(Task("Feeding", 5, Priority.HIGH))
    assert len(pet.tasks) == 1            # count went up by 1

    pet.add_task(Task("Shower", 20, Priority.MEDIUM))
    assert len(pet.tasks) == 2            # and up again
