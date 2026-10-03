# Run: receipt integration
Objective / scope: subtotal cents*quantity and empty list 0; strip label and blank Guest; integrate receipt. Protected inputs remain readonly.
Materials / Definition of Done: amounts.py, labels.py, receipt.py and check.py; direct worker acceptance plus integrated check.py passes with stable fingerprints.
Authority: tasks.md
Current coordinator: /root/followup_61_parallel
Workspace / baseline: /private/tmp/harness-followup-_hch7aol/sol61/parallel; initial Python stubs, no existing tasks.md.
Tools / limits: Python3, native workers exactly two; no worker delegation, network, installs or writes outside fixture. Coordinator exclusively owns tasks.md and receipt.py. Workers own separate modules and evidence paths.

| ID | Outcome | Depends on | Owner | Task attempt | State | Acceptance receipt |
| --- | --- | --- | --- | --- | --- | --- |
| T1 | subtotal | none | /root/followup_61_parallel/amount_worker | 1 | done | evidence/T1-check-1.json |
| T2 | label | none | /root/followup_61_parallel/label_worker | 1 | done | evidence/T2-check-1.json |
| T3 | receipt integration | T1,T2 | coordinator | 1 | done | evidence/T3-check-1.json |

## Acceptance / ownership
T1: amounts.py and evidence/T1-check-1.json; verify mixed quantities and empty list.
T2: labels.py and evidence/T2-check-1.json; verify stripping and whitespace fallback.
T3: receipt.py and evidence/T3-check-1.json; check.py covers both receipt paths. Prerequisites must be accepted before implementation.
Check attempts: T1 check 1 evidence/T1-check-1.json accepted by coordinator.

## Checkpoint
Completed and accepted: T1, T2, T3 with their individual receipts. Active worker handles: none; both native workers terminal. Unresolved work: none. Side effects: local authorized modules, task state and evidence only. Protected inputs preserved.

T2 check 1 accepted: evidence/T2-check-1.json. Both prerequisite module fingerprints match current artifacts. Worker handles terminal.

T3 check attempt 1 registered before invocation: evidence/T3-check-1.json. T3 verifying.

T3 check 1 accepted by coordinator after reading receipt and matching all current source fingerprints. Definition of Done satisfied.
