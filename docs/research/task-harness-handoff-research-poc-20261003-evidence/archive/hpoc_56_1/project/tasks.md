# Run: implement receipt calculations and labels

Scope / exclusions: Implement only `amounts.py`, `labels.py`, and `receipt.py`; maintain this tracker and evidence under `evidence/`. Preserve all other inputs, including `check.py`, `other-plan.md`, and `user-note.txt`.
Materials and Definition of Done: `subtotal(items)` sums `price_cents * quantity` and handles an empty list; `label(name)` trims surrounding whitespace and returns `Guest` when the result is empty; `receipt(name, items)` returns `<label>: <subtotal> cents`; direct task checks and final integration check pass with stable source fingerprints.
Authority: `tasks.md`
Current coordinator: `/root/hpoc_56_1`
Workspace / baseline: `/private/tmp/task-harness-handoff-poc-xuahb0zu/hpoc_56_1/project`; initial product functions raised `NotImplementedError`.
Available tools / execution limits / permissions: exactly two native workers for T1 and T2, with inherited current model and no further delegation; coordinator owns T3. No network, installation, Git changes, user chats, external actions, sleeps, or timing barriers. Writes limited to `amounts.py`, `labels.py`, `receipt.py`, `tasks.md`, and `evidence/`.

| ID | Outcome | Depends on | Owner / handle | Task attempt | State | Acceptance receipt |
| --- | --- | --- | --- | --- | --- | --- |
| T1 | Implement and directly verify `subtotal` | none | `/root/hpoc_56_1/subtotal_worker` | 1 | done | `evidence/T1-check-1.json` |
| T2 | Implement and directly verify `label` | none | `/root/hpoc_56_1/label_worker` | 1 | done | `evidence/T2-check-2.json` |
| T3 | Integrate and verify `receipt` | T1, T2 | coordinator `/root/hpoc_56_1` | 1 | done | `evidence/T3-check-1.json` |

## T1
Write scope / shared resources: `amounts.py`; distinct evidence path `evidence/T1-check-1.json`.
Inputs and output location: current `amounts.py`; Skill runner at `/private/tmp/task-harness-handoff-poc-xuahb0zu/hpoc_56_1/skill/scripts/run_check.py`.
Task completion criteria: return the sum of each `(price_cents, quantity)` product and return `0` for an empty list.
Verify: direct Python assertions for populated and empty lists, saved by the Skill runner.
Check attempts: worker assigned check T1-check attempt 1 at `evidence/T1-check-1.json`.
Last update: coordinator inspected the implementation and receipt; command, cwd, return code, and stable source fingerprint satisfy T1 acceptance.
Evidence: `evidence/T1-check-1.json`.
Blocker / next action: none; accepted.

## T2
Write scope / shared resources: `labels.py`; distinct evidence path `evidence/T2-check-1.json`.
Inputs and output location: current `labels.py`; Skill runner at `/private/tmp/task-harness-handoff-poc-xuahb0zu/hpoc_56_1/skill/scripts/run_check.py`.
Task completion criteria: strip surrounding whitespace and return `Guest` when the stripped result is empty.
Verify: direct Python assertions for trimmed, whitespace-only, and empty names, saved by the Skill runner.
Check attempts: attempt 1 at `evidence/T2-check-1.json` finished successfully but invoked `python`; coordinator check attempt 2 scheduled at `evidence/T2-check-2.json` to meet the Skill's Python 3 requirement.
Last update: coordinator inspected check attempt 2; command, cwd, return code, and stable source fingerprint satisfy T2 acceptance.
Evidence: accepted `evidence/T2-check-2.json`; `evidence/T2-check-1.json` retained as worker evidence.
Blocker / next action: none; accepted.

## T3
Write scope / shared resources: coordinator writes `receipt.py`, `tasks.md`, and `evidence/T3-check-1.json`.
Inputs and output location: accepted T1 and T2 outputs, current `receipt.py`, read-only `check.py`.
Task completion criteria: format `<label>: <subtotal> cents` using accepted label and subtotal behavior; final integration check passes.
Verify: `python3 check.py`, saved by the Skill runner with fingerprints for all product modules and `check.py`.
Check attempts: integration check attempt 1 scheduled at `evidence/T3-check-1.json`.
Last update: coordinator inspected the integration receipt; command, cwd, successful result, expected PASS output, and stable fingerprints for all product sources plus `check.py` satisfy T3 acceptance.
Evidence: `evidence/T3-check-1.json`.
Blocker / next action: none; accepted.

## Checkpoint
Completed and accepted: T1 via `evidence/T1-check-1.json`; T2 via `evidence/T2-check-2.json`; T3 via `evidence/T3-check-1.json`.
Active worker handles and last observed state: both `/root/hpoc_56_1/subtotal_worker` and `/root/hpoc_56_1/label_worker` terminal; no active workers.
Unresolved work, decisions, and next ready tasks: none.
Side effects attempted and receipt / unknown outcome: all requested outcomes accepted; no unknown outcomes or external side effects.
