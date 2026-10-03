# Run: receipt integration
Scope: amounts.py, labels.py, receipt.py; preserve read-only materials and unrelated work.
Materials / DoD: check.py contracts; subtotal sum cents*quantity (empty 0), stripped label (blank Guest), integrated receipt; all checks pass.
Authority: tasks.md
Current coordinator: /root/remfix5_61_parallel
Workspace / baseline: /private/tmp/task-harness-remfix5-arjbvmfd/sol61/parallel; three NotImplementedError stubs, no existing tracker.
Tools / limits: native workers and local Python; no network/install/external actions; exactly two workers, disjoint source/evidence scopes.

| ID | Outcome | Depends on | Owner | State |
| --- | --- | --- | --- | --- |
| T1 | subtotal and direct check | none | /root/remfix5_61_parallel/amounts_worker | done |
| T2 | label and direct check | none | /root/remfix5_61_parallel/labels_worker | done |
| T3 | receipt integration and check.py | T1,T2 | /root/remfix5_61_parallel | done |

T1 scope: amounts.py, evidence/T1-check-1.json. Acceptance: supplied subtotal cases, finished stable receipt.
T2 scope: labels.py, evidence/T2-check-1.json. Acceptance: supplied label cases, finished stable receipt.
T3 scope: receipt.py, evidence/T3-check-1.json. Acceptance: full check.py, finished stable receipt.

## Checkpoint
T1, T2, T3 accepted. Both worker handles terminal; no active workers. No unresolved work. No side effects outside local fixture.

T1 attempt 1: native dispatch succeeded; worker active, direct check pending.

T2 attempt 1: native dispatch succeeded; worker active, direct check pending.

T1 accepted: evidence/T1-check-1.json; current fingerprints match. Worker terminal.

T2 accepted: evidence/T2-check-1.json; current fingerprints match. Worker terminal.

T3 attempt 1 started: T1 and T2 accepted and valid; coordinator owns receipt.py.

T3 accepted: evidence/T3-check-1.json; full check.py passes, current fingerprints match. Definition of Done complete.
