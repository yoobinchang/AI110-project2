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

# Ari
ari.add_task(Task("Feeding", 5, Priority.HIGH, "daily"))
ari.add_task(Task("Shower", 20, Priority.MEDIUM, "daily"))
ari.add_task(Task("Buy clothes", 120, Priority.LOW, "once a month"))

# Zimba
zimba.add_task(Task("Walking", 30, Priority.HIGH, "once two days"))
zimba.add_task(Task("Feeding", 5, Priority.HIGH, "daily"))
zimba.add_task(Task("Brushing", 15, Priority.MEDIUM, "daily"))

# White
white.add_task(Task("Feeding", 5, Priority.HIGH, "daily"))
white.add_task(Task("Playing", 10, Priority.MEDIUM, "daily"))
white.add_task(Task("Nail trim", 10, Priority.LOW, "weekly"))

# generate and print the daily plan
schedule = Scheduler().generate(owner)
print(f"Daily plan for {owner.name} (budget: {owner.daily_minutes} min):\n")
print(schedule.display())
