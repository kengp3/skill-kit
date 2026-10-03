---
name: task-harness
description: Break a multi-step request into a persistent task list, assign bounded work, execute dependency-ready tasks, verify results, and resume interrupted work. Use for task decomposition, coordinated execution, or continuing an existing task plan. A request to plan alone does not authorize implementation.
---

# Task Harness

Coordinate work using the host's existing tools and one authoritative task list. This is an operating workflow, not a scheduler or a replacement agent runtime. Match the user's language.

## Establish the run

1. Identify **plan-only**, **execute**, or **resume** from the request. When planning and execution are both requested, continue after planning within that authorization. Resume inherits existing boundaries, not additional permissions.
2. Read the actual project instructions, relevant files, current changes, existing plan, and available tools. Confirm the project root; obey its document-placement rules before writing. Preserve unrelated work.
3. Capture the objective, scope, materials, meaningful assumptions, and Definition of Done. Reuse an existing brief. Ask only the unresolved question that changes the outcome; continue independent work when possible.
4. Choose the existing tracker or a project-compliant task document as the **single source of task state**. Do not create external issues without authorization. If no location is established, agree a location or keep the draft in chat; do not invent a second tracker. Keep another task's incomplete plan intact.
5. Record actual execution limits: available tools, permitted side effects, and any user/runtime time, cost, or concurrency limits. Never infer a monetary or token budget. Do not create a persistent goal, new chat, automation, or notification merely to run this workflow.

For plan-only, deliver the task list and verification approach, then stop. Do not claim workers or run implementation steps. A plan-only request permits its requested plan artifact, not unrelated project edits.

## Decompose into verifiable outcomes

- Trace the affected flow before choosing boundaries. Prefer a small end-to-end outcome over layers such as “all database work” followed by “all UI work.” Do not split a cohesive small change just to have multiple tasks.
- Give each task a stable ID and concrete acceptance criteria. Record dependencies by ID, not prose ordering alone. Detect missing IDs, self-dependencies, and cycles before dispatch; resolve the contract or regroup the tasks rather than starting a blocked cycle.
- Size tasks so one worker can understand, implement, and verify the outcome with bounded context. File counts and durations are clues, not fixed limits. Split on independent outcomes or ownership boundaries.
- Put uncertainty-reducing checks early. Define shared interfaces before tasks that rely on them. Include integration verification when independently produced outputs must work together.
- Keep an outcome and the checks needed to accept it in the same task. A separate integration task may depend on independently accepted outcomes, but must not gate those prerequisites' own completion. Trace readiness through acceptance before dispatch: an acyclic dependency graph can still deadlock when a prerequisite waits for its successor's verification.
- Keep acceptance criteria stable while executing. New evidence can justify revising the plan, with a reason and impacted tasks recorded; do not drop requirements or weaken tests to manufacture completion.

Use these fields in the existing tracker, or this compact document shape. Add detail only when it changes dispatch, verification, or recovery decisions.

```markdown
# Run: <objective>
Scope / exclusions:
Materials and Definition of Done:
Authority: <this file or tracker URL>; coordinator: <owner>
Workspace / baseline: <actual root, revision and relevant dirty files, or artifact versions>
Execution limits / permissions:

| ID | Outcome | Depends on | Owner / handle | State |
| --- | --- | --- | --- | --- |
| T1 | ... | none | unassigned | pending |

## T1
Write scope / shared resources:
Inputs and output location:
Acceptance:
Verify: <command or observable scenario and expected result>
Attempt / last update:
Evidence: <actual command, result, artifact path, tested revision or file fingerprint>
Blocker / next action:

## Checkpoint
Completed and accepted:
Active worker handles and last observed state:
Unresolved work, decisions, and next ready tasks:
Side effects attempted and receipt / unknown outcome:
```

## Assign only ready work

A task is ready when its dependencies are **done and still valid**, its inputs exist, its scope is authorized, and its write scope does not conflict with active work. `pending` does not itself mean ready.

- Use a single coordinator as the writer of task state. Workers return results; they do not race to edit the shared list. Record the owner, attempt, and actual tool-returned worker handle when dispatch succeeds. Dispatch failure does not mean running.
- Use native subagents only when permitted and useful. Independent investigations or disjoint writes may run in parallel; dependent tasks and overlapping writes run sequentially. Without delegation tools or authorization, execute ready tasks serially and record `owner: coordinator`.
- Before parallel writes, identify overlapping paths **and shared mutable resources** such as a database, generated outputs, dependency lockfiles, or service ports. Give each resource one writer, isolate it using supported facilities, or serialize. A branch name is not filesystem isolation.
- Check existing worker handles before reassignment. Never launch a replacement while a previous worker may still write the same scope. Confirm it stopped or isolate the new attempt first. Record takeover rather than trusting elapsed time as proof of death.
- Keep the critical path moving: integrate completed results and dispatch newly ready tasks without waiting for unrelated workers. Bound concurrency by useful independent work and real host limits, not the number of available slots.

