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
4. Choose the existing tracker or a project-compliant task document as the **single source of task state**, with yourself as its current coordinator, including in plan-only mode. Future task owners may remain unassigned. Do not create external issues without authorization. If no location is established, agree a location or keep the draft in chat; do not invent a second tracker. Keep another task's incomplete plan intact.
5. Record actual execution limits: available tools, permitted side effects, and any user/runtime time, cost, or concurrency limits. Never infer a monetary or token budget. Do not create a persistent goal, new chat, automation, or notification merely to run this workflow.

For plan-only, deliver the task list and verification approach, then stop. Do not claim workers or run implementation steps. A plan-only request permits its requested plan artifact, not unrelated project edits.

## Decompose into verifiable outcomes

- Trace the affected flow before choosing boundaries. Prefer a small end-to-end outcome over layers such as “all database work” followed by “all UI work.” Do not split a cohesive small change just to have multiple tasks.
- Give each task a stable ID and acceptance criteria for its requested outcome. For an assessment, completion means a supported verdict, including a negative verdict; keep the assessed object's pass criteria separate. A repair request still requires a verified repair. Record dependencies by ID, not prose ordering alone. Detect missing IDs, self-dependencies, and cycles before dispatch; resolve the contract or regroup the tasks rather than starting a blocked cycle.
- Size tasks so one worker can understand, implement, and verify the outcome with bounded context. File counts and durations are clues, not fixed limits. Split on independent outcomes or ownership boundaries.
- Put uncertainty-reducing checks early. Define shared interfaces before tasks that rely on them. Include integration verification when independently produced outputs must work together.
- Keep an outcome and its acceptance checks in one task; running its checker and saving evidence are not another outcome. Separate integration or independent review only when it has a distinct deliverable and its prerequisites can already be accepted. If an existing check-only successor duplicates its prerequisite's acceptance, record the merge and retained criteria before proceeding, rather than later marking an unstarted task done. Trace readiness through acceptance: even an acyclic dependency graph can deadlock when a prerequisite waits for its successor's verification.
- Keep acceptance criteria stable while executing. New evidence can justify revising the plan, with a reason and impacted tasks recorded; do not drop requirements or weaken tests to manufacture completion.

Use these fields in the existing tracker, or this compact document shape. Retain actual workspace and material baseline, and relevant tools and permissions; mark unknown or inapplicable values explicitly rather than inventing them. Add other detail only when it changes dispatch, verification, or recovery decisions.

```markdown
# Run: <objective>
Scope / exclusions:
Materials and Definition of Done:
Authority: <this file or tracker URL>
Current coordinator: this agent <actual handle if available; task owners are separate below>
Workspace / baseline: <actual root, revision and relevant dirty files, or artifact versions>
Available tools / execution limits / permissions:

| ID | Outcome | Depends on | Owner / handle | Task attempt | State | Acceptance receipt |
| --- | --- | --- | --- | --- | --- | --- |
| T1 | ... | none | unassigned | not started | pending | none |

## T1
Write scope / shared resources:
Inputs and output location:
Task completion criteria: <what this task must deliver; an assessment delivers a supported verdict>
Subject pass/fail criteria (assessment only): <how the evaluated object is judged; a negative verdict can complete the assessment>
Verify: <command or observable scenario and expected result>
Check attempts: <check ID, numeric attempt, receipt path; separate from task/dispatch attempt>
Last update:
Evidence: <receipt artifact path or resolvable native receipt ID; keep exact commands, results and fingerprints in the receipt>
Blocker / next action:

## Checkpoint
Completed and accepted:
Active worker handles and last observed state:
Unresolved work, decisions, and next ready tasks:
Side effects attempted and receipt / unknown outcome:
```

## Assign only ready work

A task is ready when its dependencies are **done and still valid**, its inputs exist, its scope is authorized, and its write scope does not conflict with active work. `pending` does not itself mean ready.

