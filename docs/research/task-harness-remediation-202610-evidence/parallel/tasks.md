# Run: Complete receipt helpers and assembly
Scope / exclusions: Implement amounts.subtotal, labels.label, and receipt.receipt. Preserve check.py, other-plan.md, and user-note.txt.
Materials and Definition of Done: Existing Python modules and check.py; `python check.py` prints `PASS receipt integration`.
Authority: This file; coordinator: /root/remediation_parallel.
Workspace / baseline: /private/tmp/task-harness-remediation-w5zjr1sb/parallel; no Git repository; three functions initially raise NotImplementedError.
Execution limits / permissions: Exactly two native subagents for disjoint helper files; no network, new chats, or installation. Coordinator owns this tracker, receipt.py, and evidence/.

| ID | Outcome | Depends on | Owner / handle | State |
| --- | --- | --- | --- | --- |
| T1 | subtotal sums cents times quantity, empty list returns 0 | none | /root/remediation_parallel/amounts_helper | done |
| T2 | label trims name, blank becomes Guest | none | /root/remediation_parallel/labels_helper | done |
| T3 | receipt formats label and subtotal | T1, T2 | coordinator | done |

## T1
Write scope: amounts.py and evidence/amounts/ only.
Acceptance: `subtotal([(125,2),(50,3)]) == 400`; `subtotal([]) == 0`.
Verify: direct Python assertions and final check.py.
Attempt / last update: 1; coordinator accepted direct check on current file.
Evidence: `python -c` assertions printed `PASS subtotal`; SHA-256 `0d19972bf19c9ba8d3376c6cbd0848edbd15c062747da4e224d2c6ce94dd1a07`.

## T2
Write scope: labels.py and evidence/labels/ only.
Acceptance: `label("  Alice  ") == "Alice"`; `label(" ") == "Guest"`.
Verify: direct Python assertions and final check.py.
Attempt / last update: 1; coordinator accepted direct check on current file.
Evidence: `python -c` assertions printed `PASS label`; SHA-256 `bf323853530fd47713761cb3c51f6b548f4dafa5ea8602b2a5f00d69bbf5fe1e`.

## T3
Write scope: receipt.py and evidence/ root.
Acceptance: `receipt(name, items) == '<label>: <subtotal> cents'` using the helpers; all check.py assertions pass.
Verify: `python check.py` in the authoritative workspace.
Attempt / last update: 1; integrated and accepted.
Evidence: `python check.py` exited 0 and printed `PASS receipt integration`; receipt.py SHA-256 `381c74b71cb5e233ca980493afa5a2acb7e9d9991cf0f484e69ee883f4768b6b`; see evidence/check.txt.

## Checkpoint
Completed and accepted: T1, T2, T3 on current files; final integrated check passed.
Active worker handles and last observed state: both workers returned final answers; initial running overlap in evidence/overlap.json.
Unresolved work, decisions, and next ready tasks: none.
Side effects attempted and receipt / unknown outcome: tracker created; two successful native spawns; overlap observation saved; receipt.py implemented; final check evidence saved. No unknown outcomes.
