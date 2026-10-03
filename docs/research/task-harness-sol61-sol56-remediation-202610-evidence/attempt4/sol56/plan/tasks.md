# Run: 完成 receipt CLI

Scope / exclusions: 僅規劃 `app.py` 的命令列介面；不執行實作、不新增依賴、不修改其他檔案。
Materials and Definition of Done: 以現有 `app.py` 的 `total(values)` 為基礎，CLI 接受一個姓名與一個以上整數金額，成功時輸出 `<姓名>: <總額>` 並以 0 結束；缺少姓名、姓名為空字串、缺少金額或金額不是整數時，須輸出錯誤並以非 0 結束。T1 的全部驗收情境通過即完成。
Authority: 本檔案 `/private/tmp/task-harness-remfix4-4pdrhfjg/sol56/plan/tasks.md`
Current coordinator: this agent `/root/remfix4_56_plan`; task owner 尚未指派。
Workspace / baseline: `/private/tmp/task-harness-remfix4-4pdrhfjg/sol56/plan`（非 Git repository）；規劃時 `app.py` SHA-256 為 `3251dbf18617cd67c47707cb9bd1611dbac212ff0ee9814a75b8ce1f34b85aad`，內容僅有既存 `total(values)`。
Available tools / execution limits / permissions: 後續實作者可使用本機 shell 與 Python；只允許修改 `app.py`，不得安裝套件、使用網路、委派、執行外部動作，並須保留 `project-setting.md`、`other-plan.md`、`user-note.txt` 與其他人的變更。本次為 plan-only，停止於清單完成。

| ID | Outcome | Depends on | Owner / handle | State |
| --- | --- | --- | --- | --- |
| T1 | 實作並驗證 receipt CLI 的成功與錯誤輸入行為 | none | unassigned | pending |

## T1

Write scope / shared resources: 僅 `app.py`；沿用既有 `total(values)`，優先使用 Python 標準函式庫，無共享服務或外部資源。

Inputs and output location: 輸入介面規劃為 `python app.py NAME AMOUNT [AMOUNT ...]`；輸出仍在標準輸出／標準錯誤，程式碼留在 `app.py`。

Acceptance:

- `python app.py Alice 10 20 -5` 在標準輸出精確產生 `Alice: 25`，且 exit code 為 0。
- `python app.py "" 10` 以非 0 結束並顯示錯誤，不產生成功結果。
- 缺少姓名、缺少金額或任一金額不是整數時，皆以非 0 結束並顯示錯誤。
- 直接呼叫既有 `total([10, 20, -5])` 仍回傳 `25`。
- 除 `app.py` 外沒有檔案異動，且未加入第三方 dependency。

Verify: 實作後執行下列獨立檢查並記錄各自的實際 exit code 與輸出：

```sh
python app.py Alice 10 20 -5
python app.py "" 10
python app.py Alice
python app.py Alice 10 nope
python -c 'from app import total; assert total([10, 20, -5]) == 25'
```

另比較實作前後檔案清單或可用的 workspace diff，確認只有 `app.py` 被修改。

Attempt / last update: 尚未開始；原草案 A 與 B 的循環工作以及 C 的重複驗證已合併為 T1，無效依賴 X 已移除。姓名採命令列單一 positional argument；「金額清單」暫定至少一筆，避免無金額時產生看似有效的零元結果。

Evidence: 尚無實作或驗證證據；本次僅完成規劃。規劃基線見上方 `app.py` fingerprint。

Blocker / next action: 無；T1 已 ready。後續取得執行授權後，先將 owner 設為實作者並把狀態改為 `running`，再修改 `app.py`。

## Checkpoint

Completed and accepted: 任務分解與驗收規格已完成；產品實作尚未開始。

Active worker handles and last observed state: 無。

Unresolved work, decisions, and next ready tasks: T1 為唯一 ready task；若使用者要求不同輸出格式或允許空金額清單，須在實作前修訂 Acceptance。

Side effects attempted and receipt / unknown outcome: 僅更新本 `tasks.md`；未執行產品程式、未修改 `app.py`、未發生外部 side effect。
