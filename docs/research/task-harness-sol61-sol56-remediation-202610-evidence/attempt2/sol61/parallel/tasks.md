# Run: receipt 整合
Objective: subtotal cents*quantity、空清單0；label strip/blank Guest；receipt 通過 check.py。
Background / Materials: 現有 amounts.py、labels.py、receipt.py、唯讀 check.py。
Boundaries: 僅三個 source、tasks.md、evidence/；保留 other-plan.md、user-note.txt；無網路、安裝或外部動作。
Definition of Done: 两名原生 workers 完成各自直接檢查，coordinator 整合並通過 check.py。
Authority: tasks.md；coordinator: /root/remfix2_61_parallel
Workspace / baseline: /private/tmp/task-harness-remfix2-aok63ea9/sol61/parallel；原始 source 由 placeholder 組成。
Tools / limits: native collaboration、exec、Python stdlib；恰好兩名 workers、禁止再委派。

| ID | Outcome | Depends on | Owner / handle | State |
| --- | --- | --- | --- | --- |
| T1 | subtotal | none | /root/remfix2_61_parallel/amounts (attempt 1) | done |
| T2 | label | none | /root/remfix2_61_parallel/labels (attempt 1) | done |
| T3 | receipt + check.py | T1,T2 | coordinator (attempt 1) | done |

T1 write scope: amounts.py、evidence/amounts.json；驗收 [(125,2),(50,3)] = 400、[] = 0。
T2 write scope: labels.py、evidence/labels.json；驗收 padded Alice = Alice、blank = Guest。
T3 write scope: receipt.py、evidence/integration.json；驗收 check.py exit 0。

## Checkpoint
尚未 dispatch；無 side effects。

Dispatch observation: both native workers running; evidence/overlap.json.

T1/T2 coordinator acceptance: inspected source and direct-check evidence; SHA256 matches current files.

## Final checkpoint
T1/T2/T3 completed and accepted. check.py exit 0: PASS receipt integration; evidence/integration.json fingerprints current sources and checker. Workers returned terminal completion; active handles none. Unresolved work none; side effects only owned local files.
