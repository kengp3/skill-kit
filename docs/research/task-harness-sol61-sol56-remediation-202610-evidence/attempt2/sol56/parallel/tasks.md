# Run: 完成 receipt 金額與標籤整合

Scope / exclusions: 僅修改 `amounts.py`、`labels.py`、`receipt.py`、本檔與 `evidence/`；保留 `other-plan.md`、`user-note.txt`，不修改 checker。
Materials and Definition of Done: `check.py` 全部 assertions 通過；保留兩名 worker 的驗證與協作證據。
Authority: 本檔；coordinator: `/root/remfix2_56_parallel`
Workspace / baseline: `/private/tmp/task-harness-remfix2-aok63ea9/sol56/parallel`；無 Git repository；三個來源函式起始皆為 `NotImplementedError`。
Available tools / execution limits / permissions: exactly two native helpers；無 network、installation 或 external actions；worker 不得再委派。

| ID | Outcome | Depends on | Owner / handle | State |
| --- | --- | --- | --- | --- |
| T1 | subtotal 計算 cents * quantity，空清單為 0 | none | `/root/remfix2_56_parallel/amounts_worker` | done |
| T2 | label 去除首尾空白，空白名稱回傳 Guest | none | `/root/remfix2_56_parallel/labels_worker` | done |
| T3 | receipt 整合 label 與 subtotal | T1, T2 | coordinator | done |
| T4 | 執行整合 checker 並保存證據 | T3 | coordinator | done |

## T1
Write scope / shared resources: `amounts.py`、`evidence/amounts-worker.txt`
Inputs and output location: `check.py`；上述檔案
Acceptance: `subtotal([(125,2),(50,3)]) == 400` 且 `subtotal([]) == 0`
Verify: worker 執行最小直接 assertions
Attempt / last update: attempt 1；已派給 `/root/remfix2_56_parallel/amounts_worker`，初始狀態 running
Evidence: `evidence/amounts-worker.txt`；assertions exit 0；`amounts.py` SHA-256 `34b24b52aaa6d058d4326a4dc2048716945c3794e92bf012074778ed22ff3bd9`，coordinator 已重算相符
Blocker / next action: none；accepted

## T2
Write scope / shared resources: `labels.py`、`evidence/labels-worker.txt`
Inputs and output location: `check.py`；上述檔案
Acceptance: `label("  Alice  ") == "Alice"` 且 `label(" ") == "Guest"`
Verify: worker 執行最小直接 assertions
Attempt / last update: attempt 1；已派給 `/root/remfix2_56_parallel/labels_worker`，初始狀態 running
Evidence: `evidence/labels-worker.txt`；assertions exit 0；`labels.py` SHA-256 `bf323853530fd47713761cb3c51f6b548f4dafa5ea8602b2a5f00d69bbf5fe1e`，coordinator 已重算相符
Blocker / next action: none；accepted

## T3
Write scope / shared resources: `receipt.py`
Inputs and output location: 已驗收的 `amounts.py`、`labels.py`
Acceptance: receipt 使用兩個共用函式產生 `<label>: <subtotal> cents`
Verify: `check.py`
Attempt / last update: coordinator attempt 1；T1、T2 已驗收，開始整合
Evidence: `receipt.py` SHA-256 `381c74b71cb5e233ca980493afa5a2acb7e9d9991cf0f484e69ee883f4768b6b`；整合 checker 覆蓋兩種 receipt 情境並通過
Blocker / next action: none；accepted

## T4
Write scope / shared resources: `evidence/check.txt`、本檔
Inputs and output location: 整合後來源
Acceptance: `python3 check.py` exit 0 並輸出 `PASS receipt integration`
Verify: `python3 check.py`
Attempt / last update: coordinator attempt 1；完成
Evidence: `evidence/check.txt`；`python3 check.py` exit 0，輸出 `PASS receipt integration`
Blocker / next action: none；accepted

## Checkpoint
Completed and accepted: T1、T2、T3、T4
Active worker handles and last observed state: none；兩名 worker 已完成
Unresolved work, decisions, and next ready tasks: none
Side effects attempted and receipt / unknown outcome: `git status` 顯示此目錄不是 Git repository；無外部副作用