- Use a single coordinator as the writer of task state. Workers return results; they do not race to edit the shared list. Complete the start checkpoint below for one task before starting another; parallel workers may execute concurrently after their individual dispatch records are saved.
- Use native subagents only when permitted and useful. Independent investigations or disjoint writes may run in parallel; dependent tasks and overlapping writes run sequentially. Without delegation tools or authorization, execute ready tasks serially and record `owner: coordinator`.
- When using parallel workers, select a ready, non-conflicting group within authorized concurrency and available capacity. Dispatch each worker and save its individual start checkpoint before dispatching the next. Finish this group's dispatches before actively waiting, collecting or accepting results, or doing unrelated work. Automatic completion notifications and workers finishing during dispatch do not violate this order. If readiness, capacity or safety changes, record why the group changed or dispatch stopped; reconcile failures before continuing.
- Assess dispatch order separately from execution overlap. Use native calls to verify the protocol above; record worker overlap and dispatch delays as observations. Neither zero overlap nor a worker finishing before the next dispatch proves a protocol failure or its cause. Do not require all dispatches to precede the first completion or insert artificial waits to manufacture overlap. If actual overlap is explicitly required, verify and report that outcome separately.
- Before parallel writes, identify overlapping paths **and shared mutable resources** such as a database, generated outputs, dependency lockfiles, or service ports. Give each resource one writer, isolate it using supported facilities, or serialize. A branch name is not filesystem isolation.
- Check existing worker handles before reassignment. Never launch a replacement while a previous worker may still write the same scope. Confirm it stopped or isolate the new attempt first. Record takeover rather than trusting elapsed time as proof of death.
- After the group's dispatches, keep the critical path moving: integrate completed results and dispatch newly ready tasks without waiting for unrelated workers. Bound concurrency by useful independent work and real host limits, not the number of available slots.

Send each worker this contract, with only the relevant context:

