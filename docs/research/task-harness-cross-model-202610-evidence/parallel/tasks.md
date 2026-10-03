# Run: Receipt formatter

Scope: Implement `subtotal`, `label`, and `receipt`; preserve `check.py` and unrelated files.
Materials and Definition of Done: Existing Python stubs and `check.py`; all specified cases and `python3 check.py` pass.
Authority: This file; coordinator: `/root/sol_harness_parallel`.
Workspace / baseline: `/private/tmp/task-harness-cross-model-b3f6us9z/parallel`; no Git repository. Baseline fingerprints are in `evidence/baseline.txt`.
Execution limits / permissions: Fixture writes only; two native subagents max, `gpt-6-sol`, no worker delegation; coordinator alone writes this file.

| ID | Outcome | Depends on | Owner / handle | State |
| --- | --- | --- | --- | --- |
| T1 | `amounts.subtotal` computes cents total, empty list 0 | none | `/root/sol_harness_parallel/amounts` | done |
| T2 | `labels.label` trims name, blank becomes Guest | none | `/root/sol_harness_parallel/labels` | done |
| T3 | `receipt.receipt` formats label and subtotal | T1, T2 | coordinator | done |
| T4 | Integrated `check.py` passes and preserved files verified | T1, T2, T3 | coordinator | done |

## T1
Write scope: `amounts.py` only. Acceptance: integer cents price times quantity summed; empty list 0. Verify direct Python assertions and inspect final file. Attempt: 1; dispatched to actual handle `/root/sol_harness_parallel/amounts`. Worker completed; coordinator inspected implementation and ran direct assertions (exit 0). SHA-256: `d65448402b1b7d8f036255cc1f850116cc56d05e7ba62c2151ac3586d7c24d5a`.

## T2
Write scope: `labels.py` only. Acceptance: surrounding whitespace trimmed; whitespace-only input becomes `Guest`. Verify direct Python assertions and inspect final file. Attempt: 1; dispatched to actual handle `/root/sol_harness_parallel/labels`. Worker completed; coordinator inspected implementation and ran direct assertions (exit 0). SHA-256: `bf323853530fd47713761cb3c51f6b548f4dafa5ea8602b2a5f00d69bbf5fe1e`.

## T3
Write scope: `receipt.py` only. Acceptance: returns `<label>: <subtotal> cents` using outputs of T1 and T2. Verify `check.py` after dependencies complete. Attempt: 1; coordinator changed the file. `python3 check.py` exit 0. SHA-256: `381c74b71cb5e233ca980493afa5a2acb7e9d9991cf0f484e69ee883f4768b6b`.

## T4
Write scope: `evidence/` and this task list. Acceptance: `python3 check.py` passes; `check.py`, `other-plan.md`, `user-note.txt`, `project-setting.md` match baseline hashes. Attempt: 1; command exit 0, output `PASS receipt integration`; all four preserved files match baseline hashes. See `evidence/integration.txt`.

## Checkpoint
Completed and accepted: T1, T2, T3, T4.
Active worker handles: none.
Next ready tasks: none.
Side effects: created task list and evidence; two worker dispatches succeeded; updated three function files. Live overlap was not observed as a simultaneous-running snapshot; see `evidence/dispatch.txt`.
