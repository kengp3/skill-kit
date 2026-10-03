# Receipt CLI 可執行清單（僅規劃）

Objective：CLI 接受姓名與整數金額清單，輸出姓名與總額；姓名不可為空字串，錯誤輸入須非零退出。
Background：原草案 A/B 互相依賴，C 依賴不存在的 X；app.py 目前僅有 total(values)，呼叫 sum(values)。
Materials：已讀取 project-setting.md、原 tasks.md、app.py。
Boundaries：本次只整理 tasks.md，不實作、執行 CLI、委派、安裝、連網或修改其他檔案。
Assumptions：規劃介面為 `python3 app.py NAME [AMOUNT ...]`；允許負整數，空金額清單總額為 0；stdout 一行 `姓名: 總額`。只拒絕空字串姓名，未額外禁止純空白姓名。以上是待確認規劃假設，非既有行為。
Definition of Done：本次須完成有效依賴、具體驗收及重啟資訊；後續實作須通過所有成功與失敗案例。

Authority：tasks.md 為唯一任務狀態來源；coordinator：本次規劃協調者；無 worker handle。
Workspace：/private/tmp/task-harness-solmatrix-mc_zeld9/sol61/plan（已確認根目錄）。
Baseline：Git revision 未查；採實際檔案 SHA-256：
- app.py：3251dbf18617cd67c47707cb9bd1611dbac212ff0ee9814a75b8ce1f34b85aad
- 原 tasks.md：c18dbdcb4e5dbcf61c6fe144281798d1e16bcd49c88cceb2d8cb4ba714f6fede
- project-setting.md：d26b8e41c395dbe0080550bd8dc8b0d1fa74babd113cc5b61a12f272761a39d1
Execution limits / permissions：可使用檔案讀取、shell 文件檢查與文件寫入工具；目前只授權規劃。Python 可用性未確認；未指定時間、金額或 token 預算；後續實作需另有授權。

| ID | Outcome | Depends on | Owner / handle | State |
| --- | --- | --- | --- | --- |
| A | 確認命令及輸出契約 | none | unassigned / 無 | pending |
| B | 完成 CLI 與直接檢查 | A | unassigned / 無 | pending |
| C | 驗收最終 CLI 完整流程 | B | unassigned / 無 | pending |

## A：確認契約
Write scope / shared resources：tasks.md，由單一協調者更新狀態。
Inputs / output：使用者需求及上述假設 → tasks.md。
Acceptance：確定參數、空清單、負數、空姓名、格式及退出碼；姓名缺失、空字串、非整數金額均須失敗。若修訂假設，記錄理由及 B/C 影響。
Verify：逐項比對需求與契約，不執行實作步驟。
Attempt / evidence：未開始；已讀取需求與原草案，無 CLI 通過證據。
Blocker / next action：取得實作授權後，確認假設與 Python 環境。

## B：CLI 與直接檢查
Write scope / shared resources：後續 app.py 及一個最小可執行檢查檔；重用 total(values)，不加依賴，不修改無關內容。
Inputs / output：A 契約、app.py → CLI 入口與 runnable check。
Acceptance：解析整數、驗證姓名、計算及格式化總額；成功退出 0；錯誤訊息送 stderr、退出非零且 stdout 無收據。直接檢查必須在 B 內通過，不等待 C 才接受 B。
Verify（後續執行，以 subprocess 捕捉 stdout/stderr/returncode 並斷言）：
- `python3 app.py Alice 10 20 -5` → `Alice: 25`、exit 0。
- `python3 app.py Alice` → `Alice: 0`、exit 0。
- `python3 app.py '' 10`、`python3 app.py`、`python3 app.py Alice 1.5`、`python3 app.py Alice abc` → exit 非零、stderr 有錯誤、stdout 無收據。
Attempt / evidence：未開始，未執行上述命令，無測試結果。
Blocker / next action：A 接受且有實作授權後才開始。

## C：最終流程驗收
Write scope / shared resources：tasks.md 及 evidence/；由協調者寫入，不與 B 同時寫共享檔案。
Inputs / output：B 的最終檔案與檢查 → evidence/ 命令、結果與版本紀錄。
Acceptance：在確認的根目錄重跑所有 B 案例，另驗 Unicode 姓名與 0；保存 Python 版本、實際命令、退出碼及最終檔案 SHA-256。失敗維持 verifying 或 blocked，不能宣稱 done。
Verify（後續執行）：重跑 B 檢查；`python3 app.py 王小明 0 7` → `王小明: 7`、exit 0。
Attempt / evidence：未開始，無驗收結果。
Blocker / next action：B 接受後才開始；相關檔案改變時失效並重驗受影響證據。

## Checkpoint
Completed and accepted：本次清單整理完成；修正 A/B cycle 及缺失 X，依賴為 A → B → C，無自依賴或缺失 ID；實作未完成。
Active worker handles：無；未委派。
Unresolved work / next ready task：A/B/C 均 pending。取得實作授權後先處理 A；本次停止於規劃。
Side effects：僅寫入 tasks.md；保留 app.py、other-plan.md、user-note.txt。沒有 CLI 執行或外部操作；host 留存實際工具紀錄，不生成虛構 receipts。
