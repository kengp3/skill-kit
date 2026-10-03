# Run: 將 receipt CLI 草案整理成可執行工作清單

Scope / exclusions: 規劃一個 CLI：接受非空姓名與至少一筆整數金額，輸出姓名與加總金額；無效輸入須以非零狀態退出。只規劃，不實作、不執行產品驗證、不修改 `app.py`、`other-plan.md` 或 `user-note.txt`。

Materials and Definition of Done: 以現有 `app.py` 的 `total(values)` 與原 `tasks.md` 草案為基線。完成條件是本清單沒有缺少的依賴、自我依賴或循環，且每個需求都有可直接執行的驗收命令與預期結果。

Authority: `tasks.md`；coordinator: current planning agent。

Workspace / baseline: `/private/tmp/task-harness-remfix-4199tvtt/sol56/plan`；非 Git workspace；現有 `app.py` 僅定義 `total(values) = sum(values)`。

Available tools / execution limits / permissions: 未來執行可使用 Python 3、shell 與現有專案檔案；本次僅可寫入 `tasks.md` 與 `evidence/`，不得實作、委派、連網、安裝套件或進行外部操作。

Assumptions: 金額清單至少一筆；正整數、零與負整數都屬有效整數。成功輸出契約採單行 `<姓名> <總額>` 並以換行結尾，避免額外格式需求。

| ID | Outcome | Depends on | Owner / handle | State |
| --- | --- | --- | --- | --- |
| T1 | CLI 完整處理參數、驗證、加總與輸出 | none | unassigned | pending |
| T2 | 以成功與失敗案例驗收 CLI | T1 | unassigned | pending |

## T1

Write scope / shared resources: 僅修改 `app.py`；沿用既有 `total(values)`，使用 Python 標準函式庫完成最小 CLI 入口與輸入驗證。

Inputs and output location: 輸入為第一個位置參數 `name` 與後續一筆以上的 `amount`；輸出至 stdout，錯誤訊息至 stderr。

Acceptance:

- `name` 缺少或為空字串時失敗，程序以非零狀態退出。
- 缺少金額、任一金額不是十進位整數時失敗，程序以非零狀態退出。
- 有效輸入將全部金額交由既有 `total(values)` 加總。
- 成功時 stdout 僅包含 `<姓名> <總額>` 與結尾換行，退出狀態為 0。
- 不新增相依套件、抽象層或未要求的 receipt 欄位。

Verify: 完成實作後執行 T2 所列命令；全部結果符合預期才可接受。

Attempt / last update: 尚未開始；2026-10-02 完成規劃。

Evidence: 尚無實作證據；規劃證據見 `evidence/plan-review.md`。

Blocker / next action: 無；T1 為下一個 ready task。

## T2

Write scope / shared resources: 原則上不修改產品檔案；若驗收揭露缺陷，退回 T1 修正後再重新執行全部案例。

Inputs and output location: T1 完成後的 `app.py`；驗收結果記錄於 `evidence/`。

Acceptance:

- 一般案例：`python3 app.py 王小明 100 250 -50` 的 stdout 恰為 `王小明 300`，exit 0。
- 單筆與零值：`python3 app.py Amy 0` 的 stdout 恰為 `Amy 0`，exit 0。
- 空姓名：`python3 app.py '' 100` 無成功輸出，exit 非 0。
- 缺少姓名與金額：`python3 app.py` 無成功輸出，exit 非 0。
- 缺少金額：`python3 app.py Amy` 無成功輸出，exit 非 0。
- 非整數金額：`python3 app.py Amy 10 2.5` 無成功輸出，exit 非 0。

Verify: 分別執行上述六個 CLI 案例並逐一記錄 stdout、stderr 與各自 exit status；不得以批次最後一個狀態代替個別結果。另執行 `python3 -m py_compile app.py`，預期 exit 0。

Attempt / last update: 尚未開始；等待 T1。

Evidence: 尚無；未來應記錄測試命令、個別 exit status、輸出，以及驗收時 `app.py` 的 SHA-256。

Blocker / next action: 等待 T1 完成並留下可驗收 artifact。

## Checkpoint

Completed and accepted: 規劃完成；未完成任何實作或產品驗收。

Active worker handles and last observed state: 無；本次不允許委派。

Unresolved work, decisions, and next ready tasks: T1 ready；T2 等待 T1。若產品需求不允許負金額，開始實作前需先修訂 T1 的整數範圍與案例。

Side effects attempted and receipt / unknown outcome: 僅更新 `tasks.md` 並建立規劃證據；無外部 side effect。
