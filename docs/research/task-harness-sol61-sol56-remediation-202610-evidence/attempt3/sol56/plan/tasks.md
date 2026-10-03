# Run: 完成 receipt CLI

Scope / exclusions: 僅規劃在 `app.py` 補上可直接執行的 CLI；沿用既有 `total(values)`。不修改其他檔案、不新增相依套件、不執行實作或測試。
Materials and Definition of Done: 依 `app.py` 現況與本任務需求，CLI 以 `python app.py NAME AMOUNT [AMOUNT ...]` 接受一個非空姓名與至少一個整數金額，成功時輸出 `姓名: <NAME>` 與 `總額: <SUM>` 並以 0 結束；姓名為空、缺少參數或金額不是整數時，須輸出錯誤並以非 0 結束。實作完成且下列正反向案例皆通過才算完成。
Authority: 本檔為唯一 task state；coordinator: 後續執行者（目前未指派）。
Workspace / baseline: `/private/tmp/task-harness-remfix3-1nis2bc6/sol56/plan`；`app.py` 目前只有 `total(values)`，未提供 CLI；本工作區未顯示相關 Git 變更。
Available tools / execution limits / permissions: 可讀專案檔案並於後續獲授權時修改 `app.py`、執行本機 Python；本輪僅規劃。不得修改 `project-setting.md`、`other-plan.md`、`user-note.txt`，不得委派、連網、安裝套件或採取外部動作。

| ID | Outcome | Depends on | Owner / handle | State |
| --- | --- | --- | --- | --- |
| T1 | receipt CLI 可解析輸入、計算總額、輸出結果，且拒絕錯誤輸入 | none | unassigned | pending |

## T1

Write scope / shared resources: 只修改 `app.py`；保留並重用 `total(values)`，使用 Python 標準函式庫完成參數解析與退出碼處理。
Inputs and output location: 輸入為位置參數 `NAME AMOUNT [AMOUNT ...]`；程式仍位於 `app.py`，stdout 成功格式固定為兩行 `姓名: <NAME>`、`總額: <SUM>`。
Acceptance:

- `python app.py Alice 10 20 -5` 輸出 `姓名: Alice` 與 `總額: 25`，exit code 為 0。
- `python app.py '' 10` 必須失敗，exit code 非 0，且不得輸出成功收據。
- `python app.py Alice 10 nope` 必須失敗，exit code 非 0，且不得輸出成功收據。
- `python app.py Alice` 與 `python app.py` 必須失敗，exit code 非 0。
- 既有 `total([10, 20, -5]) == 25` 行為保持不變。

Verify: 依序執行上述五組 CLI 情境並記錄各自 stdout、stderr 與實際 exit code；另以最小 Python assertion 驗證既有 `total`。只有全部符合 Acceptance 才可標記 `done`。
Attempt / last update: 尚未實作；2026-10-02 已消除原草案的 A/B 循環依賴與 C 對不存在 X 的依賴，將小型端到端成果及其驗證合併為單一任務。
Evidence: 尚無；本輪為 plan-only，未執行實作或驗證。
Blocker / next action: 無規格阻礙；取得執行授權後，先將 T1 更新為 `running`，再修改 `app.py`。

## Checkpoint

Completed and accepted: 計畫已整理；尚無實作成果。
Active worker handles and last observed state: 無。
Unresolved work, decisions, and next ready tasks: T1 已 ready，待執行授權與 owner 指派。成功輸出格式及至少一筆金額的介面已在本計畫中固定。
Side effects attempted and receipt / unknown outcome: 僅更新本 `tasks.md`；未嘗試產品程式、測試、網路或外部 side effect。
