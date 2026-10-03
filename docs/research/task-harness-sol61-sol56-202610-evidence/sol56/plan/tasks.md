# Run: 將 receipt CLI 草案整理為可執行工作

Scope / exclusions: 規劃一個 CLI，接收非空姓名與一個以上的整數金額，輸出姓名與加總金額；無效輸入須以非零狀態退出。本次只規劃，不修改 `app.py`、不執行實作或測試。

Materials and Definition of Done: 以現有 `app.py` 的 `total(values)` 為基礎；任務須涵蓋參數解析、輸出、輸入驗證及可直接執行的驗收方式，且依賴關係完整、無循環。完成本文件不代表 CLI 已實作。

Authority: `tasks.md`；coordinator: unassigned

Workspace / baseline: `/private/tmp/task-harness-solmatrix-mc_zeld9/sol56/plan`；非 Git fixture。規劃時 `app.py` SHA-256 為 `3251dbf18617cd67c47707cb9bd1611dbac212ff0ee9814a75b8ce1f34b85aad`。

Execution limits / permissions: plan-only；不得實作、委派、連網、安裝套件或修改 `tasks.md` 與 `evidence/` 以外的檔案。

| ID | Outcome | Depends on | Owner / handle | State |
| --- | --- | --- | --- | --- |
| T1 | receipt CLI 可正確處理有效輸入，並拒絕空姓名、缺少金額與非整數金額 | none | unassigned | pending |

## T1

Write scope / shared resources: `app.py` 與最小必要的測試檔；沿用既有 `total(values)`，不新增相依套件或非必要抽象。

Inputs and output location:

- CLI 介面：`python app.py <name> <amount> [<amount> ...]`
- `name` 去除前後空白後不得為空字串。
- `amount` 至少一筆，且每筆須為整數；負數與 0 未被需求排除，依整數接受。
- 成功時輸出單行 `<name>: <total>` 至 stdout，並以狀態 0 退出。
- 無效輸入的說明輸出至 stderr，並以非零狀態退出；具體錯誤文字可沿用參數解析器的預設訊息。

Acceptance:

1. `python app.py Alice 10 20 -5` 輸出 `Alice: 25`，exit code 為 0。
2. `python app.py 'Alice Chen' 10 20` 輸出 `Alice Chen: 30`，exit code 為 0。
3. 空字串或只有空白的姓名皆失敗，stderr 有錯誤訊息，exit code 非 0。
4. 缺少金額時失敗，stderr 有錯誤訊息，exit code 非 0。
5. 任一金額不是整數時失敗，stderr 有錯誤訊息，exit code 非 0。
6. 既有 `total(values)` 的整數加總行為仍成立。

Verify: 實作時以 subprocess 或 shell 逐一執行上述五類 CLI 情境並檢查 stdout、stderr 與 exit code；另以現有測試方式或最小 assert 檢查 `total([10, 20, -5]) == 25`。本次 plan-only 未執行這些驗證。

Attempt / last update: 2026-10-02，已將原草案中 A/B 循環依賴及 C 的缺失依賴 X 重整為單一端到端任務；未開始實作。

Evidence: `evidence/plan-review.md`

Blocker / next action: 無規劃阻礙；取得實作授權後，由執行者承接 T1，完成變更與驗證後才能更新為 `done`。

## Checkpoint

Completed and accepted: 規劃文件已整理；實作任務尚未完成。

Active worker handles and last observed state: none。

Unresolved work, decisions, and next ready tasks: T1 已 ready，維持 `pending`；CLI 輸出格式與空白姓名處理已在本計畫固定。

Side effects attempted and receipt / unknown outcome: 僅改寫 `tasks.md` 並新增規劃 evidence；沒有外部副作用或未知結果。
