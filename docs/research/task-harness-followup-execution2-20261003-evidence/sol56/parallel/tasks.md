# Run: 實作並整合 receipt

Scope / exclusions: 僅修改 `amounts.py`、`labels.py`、`receipt.py`、本檔與 `evidence/`；保留所有 protected inputs 與其他工作。
Materials and Definition of Done: `check.py` 為整合規格；subtotal 計算 cents * quantity 且空清單為 0，label 去除首尾空白且空白名稱為 Guest，receipt 組合為 `<label>: <subtotal> cents`；最終 `python3 check.py` 通過並留存 receipt。
Authority: `tasks.md`
Current coordinator: `/root/followup2_56_parallel`
Workspace / baseline: `/private/tmp/harness-followup2-465i825d/sol56/parallel`; 初始 product files 均為 `NotImplementedError`；非 Git fixture。
Available tools / execution limits / permissions: exactly two native workers；workers 不得再委派；無 network、install、external side effects；只可寫本 fixture 的 product outputs、`tasks.md` 與 `evidence/`。

| ID | Outcome | Depends on | Owner / handle | Task attempt | State | Acceptance receipt |
| --- | --- | --- | --- | --- | --- | --- |
| T1 | subtotal 支援 cents * quantity 與空清單 0 | none | `/root/followup2_56_parallel/subtotal_worker` | 1 | done | `evidence/T1-check-1.json` |
| T2 | label strip 且空白名稱回傳 Guest | none | `/root/followup2_56_parallel/label_worker` | 1 | done | `evidence/T2-check-1.json` |
| T3 | coordinator 整合 receipt 並通過完整檢查 | T1, T2 | coordinator | 1 | done | `evidence/T3-check-1.json` |

## T1
Write scope / shared resources: `amounts.py`, `evidence/T1-*`。
Inputs and output location: `amounts.py`, `check.py`（唯讀規格）。
Task completion criteria: `subtotal([(125,2),(50,3)]) == 400` 且 `subtotal([]) == 0`。
Verify: 以 task-harness `run_check.py` 執行只涵蓋 T1 的 Python assertion。
Check attempts: T1-check attempt 1, `evidence/T1-check-1.json`。
Last update: coordinator inspected `amounts.py` and accepted worker receipt for the current stable sources。
Evidence: `evidence/T1-check-1.json`。
Blocker / next action: none；done。

## T2
Write scope / shared resources: `labels.py`, `evidence/T2-*`。
Inputs and output location: `labels.py`, `check.py`（唯讀規格）。
Task completion criteria: `label("  Alice  ") == "Alice"` 且 `label(" ") == "Guest"`。
Verify: 以 task-harness `run_check.py` 執行只涵蓋 T2 的 Python assertion。
Check attempts: T2-check attempt 1, `evidence/T2-check-1.json`。
Last update: coordinator inspected `labels.py` and accepted worker receipt for the current stable sources。
Evidence: `evidence/T2-check-1.json`。
Blocker / next action: none；done。

## T3
Write scope / shared resources: `receipt.py`, `evidence/T3-*`, `tasks.md`。
Inputs and output location: accepted T1/T2 outputs 與 `check.py`。
Task completion criteria: receipt 正確組合 label 與 subtotal；完整 `check.py` 通過。
Verify: `python3 check.py`，預期輸出 `PASS receipt integration` 且 return code 0。
Check attempts: T3-integration attempt 1, `evidence/T3-check-1.json`。
Last update: coordinator inspected the receipt；state `finished`, return code 0, stdout `PASS receipt integration`, all four sources stable。
Evidence: `evidence/T3-check-1.json`。
Blocker / next action: none；done。

## Checkpoint
Completed and accepted: T1 via `evidence/T1-check-1.json`；T2 via `evidence/T2-check-1.json`；T3 via `evidence/T3-check-1.json`。
Active worker handles and last observed state: both worker handles terminal；no active workers。
Unresolved work, decisions, and next ready tasks: none；Definition of Done satisfied。
Side effects attempted and receipt / unknown outcome: none。
