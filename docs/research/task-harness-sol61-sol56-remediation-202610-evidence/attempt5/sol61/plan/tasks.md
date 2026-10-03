# Receipt CLI 執行清單（僅規劃）

## 任務定義
- Objective：CLI 接受姓名與整數金額清單，輸出姓名與總額；姓名不可為空字串，錯誤輸入須以非零狀態退出。
- Background：既有 `app.py` 僅提供 `total(values)`，直接使用 `sum(values)`。
- Materials：本目錄的 `app.py`、`project-setting.md`、既有 tasks.md 草案；`other-plan.md` 與 `user-note.txt` 為他人工作，須保留。
- Boundaries：本次只改寫 tasks.md，不修改或執行 app.py、不建立實作或測試檔、不委派、不使用網路、不安裝、不進行外部操作。
- Assumptions：未指定介面，未來採 `python3 app.py NAME AMOUNT [AMOUNT ...]`；金額清單至少一項，接受零與負整數。成功輸出一行 `NAME: TOTAL`，錯誤訊息寫入 stderr。只含空白的姓名也視為空姓名。此為規劃採用的介面假設，尚未實作。
- Definition of Done：本次完成條件為可執行、無依賴循環、涵蓋成功與錯誤情境的清單；CLI 完成另須 T1 的實作及驗證全部通過。

Authority：本 tasks.md 為唯一任務狀態來源。
Current coordinator：本代理（/root/remfix5_61_plan）；未來執行者尚未指派。
Workspace / baseline：`/private/tmp/task-harness-remfix5-arjbvmfd/sol61/plan`；已讀取現有草案與上述材料，Git revision 未查證。app.py 目前僅有 total 函式。
Available tools / limits / permissions：本次可用本機檔案讀取與 tasks.md 編輯；其餘檔案唯讀。沒有時間、費用或 token 預算指定。未來實作及證據寫入須取得執行授權；文件規則要求證據放在 evidence/。

## 草案修正
原 A（實作）依賴 B（格式），B 又依賴 A，形成循環；C（驗證）依賴不存在的 X。將 A、B、C 合併為 T1，保留三者的要求與驗收；驗證屬 T1 完成條件，沒有另外建立依賴後繼驗證才能完成的任務。

| ID | Outcome | Depends on | Owner / handle | State |
| --- | --- | --- | --- | --- |
| T1 | 可執行且已驗證的 receipt CLI | none | unassigned | pending |

## T1
- Write scope / shared resources：未來僅 app.py 與一個最小測試檔（例如 check_receipt.py）；驗證 receipt 放 evidence/。tasks.md 狀態由協調者單獨更新。不得修改 skill、project-setting.md、other-plan.md、user-note.txt。
- Inputs / output：使用現有 total(values)；輸出為可直接執行的 app.py 與最小可重跑檢查。
- Task completion criteria：使用標準函式庫解析參數、驗證姓名及每個整數金額，沿用 total；成功輸出姓名與正確總額並退出 0；缺少參數、空姓名或非法金額均非零退出，不印成功 receipt。
- Verify：最小檢查以 subprocess 呼叫 CLI，斷言以下輸出及退出狀態；成功 `Alice 10 20` → `Alice: 30`、退出 0；`Alice 0 -3 3` → `Alice: 0`、退出 0；缺少姓名、缺少金額、姓名為空字串或純空白、金額 `abc` 或 `1.5` → 非零退出且 stderr 有錯誤訊息。
- Evidence procedure（未執行）：執行授權後，使用指定 skill 的 scripts/run_check.py，以 Python 3 執行一個 check_receipt.py 指令，保存 evidence/T1-check-1.json，指紋包含 app.py 與 check_receipt.py。讀取 JSON，僅在 state=finished、returncode=0 且來源穩定時接受；失敗修正後使用新 attempt 檔名，不覆蓋前次證據。
- Attempt / last update：未開始實作；本次僅整理計畫。
- Evidence：無實作或驗證 receipt，未宣稱 CLI 通過。
- Blocker / next action：等待明確執行授權；授權後重讀專案規則及材料，確認 T1 scope，先持久化 owner、attempt、running，再實作與驗證，驗收後更新 done。

## Checkpoint
- Completed and accepted：規劃完成；A/B 循環與不存在依賴 X 已消除，合併後無依賴。
- Active worker handles：無；未委派。
- Unresolved work：T1 pending，CLI 實作與驗證皆未開始。
- Side effects attempted：僅更新本 tasks.md；沒有實作、驗證執行或外部操作。
