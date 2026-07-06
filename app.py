import streamlit as st

from pawpal_system import Owner, Pet, Task, Scheduler, Priority

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

# st.session_state works like a dictionary that survives every re-run.
# Store the Owner in it ONCE so pets/tasks persist as you navigate the app.
if "owner" not in st.session_state:
    st.session_state["owner"] = Owner("Jordan", 120)

owner = st.session_state["owner"]  # the persistent Owner; reuse it everywhere

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

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

    if st.button("Add task"):
        pet = owner.pets[pet_names.index(chosen)]
        pet.add_task(Task(task_title, int(duration), PRIORITY_MAP[priority]))
        st.success(f"Added '{task_title}' to {chosen}.")

# --- Show current pets & tasks (below the buttons so new items appear) ---
if owner.pets:
    st.write("Current pets & tasks:")
    for pet in owner.pets:
        st.markdown(f"**{pet.name}** ({pet.species}) — {len(pet.tasks)} task(s)")
        for task in pet.tasks:
            st.write(f"- {task.name} ({task.duration} min) [{task.priority.name.lower()}]")
else:
    st.info("No pets yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
st.caption("Calls Scheduler.generate() on your owner and shows the plan.")

if st.button("Generate schedule"):
    schedule = Scheduler().generate(owner)   # the scheduling logic
    st.text(f"Daily plan for {owner.name} (budget: {owner.daily_minutes} min):\n")
    st.text(schedule.display())
