# Run: receipt 整合
Scope: 此 fixture；amounts.py、labels.py、receipt.py。保留唯讀輸入。
Materials / DoD: check.py 全部 assertions 通過；兩名原生 workers 互斥 ownership。
Authority: tasks.md
Coordinator: /root/remfix4_61_parallel
Workspace: /private/tmp/task-harness-remfix4-4pdrhfjg/sol61/parallel；初始三個模組為 stub。
Tools / limits: native agents、shell；無 network/install/external actions；僅兩名 workers，不再委派。

| ID | Outcome | Depends on | Owner | State |
| --- | --- | --- | --- | --- |
| T1 | subtotal cents*quantity sum，empty 0 | none | /root/remfix4_61_parallel/amounts_worker | done |
| T2 | label strip，blank Guest | none | /root/remfix4_61_parallel/labels_worker | done |
| T3 | receipt 整合且 check.py 通過 | T1,T2 | coordinator | done |

Acceptance: T1 與 T2 各以直接 assertions 驗證；T3 執行 check.py。證據存 evidence/。
Checkpoint: 尚未 dispatch；無外部副作用。

T1 attempt 1: native worker dispatched; ownership amounts.py; acceptance pending.

T2 attempt 1: native worker dispatched; ownership labels.py; acceptance pending.

T1 accepted: coordinator receipt a0cf1f exit 0 PASS T1; SHA256 34b24b52aaa6d058d4326a4dc2048716945c3794e92bf012074778ed22ff3bd9. Worker terminal; receipt b6f8d4 exit 0 matches.

T2 accepted: receipt 54f1a8 exit 0 PASS T2; SHA256 bf323853530fd47713761cb3c51f6b548f4dafa5ea8602b2a5f00d69bbf5fe1e. Worker terminal; receipt cdd40c matches.

T3 attempt 1: dependencies accepted; coordinator owns receipt.py integration.

T3 accepted: python3 -B check.py; receipt 1b51a8 exit 0 PASS receipt integration. Fingerprints and acceptance invocations: evidence/verification.md.
Checkpoint: T1,T2,T3 done；兩名 workers terminal；無 unresolved work 或 external side effects。
