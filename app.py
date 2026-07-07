from datetime import time

import streamlit as st

from pawpal_system import Owner, Pet, Task, Scheduler, Schedule, Priority, start_minute

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

# st.session_state works like a dictionary that survives every re-run.
# Store the Owner in it ONCE so pets/tasks persist as you navigate the app.
if "owner" not in st.session_state:
    st.session_state["owner"] = Owner("Jordan", 120)

owner = st.session_state["owner"]  # the persistent Owner; reuse it everywhere

st.title("🐾 PawPal+")

# --- Owner settings ---
st.subheader("Owner")
owner.name = st.text_input("Owner name", value=owner.name)
owner.daily_minutes = st.number_input(
    "Daily time budget (minutes)", min_value=1, max_value=1440, value=owner.daily_minutes
)

st.divider()

# --- Add a pet: UI collects input -> Owner.add_pet stores it ---
st.subheader("Add a pet")
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])

if st.button("Add pet"):
    owner.add_pet(Pet(pet_name, species))
    st.success(f"Added {pet_name}.")

st.divider()

# --- Add a task: UI collects input -> Pet.add_task stores it ---
st.markdown("### Tasks")
PRIORITY_MAP = {"low": Priority.LOW, "medium": Priority.MEDIUM, "high": Priority.HIGH}

if not owner.pets:
    st.info("Add a pet first, then you can add tasks.")
else:
    pet_names = [pet.name for pet in owner.pets]
    chosen = st.selectbox("Which pet?", pet_names)

    col1, col2, col3 = st.columns(3)
    with col1:
        task_title = st.text_input("Task title", value="Morning walk")
    with col2:
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
    with col3:
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

    # An optional fixed start time is what lets the Scheduler sort by clock time
    # and detect overlaps. Without it a task is "untimed" and sorts to the end.
    has_time = st.checkbox("Set a fixed start time", value=True)
    start_str = None
    if has_time:
        start_str = st.time_input("Start time", value=time(8, 0)).strftime("%H:%M")

    if st.button("Add task"):
        pet = owner.pets[pet_names.index(chosen)]
        pet.add_task(Task(task_title, int(duration), PRIORITY_MAP[priority], start_time=start_str))
        st.success(f"Added '{task_title}' to {chosen}.")

# --- Current tasks: filter with Scheduler.filter_tasks, order with sort_by_time ---
if owner.pets:
    st.markdown("#### Current tasks")
    scheduler = Scheduler()

    fcol1, fcol2 = st.columns(2)
    with fcol1:
        pet_filter = st.selectbox("Filter by pet", ["All pets"] + [p.name for p in owner.pets])
    with fcol2:
        status_filter = st.selectbox("Filter by status", ["All", "Incomplete", "Completed"])

    # None means "don't filter on this"; the Scheduler combines both with AND.
    tasks = scheduler.filter_tasks(
        owner.all_tasks(),
        completed={"All": None, "Incomplete": False, "Completed": True}[status_filter],
        pet_name=None if pet_filter == "All pets" else pet_filter,
    )
    tasks = scheduler.sort_by_time(tasks)   # earliest first, untimed last

    if tasks:
        st.table(
            [
                {
                    "Time": task.start_time or "—",
                    "Task": task.name,
                    "Pet": task.pet.name if task.pet else "Unknown",
                    "Duration": f"{task.duration} min",
                    "Priority": task.priority.name.title(),
                    "Done": "✅" if task.completed else "",
                }
                for task in tasks
            ]
        )
    else:
        st.info("No tasks match these filters.")
else:
    st.info("No pets yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
st.caption("Sorts by time, fits tasks into your budget, and flags any conflicts.")

if st.button("Generate schedule"):
    scheduler = Scheduler()
    schedule = scheduler.generate(owner)   # the scheduling logic

    if not schedule.items:
        st.info("Nothing to plan yet — add tasks that fit inside your daily time budget.")
    else:
        # Budget at a glance: how much of the day the plan uses.
        c1, c2 = st.columns(2)
        c1.metric("Planned time", f"{schedule.total_minutes} min")
        c2.metric("Daily budget", f"{owner.daily_minutes} min")

        # Order the selected tasks by clock time (Scheduler.sort_by_time) and lay
        # them out the same way Schedule.display() does: honor each task's own
        # start time, and let untimed tasks fall into the running clock after it.
        st.markdown(f"#### 🗓️ Daily plan for {owner.name}")
        rows = []
        clock = Schedule.START_MINUTE
        for task in scheduler.sort_by_time(schedule.items):
            sm = start_minute(task)
            if sm is not None:
                clock = sm
            hh, mm = divmod(clock, 60)
            rows.append(
                {
                    "Time": f"{hh:02d}:{mm:02d}",
                    "Task": task.name,
                    "Pet": task.pet.name if task.pet else "Unknown",
                    "Duration": f"{task.duration} min",
                    "Priority": task.priority.name.title(),
                }
            )
            clock += task.duration
        st.table(rows)

        # Conflicts are a "look at this," not a failure — so st.warning (amber),
        # placed right under the plan, with an actionable tip. No conflicts -> reassure.
        if schedule.warnings:
            st.markdown("#### ⚠️ Scheduling conflicts")
            for warning in schedule.warnings:
                st.warning(warning)
            st.caption("Tip: shift a start time or shorten a task to clear the overlap.")
        else:
            st.success("No scheduling conflicts — you're all set! 🎉")
