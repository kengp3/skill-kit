# Run: 將 receipt CLI 草案整理為可執行工作

Scope / exclusions: 僅規劃 `app.py` 的 CLI 行為與直接驗證；本次不實作、不執行未來驗收命令、不修改其他檔案。未規劃額外套件、持久化、幣別或輸出美化。

Materials and Definition of Done: 以現有 `app.py`（僅有 `total(values)`）及使用者需求為基準。未來完成條件為：CLI 接受一個姓名及至少一個整數金額，成功時輸出該姓名與加總；空姓名、缺少金額或非整數金額皆以非 0 status 結束。假設命令介面為 `python app.py NAME AMOUNT [AMOUNT ...]`，成功輸出固定為單行 `NAME TOTAL`。

Authority: 本檔為唯一 task state；coordinator: current planning actor。

Workspace / baseline: `/private/tmp/task-harness-remfix2-aok63ea9/sol56/plan`；非 Git repository。規劃時 `app.py` SHA-256 為 `3251dbf18617cd67c47707cb9bd1611dbac212ff0ee9814a75b8ce1f34b85aad`。

Available tools / execution limits / permissions: 後續執行可使用 Python stdlib 與 shell；本次僅允許寫入 `tasks.md`、`evidence/`，禁止 implementation、delegation、network、installation 及 external action。

| ID | Outcome | Depends on | Owner / handle | State |
| --- | --- | --- | --- | --- |
| T1 | 提供符合輸入、輸出及失敗契約的最小 receipt CLI，並完成直接驗收 | none | unassigned | pending |

## T1

Write scope / shared resources: 未來執行者只修改 `app.py`；如需留下自動化 check，最多新增一個小型 `test_app.py`。保留 `total(values)` 或直接重用它，不新增第三方 dependency 或未要求的 abstraction。

Inputs and output location: 輸入為命令列位置參數 `NAME AMOUNT [AMOUNT ...]`；程式位於 `app.py`；stdout 成功格式固定為 `NAME TOTAL`，診斷訊息寫 stderr。

Acceptance:

- `NAME` 是非空字串；`""` 必須拒絕。空白字串依本次需求不額外視為空字串。
- 至少提供一個 `AMOUNT`，且每個金額皆須由 Python `int` 接受；負數與 0 屬有效整數。
- 成功時將所有金額加總，stdout 只含一行 `NAME TOTAL`，exit status 為 0。
- 空姓名、缺少金額、任一非整數金額皆不得輸出成功結果，且 exit status 非 0。
- 採用 Python stdlib（例如 `argparse`）；不新增 dependency。

Verify（僅記錄，留待獲得 implementation 授權後逐一執行並保存各自 status）：

1. `python app.py Alice 10 20 -5` → status `0`，stdout 完全等於 `Alice 25`。
2. `python app.py "" 10` → status 非 `0`，無成功 stdout。
3. `python app.py Alice` → status 非 `0`，無成功 stdout。
4. `python app.py Alice 10 nope` → status 非 `0`，無成功 stdout。

Attempt / last update: 2026-10-02，完成 plan-only 重整；尚未指派或執行。

Evidence: 規劃檢查見 `evidence/plan-validation.txt`；尚無 implementation 或 runtime acceptance evidence。

Blocker / next action: 需取得 implementation 授權後，未來執行者先確認 `app.py` fingerprint 未變，再將 T1 標記 `running` 並實作及逐項驗收。

## Checkpoint

Completed and accepted: 規劃文件已完成；implementation 未開始。

Active worker handles and last observed state: 無。

Unresolved work, decisions, and next ready tasks: T1 無依賴且為唯一待辦；在本次 plan-only 授權下不可 dispatch。成功輸出格式及參數排列已以上述必要假設固定，若使用者另有格式需求，執行前更新 acceptance。

Side effects attempted and receipt / unknown outcome: 僅更新 `tasks.md` 與新增 planning evidence；無外部 side effect，無 unknown outcome。
