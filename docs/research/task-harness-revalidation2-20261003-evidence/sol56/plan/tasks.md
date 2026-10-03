# Run: 將 receipt CLI 草案整理為可執行工作清單

## Objective

規劃一個 CLI：接受一個非空姓名與一筆以上整數金額，成功時輸出姓名與金額總和；姓名為空、缺少參數或任一金額不是整數時，必須以非零狀態退出。

## Background

- 現有 `app.py` 只有 `total(values)`，以 `sum(values)` 計算總額，尚無 CLI 入口或輸入驗證。
- 舊草案 A 與 B 互相依賴，C 又依賴不存在的 X，無法開始執行。
- 此功能規模小且實作、格式與驗收屬於同一端到端成果，因此合併成單一工作，移除循環及遺失依賴。

## Materials

- `app.py`：既有 `total(values)` 草案；未修改。
- `project-setting.md`：指定本檔為唯一 task state，規劃證據放在 `evidence/`。
- `user-note.txt`、`other-plan.md`：既有使用者工作，只讀且不納入本計畫。

## Boundaries

- 本輪只更新規劃，不實作、不執行驗收案例、不建立外部 issue 或其他持久狀態。
- 未來實作限於 receipt CLI 所需的最小程式與測試；不得修改 `user-note.txt`、`other-plan.md` 或 `project-setting.md`。
- `tasks.md` 是唯一 task state；current coordinator 為本 agent，未來 task owner 尚未指派。

## Assumptions

- CLI 介面規劃為位置參數：`python3 app.py NAME AMOUNT [AMOUNT ...]`。
- 成功輸出採單行 `NAME TOTAL`（中間一個空白、結尾換行），例如 `python3 app.py Alice 10 -3 5` 輸出 `Alice 12`。
- 金額接受 Python 可解析的十進位正負整數與 `0`；空清單不合法。
- 無效輸入的錯誤文字可由參數解析器決定；驗收只要求 stderr 有診斷、stdout 不產生成功收據、退出碼非零。
- 已確認目錄不是 Git repository，因此 baseline 以實際檔案內容為準，沒有 revision 可記錄。

## Definition of Done

- CLI 符合上述介面與輸出契約，並保留或等價使用既有加總行為。
- 正常、負數與零金額案例輸出正確。
- 空姓名、缺少姓名、缺少金額及非整數金額皆失敗退出。
- 直接驗收涵蓋成功與錯誤路徑，且結果由 task-harness `run_check.py` 留存可追溯 receipt；完成前檢查 current artifact 與 receipt 的 source fingerprints 一致。

## Authority and execution limits

- Authority: `tasks.md`（本檔）。
- Workspace / baseline: 本目錄為已確認 project root；`app.py` 目前僅含 `total(values)`；非 Git repository。
- Available tools: 本機 shell、Python 3（執行前仍須確認可用）、task-harness `scripts/run_check.py`。
- Permissions: 此次僅允許規劃；不得開始 T1、修改產品程式、安裝套件、使用網路、委派或造成外部 side effect。

| ID | Outcome | Depends on | Owner / handle | Task attempt | State | Acceptance receipt |
| --- | --- | --- | --- | --- | --- | --- |
| T1 | 完成 receipt CLI 的參數解析、驗證、輸出與端到端驗收 | none | unassigned | not started | pending | none |

## T1

Write scope / shared resources:
- 在未來取得實作授權後，修改 `app.py` 並新增最小必要的自動驗收檔；由單一 owner 同時負責，避免產品碼與測試契約分離。
- 不修改 `tasks.md` 以外的既有文件；receipt 由 coordinator 寫入 `evidence/T1-check-1.json`。

Inputs and output location:
- Input: `app.py` 的既有 `total(values)` 與本檔定義的 CLI 契約。
- Output: 可直接以 `python3 app.py NAME AMOUNT [AMOUNT ...]` 執行的 CLI，以及最小驗收腳本。

Task completion criteria:
- 一筆以上合法整數被解析後交由加總邏輯處理，stdout 僅輸出 `<姓名> <總額>` 與換行，退出碼為 0。
- 姓名去除前後空白後不得為空；空白姓名、缺少必要參數或非整數金額須在計算前拒絕，於 stderr 提供診斷並以非零狀態退出。
- 不加入與 receipt CLI 無關的 refactor、dependency 或功能。

Implementation checklist:
- [ ] 加入 CLI 入口及位置參數解析，要求一個姓名與一筆以上金額。
- [ ] 將每筆金額限制為整數，並拒絕空白姓名。
- [ ] 呼叫既有或等價的 `total(values)` 計算總額，依契約輸出單行結果。
- [ ] 建立最小端到端驗收，涵蓋：單筆、多筆、負數與零；空白姓名、缺少姓名、缺少金額、非整數金額。
- [ ] 使用 task-harness runner 留存驗收 receipt，讀回 JSON 並確認 `state: finished`、return code 成功及 source fingerprints 穩定。

Verify:
- 未來先建立一個自動驗收腳本，以 subprocess 逐案檢查 stdout、stderr 與退出碼；所有案例通過時腳本本身退出 0。
- 在執行 check 前先於本檔記錄 check attempt 與 receipt path，再單獨執行：`python3 ../skill/scripts/run_check.py --output evidence/T1-check-1.json --source app.py --source <驗收腳本> -- python3 <驗收腳本>`。
- 預期 receipt 為 `finished`、內層 command return code 為 0，且 `app.py` 與驗收腳本 fingerprints 在檢查期間未變。

Check attempts: none（plan-only，尚未執行）

Last update: 2026-10-03；已將不可執行的 A/B/C 草案合併為無依賴循環的 T1，尚未開始實作。

Evidence: none（plan-only）

Blocker / next action: 需要後續明確實作授權；取得授權後，先指派 T1 owner、記錄 attempt 1 與 `running`，再修改產品檔案。

## Checkpoint

Completed and accepted: 規劃文件已整理；產品成果尚無完成項目。

Active worker handles and last observed state: none；未委派、未執行。

Unresolved work, decisions, and next ready tasks: T1 沒有依賴且在取得實作授權後可開始；姓名是否保留首尾空白已依「不可為空」採取最小假設：驗證時 trim、輸出也使用 trim 後姓名。

Side effects attempted and receipt / unknown outcome: 僅更新 `tasks.md`；沒有外部 side effect，沒有未知結果。
