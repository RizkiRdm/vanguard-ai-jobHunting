# before kerja

You are assisting in the development of an ongoing software project.

## SOURCE OF TRUTH

You MUST treat the provided Project State Document as the single source of truth.

Current Project State:
[PASTE / ATTACH project_state.md]

---

## TASK

Your objective:

[DESCRIBE THE TASK CLEARLY]

---

## EXECUTION RULES (STRICT)

1. Architecture Integrity

- Do NOT contradict or override existing architecture decisions.
- Do NOT introduce new patterns unless absolutely necessary and justified.

2. Context Awareness

- Always reference the current Project State before making decisions.
- Ensure all outputs are consistent with existing modules, structure, and constraints.

3. Minimal Change Principle

- Implement ONLY what is required for this task.
- Avoid unnecessary refactoring or unrelated improvements.

4. Dependency Discipline

- Respect existing dependency direction and module boundaries.
- Do NOT introduce circular dependencies.

5. Deterministic Output

- Avoid ambiguity.
- Make decisions explicit and consistent.

---

## OUTPUT FORMAT (MANDATORY)

### Implementation Plan

- Brief step-by-step plan before execution

### Changes Made

- List of files created/modified
- Short explanation per change

### Code Output

Use file-based format:

# FILE: path/to/file.py

<code>

# FILE: path/to/another_file.py

<code>

---

### Project State Update (MANDATORY)

Update the Project State Document to reflect:

- New components
- Modified structure
- New decisions (if any)

Return ONLY the updated sections (not the full document).

---

## SELF-CHECK (BEFORE FINALIZING)

- Does this contradict the existing architecture? → If yes, fix it
- Are all imports valid and consistent? → Verify
- Is the change minimal and scoped? → Ensure
- Is Project State updated correctly? → Mandatory

---

## FAILURE CONDITIONS (AVOID)

- Ignoring Project State
- Introducing new architecture without justification
- Making undocumented changes
- Generating inconsistent multi-file code

---

## GOAL

Ensure every change:

- Is traceable
- Is consistent
- Keeps the system stable
- Moves the project forward without creating hidden complexity

# setelah before bekerja

[upload doc project_state.md & dev_log.md]
Update the project state document and dev log document based on the work we just did.
return the full updated document
