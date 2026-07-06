# temporary test ground

from pawpal_system import Task, Owner, Pet, Scheduler, Priority

owner = Owner("Yoobin Chang", 120)
ari = Pet("Ari", "Persian Cat")
zimba = Pet("Zimba", "Golden Retriever")
white = Pet("White", "Maltese Dog")

# register the pets with the owner so the scheduler can see their tasks
owner.add_pet(ari)
owner.add_pet(zimba)
owner.add_pet(white)

# Tasks are added OUT OF ORDER on purpose (start_time is all over the place)
# so we can prove sort_by_time() actually reorders them. Some are marked
# completed=True to prove filter_tasks() can separate done vs. to-do.

# Ari
ari.add_task(Task("Feeding", 5, Priority.HIGH, "daily", start_time="08:00"))
ari.add_task(Task("Shower", 20, Priority.MEDIUM, "daily", start_time="19:30"))
ari.add_task(Task("Buy clothes", 120, Priority.LOW, "once a month"))  # no time

# Zimba
zimba.add_task(Task("Walking", 30, Priority.HIGH, "once two days", start_time="7:15"))
zimba.add_task(Task("Feeding", 5, Priority.HIGH, "daily", start_time="18:00", completed=True))
zimba.add_task(Task("Brushing", 15, Priority.MEDIUM, "daily", start_time="12:00"))

# White
white.add_task(Task("Feeding", 5, Priority.HIGH, "daily", start_time="9:00", completed=True))
white.add_task(Task("Playing", 10, Priority.MEDIUM, "daily", start_time="16:45"))
white.add_task(Task("Nail trim", 10, Priority.LOW, "weekly", start_time="10:30"))

# --- CONFLICTS on purpose, to test detect_conflicts() ---
# Same pet: Ari already has "Feeding" at 08:00 for 5 min (08:00-08:05).
# This "Medicine" at 08:00 for 10 min overlaps it -> same-pet conflict.
ari.add_task(Task("Medicine", 10, Priority.HIGH, "daily", start_time="08:00"))
# Different pets: Zimba "Brushing" is 12:00-12:15. This White "Vet visit"
# at 12:10 for 30 min overlaps it -> owner-can't-be-in-two-places conflict.
white.add_task(Task("Vet visit", 30, Priority.HIGH, "weekly", start_time="12:10"))

scheduler = Scheduler()
all_tasks = owner.all_tasks()


def show(title, tasks):
    """Print a labeled list of tasks with their start time and pet."""
    print(title)
    if not tasks:
        print("  (none)")
    for t in tasks:
        pet_name = t.pet.name if t.pet else "Unknown"
        done = "x" if t.completed else " "
        print(f"  [{done}] {str(t.start_time):>5}  {t.name} ({pet_name})")
    print()


# --- 0. Raw order (as inserted, unsorted) ---
show("0) Insertion order (unsorted):", all_tasks)

# --- 1. sort_by_time(): earliest first, None goes last ---
show("1) Sorted by time:", scheduler.sort_by_time(all_tasks))

# --- 2. filter_tasks(): only incomplete, then sorted ---
todo = scheduler.filter_tasks(all_tasks, completed=False)
show("2) Incomplete only, sorted by time:", scheduler.sort_by_time(todo))

# --- 3. filter_tasks(): only completed ---
show("3) Completed only:", scheduler.filter_tasks(all_tasks, completed=True))

# --- 4. filter_tasks(): one pet, sorted by time ---
zimba_tasks = scheduler.filter_tasks(all_tasks, pet_name="Zimba")
show("4) Zimba's tasks, sorted by time:", scheduler.sort_by_time(zimba_tasks))

# --- 5. combined filters: Zimba's incomplete tasks, sorted ---
show(
    "5) Zimba's incomplete tasks, sorted by time:",
    scheduler.sort_by_time(
        scheduler.filter_tasks(all_tasks, pet_name="Zimba", completed=False)
    ),
)

# --- 6. detect_conflicts(): warn on overlapping times ---
print("6) Conflict check (all tasks):")
conflicts = scheduler.detect_conflicts(all_tasks)
if not conflicts:
    print("  No conflicts found.")
for warning in conflicts:
    print(" ", warning)
print()

# --- the original daily plan still works ---
schedule = scheduler.generate(owner)
print(f"Daily plan for {owner.name} (budget: {owner.daily_minutes} min):\n")
print(schedule.display())
