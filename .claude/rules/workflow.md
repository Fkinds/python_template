# Workflow Orchestration Rules

These rules govern how Claude approaches work in this project.
They complement the coding standards in CLAUDE.md.

## 1. Plan Node Default

- Enter plan mode for ANY non-trivial task (3+ steps or
  architectural decisions)
- If something goes sideways, STOP and re-plan immediately
- Use plan mode for verification steps, not just building
- Write detailed specs upfront to reduce ambiguity
- Skip planning only for single-file, obvious fixes (typos,
  one-line bug fixes, simple renames)

## 2. Subagent Strategy

- Use subagents liberally to keep main context window clean
- Offload research, exploration, and parallel analysis to
  subagents
- For complex problems, throw more compute at it via
  subagents
- One task per subagent for focused execution

## 3. Self-Improvement Loop

After ANY correction from the user:

1. Immediately update `tasks/lessons.md` with the pattern
2. Write a concrete rule to prevent the same mistake
3. Include the date and context of the correction
4. Reference the relevant CLAUDE.md rule if one was violated
5. Review lessons at session start for relevant project

## 4. Verification Before Done

Never mark a task complete without proving it works:

- Run the relevant test suite with `uv run pytest`
- Run the full lint chain:
  `uv run ruff check src tests &&
   uv run ruff format --check src tests &&
   uv run mypy src &&
   uv run fixit lint src tests &&
   uv run lint-imports`
- Diff behavior between main and your changes when relevant
- Ask yourself: "Would a staff engineer approve this?"

## 5. Demand Elegance (Balanced)

- For non-trivial changes: pause and ask "is there a more
  elegant way?"
- If a fix feels hacky: "Knowing everything I know now,
  implement the elegant solution"
- Skip this for simple, obvious fixes -- do not over-engineer
- Challenge your own work before presenting it

## 6. Autonomous Bug Fixing

- When given a bug report: just fix it. Do not ask for
  hand-holding
- Point at logs, errors, failing tests -- then resolve them
- Zero context switching required from the user
- Use `git commit --fixup=<target-sha>` per CLAUDE.md rules

---

## Task Management Protocol

### Starting a task

1. Write the plan to `tasks/todo.md` with checkable items
   (`- [ ]` syntax)
2. Check in with the user before starting implementation

### During implementation

3. Mark items complete (`- [x]`) as you go
4. Provide a high-level summary at each major step
5. Document results and decisions in `tasks/todo.md`

### After completion

6. Capture lessons learned in `tasks/lessons.md`
7. Add a review section to `tasks/todo.md`

---

## Core Principles

- **Simplicity First**: Make every change as simple as
  possible. Impact minimal code.
- **No Laziness**: Find root causes. No temporary fixes.
  Senior developer standards.
- **Minimal Impact**: Changes should only touch what is
  necessary. Avoid introducing bugs.
