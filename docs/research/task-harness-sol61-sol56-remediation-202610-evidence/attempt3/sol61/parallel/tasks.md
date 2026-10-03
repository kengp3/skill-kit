# Run: receipt integration
Scope: amounts.py, labels.py, receipt.py; preserve all read-only materials.
Materials / DoD: check.py passes, sum cents*quantity including empty; strip names with Guest fallback.
Authority: tasks.md; coordinator: /root/remfix3_61_parallel
Workspace: /private/tmp/task-harness-remfix3-1nis2bc6/sol61/parallel; baseline three NotImplementedError functions.
Tools / limits: native workers and local Python; exactly two workers, disjoint writes; no network/install/external actions.

| ID | Outcome | Depends on | Owner / handle | State |
| --- | --- | --- | --- | --- |
| T1 | subtotal | none | /root/remfix3_61_parallel/amounts; attempt 1 | done |
| T2 | label | none | /root/remfix3_61_parallel/labels; attempt 1 | done |
| T3 | receipt integration and check.py | T1,T2 | coordinator; attempt 1 | done |

Acceptance: T1 subtotal([(125,2),(50,3)])=400 and subtotal([])=0; T2 label('  Alice  ')='Alice' and label(' ')='Guest'; T3 check.py exits 0.
Evidence: pending.

## Checkpoint
Active handles: /root/remfix3_61_parallel/amounts and /root/remfix3_61_parallel/labels; last native observation running for both immediately after second spawn (evidence/overlap.json).
Shared mutable resources: none; each worker writes one exclusive Python file. Coordinator alone writes tasks.md and evidence/.
T1 inputs/output: amounts.py; T2 inputs/output: labels.py; T3 receipt.py. All contracts read from check.py.
Next: accept worker receipts on unchanged fingerprints, persist done before T3 start; integrate receipt and run check.py.
Side effects: local fixture writes only.

T2 accepted: worker receipt e790c9 exit 0; unchanged SHA256 confirmed; evidence/labels.json. Handle terminal (completed).

T1 accepted: receipt d4a5b1 exit 0, unchanged SHA256 confirmed; evidence/amounts.json. Handle terminal (completed).

T3 start checkpoint: both prerequisites accepted and persisted; implement receipt then verify integrated check.py.

Final checkpoint: T1,T2,T3 accepted; python3 -B check.py receipt 8a3a09 exit 0, PASS receipt integration. Fingerprints in evidence/integration.json. Active worker handles: none; both completed. No unresolved work or blockers; protected files unchanged.
