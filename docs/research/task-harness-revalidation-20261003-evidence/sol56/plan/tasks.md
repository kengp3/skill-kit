# Run: 將 receipt CLI 草案整理為可執行工作清單

Objective：完成一個 Python CLI，接受非空姓名與至少一筆整數金額，輸出姓名與加總結果；不合法輸入以非零狀態退出。

Scope / exclusions：僅規劃 `app.py` 的最小修改與驗證；本次不實作、不執行驗證、不建立 evidence、不修改 `project-setting.md`、`other-plan.md` 或 `user-note.txt`，也不新增依賴或檔案。

Materials and Definition of Done：以現有 `app.py` 的 `total(values)` 為基礎。實作階段完成後，`python3 app.py NAME AMOUNT [AMOUNT ...]` 可正確輸出姓名與總額；空姓名、缺少金額、非整數金額皆以非零狀態退出，且成功路徑以零狀態退出。所有列出的驗證情境通過才算完成。

Assumptions：CLI 採位置參數；姓名保留使用者輸入，但空字串視為錯誤；金額允許負整數與 `0`；成功輸出固定為兩行 `姓名: <NAME>` 與 `總額: <SUM>`。若產品契約另有指定，實作前先更新此假設與驗收預期。

Authority：本檔 `tasks.md` 是唯一 task state。

Current coordinator：this agent `/root/reval03_56_plan`；後續 task owner 尚未指派。

Workspace / baseline：`/private/tmp/task-harness-reval03-rmiru6z0/sol56/plan`；此目錄不是 Git repository。基準 `app.py` 僅含 `total(values): return sum(values)`；原草案 A/B 形成循環依賴，C 依賴不存在的 X，已合併為一個端到端任務並移除無效依賴。

Available tools / execution limits / permissions：後續可使用本機檔案工具、Python 3，以及 task-harness 的 `scripts/run_check.py`；僅可寫入 `app.py` 與 `evidence/` 時須另有 execute 授權。本次為 plan-only；禁止 delegation、network、install 與 external actions。

| ID | Outcome | Depends on | Owner / handle | State |
| --- | --- | --- | --- | --- |
| T1 | 實作並驗證 receipt CLI 的成功與錯誤輸入契約 | none | unassigned | pending |

## T1

Write scope / shared resources：實作時只修改 `app.py`；驗證 receipt 寫入 `evidence/T1-*.json`。保留其他所有檔案與他人變更。

Inputs and output location：輸入為現有 `app.py` 與上述 CLI 契約；產出為更新後的 `app.py` 及各驗證情境的 JSON receipt。

Task completion criteria：

- 沿用 `total(values)`，以 Python 標準函式庫提供 CLI 參數解析，不新增 dependency 或抽象層。
- 接受一個非空姓名與至少一筆整數金額；成功時 stdout 精確輸出 `姓名: <NAME>`、`總額: <SUM>` 兩行並以狀態 0 結束。
- 空姓名、缺少金額或任一非整數金額時不得輸出成功結果，並以非零狀態結束。
- 下列直接驗證全部完成，receipt 顯示 `state: finished`、符合預期 return code，且來源 fingerprint 穩定。

Verify：實作階段使用 task-harness `scripts/run_check.py`，每個情境各存一份 receipt，不以 pipeline 或批次包裝多個檢查：

1. `python3 app.py Alice 10 20 -5`：預期 stdout 為 `姓名: Alice`、`總額: 25`，return code 0。
2. `python3 app.py Bob 0`：預期 stdout 為 `姓名: Bob`、`總額: 0`，return code 0。
3. `python3 app.py '' 10`：預期 return code 非 0，且無成功結果。
4. `python3 app.py Alice`：預期 return code 非 0，且無成功結果。
5. `python3 app.py Alice 10 nope`：預期 return code 非 0，且無成功結果。

Attempt / last update：尚未開始；本次僅完成規劃。

Evidence：尚無；執行時為五個情境分別建立 `evidence/T1-check-1.json` 至 `evidence/T1-check-5.json`，每次以 `--source app.py` 綁定被測版本。

Blocker / next action：需要新的 execute 授權後，將 T1 指派給 coordinator 或單一 worker；先把狀態與 owner 寫為 `running`，再修改 `app.py`。

## Checkpoint

Completed and accepted：計畫已整理；尚無 implementation task 完成。

Active worker handles and last observed state：無。

Unresolved work, decisions, and next ready tasks：T1 無依賴且材料齊全，但因 plan-only 授權尚未 dispatch；成功輸出格式目前依 Assumptions 固定。

Side effects attempted and receipt / unknown outcome：僅更新 `tasks.md`；未嘗試產品修改、驗證或外部 side effect。
