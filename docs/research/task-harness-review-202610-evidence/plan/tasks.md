# Receipt CLI 任務清單

## Objective
將現有草案整理為可執行的任務與驗證方式。本次只完成規劃，CLI 實作尚未開始。

## Background / Materials
已讀取 `project-setting.md`、原有 `tasks.md`、`app.py`、`other-plan.md`、`user-note.txt`。`app.py` 僅有 `total(values)`，直接回傳 `sum(values)`，尚無 CLI 入口。
原草案 A／B 循環依賴；C 依賴不存在的 X。B 的格式化工作併入 A，保留 A、C 識別碼，C 改為依賴 A。

## Boundaries
- 唯一任務狀態來源：本檔；協調者負責更新。
- 確認專案根目錄：`/private/tmp/task-harness-review-_n73s1n9/plan`。
- 本次僅可修改 `tasks.md`；不實作、不執行 CLI、不建立 worker、goal、排程或外部 issue，無外部副作用。
- 後續實作授權後，預期寫入範圍為 `app.py` 與一個精簡 `test_receipt.py`；若保存驗證紀錄，置於 `evidence/`。保留 `other-plan.md`、`user-note.txt`。
- 可用工具為檔案讀寫與 shell；不新增套件。未指定時間、費用或 token 預算，不另作假設。本次無委派。

## Assumptions
以下是供執行的明確預設，不是已存在的 CLI 行為：
- 命令介面為 `python3 app.py NAME AMOUNT [AMOUNT ...]`，至少一筆金額。
- 名稱不可為空白；含空格的名稱以 shell 引號傳入。
- 金額為十進位整數，可為負數或零；不接受小數或非數字，不引入幣別與小數精度規則。
- 成功時 stdout 為兩行：`姓名：<NAME>`、`總額：<SUM>`，結尾換行，exit code 0。
- 輸入不合法時 stderr 顯示錯誤、exit code 非 0，stdout 不輸出收據。

## Definition of Done
本次規劃：任務範圍、輸出、驗收與驗證情境明確；依賴無缺失、自我依賴或循環；僅更新本檔。
後續 CLI：A、C 的驗收均通過，且證據對應當時的實際檔案；不能將規劃完成視為 CLI 完成。

| ID | Outcome | Depends on | Owner / handle | State |
| --- | --- | --- | --- | --- |
| A | 完整 receipt CLI：解析、驗證、加總與格式輸出 | none | unassigned / none | pending |
| C | 以真實 CLI 行程驗證成功與錯誤路徑 | A | unassigned / none | pending |

## A
Write scope / inputs / output：讀取本檔與現有 `app.py`；只修改 `app.py`。沿用 `total(values)` 與 Python 標準函式庫，加入命令列入口。
Acceptance：符合上述介面、姓名與總額輸出及錯誤行為；不改動無關檔案。
Verify：執行 `python3 app.py Alice 10 20`，預期 stdout 精確為 `姓名：Alice\n總額：30\n`、stderr 空白、exit code 0；最終由 C 完整驗證。
Attempt / evidence：0；未實作、未執行，沒有 runtime 驗證證據。
Blocker / next action：須先取得實作授權；其後可開始 A。

## C
Write scope / inputs / output：A 的實際 `app.py`；新增單一 `test_receipt.py`，用標準函式庫 `subprocess` 和 `assert` 檢查 exit code、stdout、stderr。可將實際結果存入 `evidence/`，不另建 tracker。
Acceptance / Verify：以 `python3 test_receipt.py` 執行下列真實 CLI 情境，全部通過才將 A、C 標為 done：
- `python3 app.py Alice 10 20` → 姓名 Alice、總額 30。
- `python3 app.py '王 小明' -5 0 12` → 保留姓名空格、總額 7。
- `python3 app.py Alice 0` → 總額 0。
- `python3 app.py Alice 99999999999999999999 1` → 總額 100000000000000000000。
- 缺少名稱、僅有名稱、空白名稱、金額 `1.5`、金額 `abc` → 各自 exit code 非 0、stderr 有錯誤、stdout 空白。
成功情境均檢查完整兩行輸出、結尾換行、exit code 0 與空白 stderr。紀錄實際命令、結果及 `app.py`／`test_receipt.py` 的 SHA-256，檔案改動後重新驗證。
Attempt / evidence：0；尚未建立或執行測試。
Blocker / next action：等待實作授權與 A 產物；A 產出後執行 C。

## Checkpoint
- 已完成：現況閱讀與任務重整；B 已併入 A，X 已移除，依賴只有 C → A。
- Active worker handles：none；沒有啟動實作工作。
- 待完成：A、C 均 pending；下一步須在使用者授權實作後重新讀取專案規則、本檔與實際產物，再開始 A。
- Side effects：本次只更新 `tasks.md`；沒有執行 CLI 或外部操作。
- Baseline：`app.py` SHA-256 `3251dbf18617cd67c47707cb9bd1611dbac212ff0ee9814a75b8ce1f34b85aad`；原草案 SHA-256 `f81e10e69143c866b9201f3fb0c4143b47dea53ef5eb3c3dd52ad1c5437ce7ee`。
