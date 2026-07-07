# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

**Owner (Add a user)**
# Attributes
name: str
daily_minutes: int
pets: list[Pet]
# Methods:
add_Pet(pet: Pet)

**Pet (Add a pet)**
# Attributes:
name: str
species: str
# Methods:
add_task(task: Task)

**Task (Add a task)**
# Attributes:
name: str
duration: int
priority: Enum Priority - LOW / MEDIUM / HIGH
# Methods:
edit(name=None, duration=None, priority=None) - Optional edits

**Scheduler (Logic - Generate a schedule)**
# Methods:
generate(owner: Owner) -> Schedule

**Schedule (Result - Generate a schedule)**
# Attributes:
items: list[Task], total_minutes: int
# Methods:
display() -> str

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

Yes, the design changed in one meaningful way during implementation.

My initial UML modeled the Pet–Task relationship as one-directional ownership (a Pet has Tasks). While implementing the scheduler I added a back-reference so each Task also knows its Pet (`Task.pet`, set in `Pet.add_task()`), making the relationship bidirectional. I made this change because the scheduling logic genuinely needs it: `Schedule.display()` and the conflict warnings read `task.pet.name` (to print "for Ari" and "Ari can't do two things at once"), and `Task.mark_complete()` calls `self.pet.add_task()` to attach the next recurring occurrence to the right pet. I kept the ownership conceptually clear (the Pet still owns its Tasks) but let the code carry the back-reference the logic depends on.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

**Warn about conflicts instead of auto-resolving them**
When two tasks overlap in time, the scheduler warns the owner instead of moving one of them. `display()` keeps every task at the exact `start_time` the owner chose, and `detect_conflicts()` just adds a message like "Ari can't do two things at once." The tradeoff is that the plan can still contain an overlap the program didn't fix. That's reasonable here because the owner knows things the program doesn't, which task can actually move, or whether they have help, and
auto-repacking could quietly shift a task they pinned on purpose (like medication at 08:00). Warning instead of blocking keeps the owner in control while still catching the mistake.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

I used AI across distinct phases of the project: brainstorming the UML design, implementing the scheduling logic, writing the test suite, connecting the logic to the Streamlit UI, and drafting documentation. The most helpful prompts were specific and grounded in a real file. For example, pointing the assistant at `pawpal_system.py` and asking "what are the most important edge cases to test for sorting and recurring tasks?" produced far better results than vague, open-ended prompts. Asking it to explain its reasoning was more useful than asking it to just write code.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

For the recurrence test that checks a daily task's next due date, the logic depends on today's date. The assistant suggested pulling in the `freezegun` library to freeze the clock. I didn't accept that as-is — I kept the test dependency-free by asserting the next due date relative to `date.today()` instead, since adding an external library for a single date-based test wasn't worth the extra dependency in a small project. I verified the assistant's suggestions by **running them, not trusting them** — it executed my `pytest` suite (32 tests passing) and ran `main.py` to paste real output into the README, rather than inventing results. That habit of "run it to confirm" is how I checked its work.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

I wrote 32 tests covering the four core behaviors of the scheduler, each with both normal cases and tricky edge cases:

- **Recurring tasks** — completing a daily task creates the next day's task and a weekly one moves ahead a week; the new task copies the details but starts as not-done; a one-time task creates nothing; and the date math handles month-ends and leap years correctly (for example, the last day of January rolls into February).
- **Sorting by time** — tasks come back earliest first, the comparison treats the time as an actual clock value rather than plain text (so an earlier morning time correctly comes before a later one), tasks with no time or an unreadable time fall to the end, and the original list is never changed.
- **Conflict detection** — overlapping tasks are flagged, two tasks at the exact same time produce a warning, a task that starts at the very moment another ends is not treated as a conflict, and a same-pet conflict reads differently from a conflict between two different pets.
- **Budget and priority** — tasks are chosen by priority first and shorter length second, already-completed tasks are left out, a task too long to fit is skipped while a smaller one still fits, and an owner with no tasks produces an empty plan.

These are the behaviors a bug would hurt most, because they rely on non-obvious logic — date rollovers, exact time boundaries, and treating times as numbers instead of text — where a small, plausible-looking change could quietly break the result. Locking them down with tests protects against those silent mistakes.

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

My confidence on the scheduler is **4 out of 5**. For the documented core logic the tests are thorough and all 32 pass in under a second, so the parts under test are proven, not just assumed. What holds me back from full confidence is coverage at the edges of the input space rather than any known bug.

If I had more time I would test the filtering feature, which is part of the app but currently has no tests; impossible times like "25:00", which the app accepts as valid instead of rejecting (I would decide whether to block them or clearly document the behavior); and basic input checks for negative durations, a negative time budget, and empty names. I would also make the one date-based test reliable so its result can't change depending on the day it happens to run.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

I'm most satisfied with how the scheduling logic came together as small, focused pieces that each do one thing well, so the same time-parsing work isn't repeated in different places. Because the logic lived in clean classes kept separate from the interface, I could test it thoroughly and reuse the exact same code in both the command-line demo and the Streamlit app without rewriting anything. The way conflicts are handled also went well: instead of silently rearranging tasks to fix an overlap, the app explains the problem in plain language and lets the owner decide what to do, which keeps them in control.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

I would add better input validation at the edges. Right now the app will accept an impossible time like "25:00" and treat it as valid instead of rejecting it, and there is no guard against negative durations or a negative time budget. I would also add tests for the filtering feature, which currently has none, and make the one date-based test reliable so its result can't change depending on the day it runs. On the design side, I would give the task frequency a fixed set of allowed values instead of a free-form text field, so an invalid entry couldn't slip in unnoticed.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

I learned that visualizing the initial brainstorming through a UML diagram is very important in system design — starting from the diagram forced me to decide what each class was responsible for before writing code, so implementation became "fill in the plan" rather than "figure it out as I go." Just as importantly, I learned that the diagram is a "living document" like my design genuinely evolved during implementation, and keeping the UML, the code, and this reflection in sync mattered more than defending my first draft.