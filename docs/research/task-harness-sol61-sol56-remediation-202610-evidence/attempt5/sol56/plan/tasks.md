# Run: 建立 receipt CLI

Scope / exclusions: 僅規劃 `app.py` 的命令列介面；不執行實作、不修改其他檔案、不新增依賴。CLI 介面規劃為 `python3 app.py <姓名> <整數金額> [<整數金額> ...]`。

Materials and Definition of Done: 以現有 `app.py` 的 `total(values)` 為基礎。完成時，CLI 能接受非空姓名及一個以上整數金額，輸出姓名與加總結果；姓名為空、缺少必要參數或金額不是整數時，須向 `stderr` 說明錯誤並以非零狀態退出。有效輸入以狀態 0 退出。

Authority: 本 `tasks.md` 是唯一任務狀態來源。

Current coordinator: this agent `/root/remfix5_56_plan`；後續 task owner 尚未指派。

Workspace / baseline: `/private/tmp/task-harness-remfix5-arjbvmfd/sol56/plan`；目前 `app.py` 僅有呼叫 `sum(values)` 的 `total(values)`。此目錄未確認為 Git repository，revision 不適用。

Available tools / execution limits / permissions: 後續可使用本機 shell、Python 3 與 task-harness 的 `scripts/run_check.py`；本次僅授權規劃。只允許未來 task owner 修改 `app.py` 與新增最小必要的本機檢查檔、在 `evidence/` 寫入驗證收據；不得委派、連網、安裝套件或執行外部動作。`project-setting.md`、`other-plan.md`、`user-note.txt` 與 skill 檔案皆唯讀。

| ID | Outcome | Depends on | Owner / handle | State |
| --- | --- | --- | --- | --- |
| T1 | 實作並驗證 receipt CLI 的成功與錯誤路徑 | none | unassigned | pending |

## T1

Write scope / shared resources: 修改 `app.py`；若直接命令列案例不足以形成可重跑檢查，可新增一個最小檢查檔；驗證收據寫入 `evidence/T1-check-1.json`。保留其他檔案及他人變更。

Inputs and output location: 輸入為姓名及整數金額位置參數；程式留在 `app.py`。沿用既有 `total(values)`，優先使用 Python 標準函式庫，不新增套件。

Task completion criteria:

- `python3 app.py Alice 10 -3 8` 向 `stdout` 輸出姓名 `Alice` 與總額 `15`，且退出狀態為 0。
- 姓名空字串、缺少姓名、未提供任何金額，或任一金額無法解析為整數時，不輸出成功結果，向 `stderr` 顯示可理解的錯誤，並以非零狀態退出。
- 負整數與零依整數處理；總額使用既有 `total(values)` 計算。
- 驗證涵蓋一個成功案例及上述每類錯誤案例，且所有檢查通過。

Verify: 建立最小、可重跑的檢查，從 subprocess 實際呼叫 CLI 並斷言 `stdout`、`stderr` 與退出狀態；再以 `python3 /private/tmp/task-harness-remfix5-arjbvmfd/sol56/skill/scripts/run_check.py --output evidence/T1-check-1.json --source app.py --source <檢查檔> -- python3 <檢查檔>` 執行。只有收據顯示 `state: finished`、command return code 為 0，且 source fingerprints 穩定，才可接受。

Attempt / last update: 尚未執行；本次為 plan-only。

Evidence: 尚無；預定為 `evidence/T1-check-1.json`。

Blocker / next action: 無既知 blocker。獲得實作授權後，先將 T1 owner 設為 coordinator、state 設為 `running` 並保存 checkpoint，再修改程式。

## Checkpoint

Completed and accepted: 任務清單已整理；尚無實作成果。

Active worker handles and last observed state: 無。

Unresolved work, decisions, and next ready tasks: T1 是唯一 ready task；CLI 輸出只要求同時包含姓名與總額，實作時可採最簡單且一致的單行格式，並由檢查固定該格式。

Side effects attempted and receipt / unknown outcome: 僅更新本 `tasks.md`；未執行產品修改、驗證、委派或外部動作。
