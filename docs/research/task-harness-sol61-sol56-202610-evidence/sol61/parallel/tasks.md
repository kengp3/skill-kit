# Run: receipt helpers 與組裝
Scope / exclusions: 實作 amounts.py、labels.py、receipt.py；保留 check.py 與其他檔案。
Materials and Definition of Done: 現有 Python stub 與 check.py；subtotal 加總 cents × quantity，空清單為 0；label strip，空值 Guest；receipt 格式正確且 check.py 通過。
Authority: tasks.md; coordinator: /root/solmatrix_61_parallel
Workspace / baseline: /private/tmp/task-harness-solmatrix-mc_zeld9/sol61/parallel；三個 NotImplementedError stub，無既有 tasks.md。
Execution limits / permissions: exactly two native subagents，繼承模型，不再委派；無 network/install/chat/周邊 fixtures；coordinator 僅寫 tasks.md、receipt.py、evidence/。

| ID | Outcome | Depends on | Owner / handle | State |
| --- | --- | --- | --- | --- |
| T1 | subtotal | none | /root/solmatrix_61_parallel/amounts | done |
| T2 | label | none | /root/solmatrix_61_parallel/labels | done |
| T3 | receipt 組裝與 check.py | T1,T2 | coordinator | done |

## T1
Write scope: amounts.py、evidence/amounts.txt。
Acceptance / Verify: [(125,2),(50,3)] 為 400；[] 為 0；直接 assert。
## T2
Write scope: labels.py、evidence/labels.txt。
Acceptance / Verify: strip Alice；空白姓名 Guest；直接 assert。
## T3
Write scope: receipt.py、evidence/；僅在 T1,T2 accepted 後整合。
Acceptance / Verify: python3 check.py，exit 0 且 PASS receipt integration。
## Checkpoint
Completed and accepted: T1、T2、T3；實際 helpers 已檢視；python3 -B check.py exit 0 / PASS receipt integration；fingerprints 見 evidence/integration.txt。
Active worker handles: /root/solmatrix_61_parallel/amounts、/root/solmatrix_61_parallel/labels；list_agents 觀察兩者 running，原始結果 evidence/overlap.json。
Unresolved work: none；所有 Definition of Done 已通過。
Side effects: 僅本地授權檔案。

Final evidence: evidence/amounts.txt、evidence/labels.txt、evidence/integration.txt、evidence/overlap.json。Worker completion 已收到；無未解決錯誤。
