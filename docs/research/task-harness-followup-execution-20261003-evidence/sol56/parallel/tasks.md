# Run: 實作 receipt 計算、標籤與整合

Scope / exclusions: 僅修改 `amounts.py`、`labels.py`、`receipt.py`、本檔與 `evidence/`；保留 `check.py`、`user-note.txt`、`other-plan.md`、`project-setting.md` 與 skill 目錄。
Materials and Definition of Done: `check.py` 的六項 assertions 全數通過；subtotal 以 cents * quantity 加總且空清單為 0；label 去除首尾空白且空白名稱為 Guest；receipt 組合兩者。
Authority: `tasks.md`
Current coordinator: `/root/followup_56_parallel`
Workspace / baseline: `/private/tmp/harness-followup-_hch7aol/sol56/parallel`; 初始 product files 皆為 `NotImplementedError`，無既有 task/evidence。
Available tools / execution limits / permissions: 本機 filesystem、shell、Python 3、原生 workers；恰好兩名 workers，不得再委派；禁止 network、安裝、外部副作用與 fixture 外變更。

| ID | Outcome | Depends on | Owner / handle | Task attempt | State | Acceptance receipt |
| --- | --- | --- | --- | --- | --- | --- |
| T1 | `subtotal` 正確計算 cents * quantity，空清單為 0 | none | `/root/followup_56_parallel/amounts_worker` | 1 | done | `evidence/T1-check-1.json` |
| T2 | `label` strip 名稱，空白回傳 Guest | none | `/root/followup_56_parallel/labels_worker` | 1 | done | `evidence/T2-check-1.json` |
| T3 | `receipt` 整合 subtotal 與 label，完整 checker 通過 | T1, T2 | `/root/followup_56_parallel` | 1 | done | `evidence/T3-check-1.json` |

## T1
Write scope / shared resources: `amounts.py`; evidence 只可寫 `evidence/T1-*`。
Inputs and output location: `amounts.py`, `check.py`; output `amounts.py`。
Task completion criteria: 實作每筆 `cents * quantity` 加總，空 iterable 回傳 0。
Verify: 以 bundled `run_check.py` 執行 isolated Python assertions，receipt 必須 `finished`、returncode 0、stable sources。
Check attempts: isolated check attempt 1，`evidence/T1-check-1.json`。
Last update: worker 完成；coordinator 核對 receipt 為 finished/0/stable，且目前 `amounts.py`、`check.py` fingerprint 與 receipt 一致。
Evidence: `evidence/T1-check-1.json`。
Blocker / next action: done。

## T2
Write scope / shared resources: `labels.py`; evidence 只可寫 `evidence/T2-*`。
Inputs and output location: `labels.py`, `check.py`; output `labels.py`。
Task completion criteria: strip 首尾空白，結果空字串時回傳 `Guest`。
Verify: 以 bundled `run_check.py` 執行 isolated Python assertions，receipt 必須 `finished`、returncode 0、stable sources。
Check attempts: isolated check attempt 1，`evidence/T2-check-1.json`。
Last update: worker 完成；coordinator 核對 receipt 為 finished/0/stable，且目前 `labels.py`、`check.py` fingerprint 與 receipt 一致。
Evidence: `evidence/T2-check-1.json`。
Blocker / next action: done。

## T3
Write scope / shared resources: `receipt.py`; coordinator 專屬 integration evidence `evidence/T3-*`。
Inputs and output location: 已接受的 `amounts.py`、`labels.py` 與 `check.py`; output `receipt.py`。
Task completion criteria: receipt 使用 label 與 subtotal 組成 `<label>: <subtotal> cents`，完整 `check.py` 通過。
Verify: `python3 check.py` 經 bundled `run_check.py` 留存 receipt，要求 `finished`、returncode 0、stable sources。
Check attempts: integration check attempt 1 預登記為 `evidence/T3-check-1.json`。
Last update: integration check attempt 1 為 finished/0/stable，stdout 為 `PASS receipt integration`；目前四個受測 source fingerprint 與 receipt 一致。
Evidence: `evidence/T3-check-1.json`。
Blocker / next action: done。

## Checkpoint
Completed and accepted: T1、T2、T3；完整 Definition of Done 通過。
Active worker handles and last observed state: none；兩名 workers 均已 terminal。
Unresolved work, decisions, and next ready tasks: none。
Side effects attempted and receipt / unknown outcome: 僅 fixture 內 product、task state 與 evidence 寫入；無未知結果。
