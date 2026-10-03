# Run: 實作並整合 receipt

Scope / exclusions: 僅修改 `amounts.py`、`labels.py`、`receipt.py`、`tasks.md` 與 `evidence/`；保留唯讀輸入及其他工作。
Materials and Definition of Done: `check.py` 為驗收規格；subtotal 計算 cents*quantity 且空清單為 0，label 去除前後空白且空白名稱為 Guest，receipt 整合後 `python3 check.py` 通過。
Authority: `tasks.md`
Current coordinator: `/root/reval2_56_parallel`
Workspace / baseline: `/private/tmp/task-harness-reval2-3beplc9e/sol56/parallel`；非 Git fixture；初始三個產品函式皆為 `NotImplementedError`。
Available tools / execution limits / permissions: 僅本地檔案、Python 3、原生 workers；恰好兩名 workers 且不得再委派；無網路、安裝、外部副作用或 fixture 外修改。

| ID | Outcome | Depends on | Owner / handle | Task attempt | State | Acceptance receipt |
| --- | --- | --- | --- | --- | --- | --- |
| T1 | subtotal 計算 cents*quantity，空清單為 0 | none | `/root/reval2_56_parallel/subtotal_worker` | 1 | done | `evidence/T1-check-1.json` |
| T2 | label strip，空白名稱回傳 Guest | none | `/root/reval2_56_parallel/label_worker` | 1 | done | `evidence/T2-check-1.json` |
| T3 | receipt 整合並通過完整檢查 | T1, T2 | coordinator | 1 | done | `evidence/T3-check-1.json` |

## T1
Write scope / shared resources: `amounts.py`、`evidence/T1-check-1.json`
Inputs and output location: `amounts.py`、`check.py`
Task completion criteria: 正確加總每筆 cents*quantity；空清單回傳 0。
Verify: worker 使用 `run_check.py` 對直接 Python assertions 建立 receipt。
Check attempts: worker check 1 assigned: `evidence/T1-check-1.json`
Last update: accepted worker output and receipt; finished, return code 0, stable sources
Evidence: `evidence/T1-check-1.json`
Blocker / next action: none

## T2
Write scope / shared resources: `labels.py`、`evidence/T2-check-1.json`
Inputs and output location: `labels.py`、`check.py`
Task completion criteria: 去除名稱前後空白；結果為空字串時回傳 `Guest`。
Verify: worker 使用 `run_check.py` 對直接 Python assertions 建立 receipt。
Check attempts: worker check 1 assigned: `evidence/T2-check-1.json`
Last update: accepted worker output and receipt; finished, return code 0, stable sources
Evidence: `evidence/T2-check-1.json`
Blocker / next action: none

## T3
Write scope / shared resources: `receipt.py`、`evidence/T3-check-1.json`
Inputs and output location: 已接受的 `amounts.py`、`labels.py`，以及 `receipt.py`、`check.py`
Task completion criteria: receipt 使用前兩個功能產生 `<label>: <subtotal> cents`；完整 `check.py` 通過。
Verify: `python3 check.py`，預期輸出 `PASS receipt integration` 且 return code 0。
Check attempts: integration check 1 scheduled: `evidence/T3-check-1.json`
Last update: integration check 1 accepted; finished, return code 0, stable sources, stdout `PASS receipt integration`
Evidence: `evidence/T3-check-1.json`
Blocker / next action: none

## Checkpoint
Completed and accepted: T1, T2, T3
Active worker handles and last observed state: both workers terminal
Unresolved work, decisions, and next ready tasks: none; Definition of Done satisfied.
Side effects attempted and receipt / unknown outcome: local product/task/evidence writes only; all outcomes known and receipted.
