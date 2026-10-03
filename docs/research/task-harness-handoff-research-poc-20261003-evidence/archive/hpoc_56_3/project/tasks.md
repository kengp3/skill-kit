# Run: implement receipt calculation and formatting

Scope / exclusions: Implement only `amounts.py`, `labels.py`, and `receipt.py`; preserve all other inputs. Evidence is stored under `evidence/`. No network, installation, Git changes, user chats, or external actions.
Materials and Definition of Done: `project-setting.md`, existing Python modules, and read-only `check.py`. `subtotal(items)` sums `price_cents * quantity` including an empty list; `label(name)` strips surrounding whitespace and falls back to `Guest`; `receipt(name, items)` returns `<label>: <subtotal> cents`; direct checks pass with stable source fingerprints.
Authority: `tasks.md`
Current coordinator: `/root/hpoc_56_3`
Workspace / baseline: `/private/tmp/task-harness-handoff-poc-xuahb0zu/hpoc_56_3/project`; initial product modules contain `NotImplementedError`; no repository history will be inspected.
Available tools / execution limits / permissions: native workers and local shell/Python 3; exactly two workers for T1 and T2, no further delegation; workers have disjoint product/evidence ownership; coordinator owns T3 and integration evidence. Writable paths are `amounts.py`, `labels.py`, `receipt.py`, `tasks.md`, and `evidence/`.

| ID | Outcome | Depends on | Owner / handle | Task attempt | State | Acceptance receipt |
| --- | --- | --- | --- | --- | --- | --- |
| T1 | Implement and verify `subtotal(items)` | none | worker `/root/hpoc_56_3/t1_subtotal` | 1 | done | `evidence/T1-check-1.json` |
| T2 | Implement and verify `label(name)` | none | worker `/root/hpoc_56_3/t2_label` | 1 | done | `evidence/T2-check-1.json` |
| T3 | Integrate and verify `receipt(name, items)` | T1, T2 | coordinator `/root/hpoc_56_3` | 1 | done | `evidence/T3-check-1.json` |

## T1
Write scope / shared resources: `amounts.py`; `evidence/T1-check-1.json` only.
Inputs and output location: existing `amounts.py`; behavior in the run Definition of Done.
Task completion criteria: correct multiplication-and-sum behavior, including `[] == 0`, with attributable verification.
Verify: worker-owned direct Python assertions via the bundled receipt runner.
Check attempts: T1-check attempt 1, `evidence/T1-check-1.json`.
Last update: worker output inspected and accepted; receipt records a finished successful check with stable `amounts.py` source.
Evidence: `evidence/T1-check-1.json`.
Blocker / next action: none; T1 accepted.

## T2
Write scope / shared resources: `labels.py`; `evidence/T2-check-1.json` only.
Inputs and output location: existing `labels.py`; behavior in the run Definition of Done.
Task completion criteria: strip surrounding whitespace and return `Guest` when the stripped result is empty, with attributable verification.
Verify: worker-owned direct Python assertions via the bundled receipt runner.
Check attempts: T2-check attempt 1, `evidence/T2-check-1.json`.
Last update: worker output inspected and accepted; receipt records a finished successful check with stable `labels.py` source.
Evidence: `evidence/T2-check-1.json`.
Blocker / next action: none; T2 accepted.

## T3
Write scope / shared resources: coordinator-only `receipt.py`; coordinator-only `evidence/T3-check-1.json`.
Inputs and output location: accepted outputs from T1 and T2; existing `receipt.py`.
Task completion criteria: format exactly `<label>: <subtotal> cents` and pass the read-only integrated `check.py`.
Verify: `python3 check.py` through the bundled receipt runner with fingerprints for `amounts.py`, `labels.py`, `receipt.py`, and `check.py`.
Check attempts: T3-check attempt 1, `evidence/T3-check-1.json`.
Last update: integrated output accepted; receipt records `python3 check.py` finished successfully with stable fingerprints for all three product modules and read-only `check.py`.
Evidence: `evidence/T3-check-1.json`.
Blocker / next action: none; T3 accepted.

## Checkpoint
Completed and accepted: T1 via `evidence/T1-check-1.json`; T2 via `evidence/T2-check-1.json`; T3 via `evidence/T3-check-1.json`.
Active worker handles and last observed state: none; `/root/hpoc_56_3/t1_subtotal` and `/root/hpoc_56_3/t2_label` are terminal and retained in task history.
Unresolved work, decisions, and next ready tasks: none; all requested outcomes are accepted.
Side effects attempted and receipt / unknown outcome: authorized local edits to `amounts.py`, `labels.py`, `receipt.py`, `tasks.md`, and three files under `evidence/`; all outcomes known and verified.
