# Receipt CLI 任務規劃

## Objective
將現有 `app.py` 的加總函式接成 CLI：接受名稱與整數金額清單，輸出姓名及總額。本次只完成規劃。

## Background
現有 `app.py` 僅有 `total(values)`，透過 `sum(values)` 加總，尚無 CLI。原草案 A 與 B 互相依賴，C 依賴不存在的 X；改為單一端到端任務 A，將 B 的格式化與 C 的驗證納入 A，移除無來源的 X。B、C 作為舊草案 ID 保留此對照，不再是獨立任務。

## Materials
- 專案根目錄：`/private/tmp/task-harness-review-_n73s1n9/plan-fixed`
- 實際已讀：`project-setting.md`、`tasks.md`、`app.py`、`other-plan.md`、`user-note.txt`。
- 本文件 `tasks.md` 是唯一任務狀態來源；coordinator 負責更新。
- 根目錄內未找到 `AGENTS.md`；依提供的工作指示及 `project-setting.md` 執行。
- Baseline：本 fixture 無 `.git`，不查閱父目錄；以檔案 SHA-256 記錄版本。
- `app.py`：`3251dbf18617cd67c47707cb9bd1611dbac212ff0ee9814a75b8ce1f34b85aad`

## Boundaries
- 本次只可更新既有 `tasks.md`，不修改或執行 CLI 實作、不建立測試或新 tracker。
- 保留 `other-plan.md`、`user-note.txt` 及其他既有內容。
- 未來實作須另有授權；預計僅涉及 `app.py` 與一個最小可執行 CLI 檢查檔 `test_receipt.py`。
- 可用工具：本機檔案讀寫與 Python 3；本次僅用於閱讀、規劃與規劃產物檢查。
- 不委派、不建立外部事項、不使用網路或執行 remote changes；無指定時間、金額或 token 預算。

## Assumptions
- 採 positional arguments：`python3 app.py NAME AMOUNT [AMOUNT ...]`；含空白姓名由 shell 引號包住。
- 金額至少一筆，採十進位整數，允許零與負數；不加入幣別、小數、檔案輸入或互動模式。
- 成功時 stdout 恰為 `姓名: 總額` 一行，exit code 0；缺少參數或非整數時 exit code 非 0、stderr 提供錯誤，stdout 不輸出收據。
- 這些是讓後續工作可執行的規劃預設，並非已驗證的程式行為。

## Definition of Done
- 本次規劃：沿用本文件，列出穩定 ID、無循環且存在的依賴、寫入範圍、驗收條件與可重跑檢查；其他檔案不變。
- 未來 CLI：A 的全部驗收條件在當時實際產物上通過，並記錄指令、exit code 與檔案指紋，才可標示 done。

| ID | Outcome | Depends on | Owner / handle | State |
| --- | --- | --- | --- | --- |
| A | 完成 receipt CLI 並通過同一任務內的直接驗證 | none | unassigned / none | pending |

## A
- Write scope / shared resources：`app.py`、`test_receipt.py`；無服務、資料庫或共享 port。任務狀態僅由 coordinator 寫入本文件。
- Inputs / output location：以上 CLI 契約、現有 `app.py`；輸出仍位於同一專案根目錄。
- 實作方式：重用既有 `total(values)`；使用 Python 標準庫 `argparse` 解析姓名及一個以上 `type=int` 金額，加上 CLI entry point，不新增依賴。
- Acceptance：有效輸入正確加總並保留姓名；錯誤輸入符合上述 stderr、stdout 及 exit code 契約；import `app` 不觸發 CLI。
- Verify（未執行，後續以一個 `test_receipt.py` 使用標準庫 subprocess 與 assert 驗證）：

| 指令／情境 | 預期結果 |
| --- | --- |
| `python3 app.py 王小明 10 20` | stdout `王小明: 30\n`、stderr 空、exit 0 |
| `python3 app.py "王 小明" 0 -5 12` | stdout `王 小明: 7\n`、stderr 空、exit 0 |
| `python3 app.py 小明 8` | stdout `小明: 8\n`、stderr 空、exit 0 |
| `python3 app.py` | stdout 空、stderr 有錯誤、exit 非 0 |
| `python3 app.py 小明` | stdout 空、stderr 有錯誤、exit 非 0 |
| `python3 app.py 小明 1.5` | stdout 空、stderr 有錯誤、exit 非 0 |
| `python3 app.py 小明 abc` | stdout 空、stderr 有錯誤、exit 非 0 |
| `python3 -c 'import app; assert app.total([2, -1]) == 1'` | 無輸出、exit 0 |

- 後續統一驗證入口：`python3 test_receipt.py`；需檢查每個 subprocess 的 stdout、stderr 與 returncode，全部斷言通過才接受 A。
- Attempt / last update：2026-10-02，僅規劃；實作 attempt 0。
- Evidence：目前僅有檔案閱讀及 baseline 指紋，尚無實作或測試結果。
- Blocker / next action：無技術 blocker；只有取得實作授權後，才可由 coordinator 重新讀取本文件、規則及實際檔案，執行 A。

## Checkpoint
- Completed and accepted：已整理規劃，修正循環及缺失依賴，保留舊 ID 對照；未完成 CLI 實作。
- Active worker handles：none；本次沒有啟動任何 worker。
- Unresolved work：A 維持 pending；依賴已滿足，但本次 plan-only 授權不允許派工或執行。
- Side effects：僅更新本文件；沒有外部操作或未知結果。
- 規劃檢查：A 是唯一有效任務，depends on none；沒有缺失 ID、自我依賴、循環或等待後繼驗收的死鎖。
