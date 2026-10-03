# Run: receipt 整合
Scope: 僅此 fixture；唯讀規則、check.py、other-plan.md、user-note.txt。
Materials / DoD: amounts.py subtotal cents*quantity 總和與空清單 0；labels.py strip 與 blank Guest；receipt.py 整合；check.py 通過。
Authority: tasks.md
Current coordinator: /root/reval03_61_parallel
Workspace / baseline: /private/tmp/task-harness-reval03-rmiru6z0/sol61/parallel；三個函式為 NotImplementedError。
Tools / limits: native workers 兩名，Python3/run_check.py；無網路、安裝、外部操作；不得再委派。

| ID | Outcome | Depends on | Owner | State |
| --- | --- | --- | --- | --- |
| T1 | subtotal 實作與直接驗證 | none | /root/reval03_61_parallel/amounts_worker | done |
| T2 | label 實作與直接驗證 | none | /root/reval03_61_parallel/labels_worker | done |
| T3 | receipt 整合與 check.py | T1,T2 | /root/reval03_61_parallel | done |

T1 scope: amounts.py、evidence/T1-check-1.json。Verify: subtotal 一般與空清單 assert。
T2 scope: labels.py、evidence/T2-check-1.json。Verify: strip 與 blank assert。
T3 scope: receipt.py、evidence/T3-check-1.json。Verify: check.py。
Attempt: 各首次嘗試；Evidence: pending。
Checkpoint: 無已接受結果；待派遣 T1/T2；無外部副作用。

T1 dispatched: /root/reval03_61_parallel/amounts_worker; attempt 1; liveness active.

T2 dispatched: /root/reval03_61_parallel/labels_worker; attempt 1; liveness active.

T1 accepted: evidence/T1-check-1.json; current fingerprint matches. Worker terminal, removed from active handles.

T2 accepted: evidence/T2-check-1.json; current fingerprint matches. Worker terminal, removed from active handles.

T3 attempt 1 started; dependencies accepted; next action receipt integration.

T3 accepted: evidence/T3-check-1.json; all source fingerprints match.
Final checkpoint: T1/T2/T3 done and accepted; no active workers; no unresolved work or external side effects.