```text
Task ID / outcome:
Inputs: exact workspace, instructions, source paths, dependency outputs.
Ownership: product files/resources AND a distinct authorized evidence path for this task's checks; excluded areas. If only product writes are authorized, the coordinator owns receipt-producing verification before acceptance.
You are not alone in this workspace. Preserve others' changes and adapt to them.
Task completion criteria and verification: requested deliverable and direct checks; separate subject pass/fail criteria for assessments.
Limits: authorized operations, relevant runtime/user limits, stopping condition.
Return: changed artifacts, receipt paths from the evidence procedure below, unresolved issues. Do not retype commands, exit codes or fingerprints into the tracker; reference the receipts that contain them.
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
| done | Task completion criteria and applicable integration checks passed. An assessment may be done with a negative subject verdict; an unverified repair may not. |
| blocked | Work requires missing input, permission, an external change, or diagnosis after exhausted retries. Record the specific unblock action. |

These are task-list labels, not instructions to change a host's persistent-goal status. Follow the host's own lifecycle rules.

1. **Start one task.** First confirm each dependency has valid acceptance evidence and its done write succeeded. This gate applies before implementation, including coordinator work; deferring only the final check does not satisfy it. Follow the applicable sequence, completing its tracker write before another dispatch or other work:
   - Delegated: dispatch one worker → use the returned handle to persist owner, numeric task attempt and running → select the next ready task. If output is already available, record verifying instead. A failed dispatch does not mean running; do not batch several successful dispatches into one later checkpoint.
   - Coordinator-owned, including a separately tracked check: persist owner, numeric attempt and running → wait for that write to succeed → issue the task's first action. Keep this checkpoint separate from product mutations; a combined multi-file patch does not establish a preceding checkpoint.
   The first task execution/dispatch attempt is 1. A new execution increments that task's known attempt after reconciling prior state. If historical counts are absent, retain `historical attempts: unknown`; a prior done/running entry does not prove a total count of 1. After reconciling artifacts, worker liveness and side effects, use an explicitly named resume epoch with local task/check counters starting at 1 for safe new work; this does not authorize replay of an unknown side effect. Track check attempts separately by check ID; before a coordinator-run check or safe retry, persist its numeric attempt and new receipt path, then wait for that write to succeed before invoking it. Workers save their check attempts in their assigned evidence paths and return the references for the coordinator to record. Do not infer a task restart from a check retry or overwrite earlier receipts.
   If a tracker write fails, reconcile before proceeding.
2. **Produce and inspect.** Execute the smallest change within ownership, then inspect actual artifacts and relevant diffs. Update coordination before widening scope. Integrate into the authoritative workspace and check the affected combined path; isolated success does not prove the final combination works. Preserve unrelated changes.
3. **Check and retain receipts.** Map task completion criteria to direct checks, including relevant boundaries and user-visible flows. For local acceptance or retry checks, use Python 3 and the bundled [run_check.py](scripts/run_check.py) to save the actual process result and relevant source fingerprints. Give each attempt its own authorized evidence path and run one command per receipt:
   ```sh
   python3 <skill-dir>/scripts/run_check.py --output evidence/T1-check-1.json --source module.py --source check.py -- python3 check.py
   ```
   The runner does not retry or use shell expansion. Do not wrap several acceptance commands in a shell pipeline/batch: its receipt covers only the invoked process. Read the saved JSON; require state `finished` and stable sources before accepting a version. A nonzero command returncode is a failed check, even if stdout says PASS. `started` or `unknown` requires reconciliation; `not_started` has no process exit code. The runner's own exit can differ on launch failure or source changes, so the JSON is authoritative. Cite the receipt path rather than manually copying commands, exit codes or digests. Native structured observations may instead use a resolvable native receipt; do not invent shell exits for them. If Python 3 is unavailable, record that command-receipt verification is blocked rather than fabricating evidence. Equivalent reproduction commands must be labeled separately from actual invocations.
4. **Accept the tested version.** Read each task's own receipt and check its actual command, cwd, result and source fingerprints against the artifacts being accepted. Bind receipts to revision plus relevant dirty-file information, or artifact fingerprints. If a worker cannot supply attributable verification, keep the task verifying and have the coordinator check the current artifacts using a new authorized receipt; label it as coordinator verification. Do not substitute a successor's later integration receipt for prerequisite acceptance. When accepted inputs or outputs change, reopen affected acceptance checks. A success message, running test, screenshot without the required interaction, or old green log is not acceptance. Missing required verification keeps the task verifying or blocked. For meaningful risk or subjective criteria, use an independent evaluator when permitted, with requirements and raw artifacts rather than a desired verdict; do not build a reviewer hierarchy by default.
5. **Persist and hand off: two successful writes.** After coordinator acceptance, perform this sequence for a dependent task:
   - Write the accepted prerequisite's receipt reference and done state; leave the dependent task pending. Read the write's success result before proceeding.
   - Recheck readiness, then use a separate write to save the dependent task's start checkpoint from step 1. Read this write's success result before its first product action.
   Never combine prerequisite done and dependent running in one patch or file write. Two sequential awaited tool operations may share an outer call; two state edits inside one write do not satisfy the sequence. On either write failure, reconcile the saved state before proceeding.

## Recover without replaying blindly

- Checkpoint after meaningful accepted results and before handing off or ending a session. Record task states, artifact locations, verification results, failures, and the next action. Refresh worker liveness separately from task acceptance: move confirmed terminal handles out of the active list while retaining their history, and label unconfirmed liveness explicitly. Exclude credentials and unnecessary sensitive output.
- On resume, reread instructions and the authoritative list; inspect actual artifacts, current changes, and live workers. Reconcile differences before dispatch. A saved `running` state is not proof of life, and a saved `done` state is not proof that the current output still passes.
- Treat a timeout or lost response as **unknown outcome**. Check receipts, resulting state, and operation IDs before retrying a mutation. Use the service's idempotency facility when available. If a consequential side effect cannot be reconciled safely, block that task and request the needed decision; do not reissue it optimistically.
- Use the host's bounded retry policy if one exists. Otherwise, for a safe transient operation, make one retry after checking state. For a failed implementation check, diagnose and make a targeted repair; stop repeating the same failure without new evidence. Replan or block the affected task while continuing unrelated ready work.
- Stop dispatching on cancellation, exhausted explicit limits, an unresolved authorization boundary, or when no safe ready work remains. Respect cancellation of active workers using available controls and report any unconfirmed stop. Preserve a checkpoint; do not imply automatic future execution.

## Close the loop

Reconcile every requested outcome with the task list and final integrated artifacts. Report accepted results, failed or unverified items, and concrete blockers with evidence links. Only claim overall completion when the whole Definition of Done passes; distinguish a completed plan from completed implementation. If work remains, leave the exact resume action and current state, not a generic promise to continue.
