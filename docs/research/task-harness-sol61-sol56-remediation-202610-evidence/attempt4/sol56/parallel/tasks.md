# Run: 完成收據計算與標籤整合

Scope / exclusions: 僅修改 `amounts.py`、`labels.py`、`receipt.py` 與本協調檔；保留唯讀檔案。
Materials and Definition of Done: `check.py` 所有 assertions 通過並輸出 `PASS receipt integration`。
Authority: 本檔
Current coordinator: `/root/remfix4_56_parallel`
Workspace / baseline: `/private/tmp/task-harness-remfix4-4pdrhfjg/sol56/parallel`；三個目標函式起始皆為 `NotImplementedError`。
Available tools / execution limits / permissions: 兩名原生 workers；無 network、install、external actions；workers 不再委派。

| ID | Outcome | Depends on | Owner / handle | State |
| --- | --- | --- | --- | --- |
| T1 | `subtotal` 計算 cents * quantity 總和，空清單為 0 | none | `/root/remfix4_56_parallel/amounts_worker` | done |
| T2 | `label` 去除前後空白，空白名稱為 Guest | none | `/root/remfix4_56_parallel/labels_worker` | done |
| T3 | `receipt` 整合 T1、T2 並通過 `check.py` | T1, T2 | coordinator | done |

## T1
Write scope / shared resources: 僅 `amounts.py`。
Inputs and output location: `check.py`；輸出原檔。
Acceptance: 指定一般案例與空清單結果正確。
Verify: worker 的直接函式 assertions；整合時執行 `python3 check.py`。
Attempt / last update: worker 完成；coordinator 已重跑直接檢查並確認檔案未變。
Evidence: `python3 -c 'from amounts import subtotal; ...'` exit 0，輸出 `PASS subtotal direct checks`；SHA-1 `5bbd7564b5dc011bef6a30555b00155703ed445d`。
Blocker / next action: 無。

## T2
Write scope / shared resources: 僅 `labels.py`。
Inputs and output location: `check.py`；輸出原檔。
Acceptance: strip 後回傳名稱；blank 回傳 `Guest`。
Verify: worker 的直接函式 assertions；整合時執行 `python3 check.py`。
Attempt / last update: worker 完成；coordinator 已重跑直接檢查並確認檔案未變。
Evidence: `python3 -c 'from labels import label; ...'` exit 0，輸出 `PASS label direct checks`；SHA-1 `92a85d6255b9c0f558702819e8dcccce3f139ccc`。
Blocker / next action: 無。

## T3
Write scope / shared resources: 僅 `receipt.py`；coordinator 整合。
Inputs and output location: T1、T2 函式及 `check.py`。
Acceptance: 格式為 `<label>: <subtotal> cents`，完整 checker 通過。
Verify: `python3 check.py`，預期 exit 0 與 `PASS receipt integration`。
Attempt / last update: coordinator 完成最小整合並驗收。
Evidence: `python3 check.py` exit 0，輸出 `PASS receipt integration`；`receipt.py` SHA-1 `ab0782360ed2aff17d7d46df86b9d6c2bc1a4c33`。
Blocker / next action: 無。

## Checkpoint
Completed and accepted: T1、T2、T3。
Active worker handles and last observed state: 兩名 workers terminal。
Unresolved work, decisions, and next ready tasks: 無。
Side effects attempted and receipt / unknown outcome: 已修改三個授權實作檔並建立 `tasks.md`；無未知結果。
