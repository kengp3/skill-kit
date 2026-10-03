# Run: receipt 整合
Objective: 兩名原生 workers 分別實作 subtotal 與 label，coordinator 整合 receipt。
Scope / exclusions: 僅 amounts.py、labels.py、receipt.py、tasks.md、evidence/；其餘唯讀。
Materials / Definition of Done: 現有 source、check.py；subtotal cents*quantity 與空清單 0、label strip 與 blank Guest，receipt 整合通過 check.py。
Authority: tasks.md；coordinator: /root/remfix_61_parallel。
Workspace / baseline: /private/tmp/task-harness-remfix-4199tvtt/sol61/parallel；三個函式起初皆 NotImplementedError。
Tools / limits: native collaboration、shell、Python；恰好兩名 helpers，同模型繼承、不得再委派；無 network/install/external actions。

| ID | Outcome | Depends on | Owner / handle | State |
| --- | --- | --- | --- | --- |
| T1 | subtotal cents*quantity、空清單 0 | none | /root/remfix_61_parallel/amounts | done |
| T2 | label strip、blank Guest | none | /root/remfix_61_parallel/labels | done |
| T3 | receipt 整合與 check.py | T1,T2 | coordinator | done |

## Acceptance / verification
T1: worker 執行 subtotal 兩個 assert；evidence/amounts.json 保存結果與 SHA256。
T2: worker 執行 label 兩個 assert；evidence/labels.json 保存結果與 SHA256。
T3: coordinator 執行 python3 check.py，保存 stdout、exit status 與檔案 SHA256。
Write scopes: T1 amounts.py、evidence/amounts.json；T2 labels.py、evidence/labels.json；coordinator receipt.py、tasks.md、其餘 evidence/。

## Checkpoint
Completed: T1、T2 assertions exit 0，current fingerprints 比對通過；證據 evidence/amounts.json、evidence/labels.json。
Completed: T3 python3 -B check.py exit 0，PASS receipt integration；evidence/integration.json。Next: none。兩 helpers 立即觀察時皆 completed；evidence/overlap.json 保留真實 relevant native states，未觀察到同時 running。
Side effects: local file writes only。

Final: T1、T2、T3 done；無未解工作。Helpers terminal completed，無 active handles。整合證據綁定所有 source 與 checker SHA256。