Send each worker this contract, with only the relevant context:

```text
Task ID / outcome:
Inputs: exact workspace, instructions, source paths, dependency outputs.
Ownership: files/resources you may change; excluded areas.
You are not alone in this workspace. Preserve others' changes and adapt to them.
Acceptance and verification: expected behavior and direct checks.
Limits: authorized operations, relevant runtime/user limits, stopping condition.
Return: changed artifacts, commands and results, tested version, unresolved issues.
Do not update the shared task list or delegate again unless assigned that responsibility.
```

Use real tool handles, not invented agent identities. User-visible chats are not interchangeable with subagents. Follow the host's authorization rules for creating or messaging chats and for external actions.

## Execute, verify, integrate

Use these task states, mapped to equivalent existing tracker states if needed:

| State | Meaning / transition |
| --- | --- |
| pending | Not started, or deliberately reopened with a recorded reason. Dispatch only after readiness checks. |
| running | Coordinator is executing, or a worker was successfully started. |
| verifying | Output exists; acceptance or integration checks remain. |
| done | Acceptance and applicable integration checks passed on the current artifact. |
| blocked | Work requires missing input, permission, an external change, or diagnosis after exhausted retries. Record the specific unblock action. |

These are task-list labels, not instructions to change a host's persistent-goal status. Follow the host's own lifecycle rules.

1. Execute the smallest change that satisfies the task. Reuse existing tools and checks. Keep implementation within ownership; update coordination before widening a write scope.
2. Inspect each worker's actual artifacts and relevant diff. A success message, running test, screenshot without the required interaction, or old green log is not acceptance evidence.
3. Run the task's direct checks and inspect final results. For user-visible behavior, exercise the relevant real flow where feasible; unit tests alone may miss integration failures. Missing required verification keeps the task `verifying` or `blocked`, not `done`.
4. Integrate into the authoritative workspace and test the affected combined path. Passing in a worker's isolated checkout does not prove the final combination works. Do not revert unrelated changes to make integration easy.
5. Record evidence with the tested version: revision plus dirty-file information, or fingerprints of relevant artifacts. When inputs or accepted output change, invalidate affected evidence and reopen dependent acceptance checks; unrelated changes need not trigger a full rerun.
6. Mark done only after the coordinator accepts the evidence. For meaningful risk or subjective criteria, use an independent evaluator when permitted, giving it requirements and raw artifacts rather than the author's desired verdict. Use deterministic checks when they settle the question; do not build a reviewer hierarchy by default.

## Recover without replaying blindly

- Checkpoint after meaningful accepted results and before handing off or ending a session. Record enough to resume: task states, artifact locations, worker handles, verification results, known failures, and the next action. Exclude credentials and unnecessary sensitive output.
- On resume, reread instructions and the authoritative list; inspect actual artifacts, current changes, and live workers. Reconcile differences before dispatch. A saved `running` state is not proof of life, and a saved `done` state is not proof that the current output still passes.
- Treat a timeout or lost response as **unknown outcome**. Check receipts, resulting state, and operation IDs before retrying a mutation. Use the service's idempotency facility when available. If a consequential side effect cannot be reconciled safely, block that task and request the needed decision; do not reissue it optimistically.
- Use the host's bounded retry policy if one exists. Otherwise, for a safe transient operation, make one retry after checking state. For a failed implementation check, diagnose and make a targeted repair; stop repeating the same failure without new evidence. Replan or block the affected task while continuing unrelated ready work.
- Stop dispatching on cancellation, exhausted explicit limits, an unresolved authorization boundary, or when no safe ready work remains. Respect cancellation of active workers using available controls and report any unconfirmed stop. Preserve a checkpoint; do not imply automatic future execution.

## Close the loop

Reconcile every requested outcome with the task list and final integrated artifacts. Report accepted results, failed or unverified items, and concrete blockers with evidence links. Only claim overall completion when the whole Definition of Done passes; distinguish a completed plan from completed implementation. If work remains, leave the exact resume action and current state, not a generic promise to continue.
