# Run: receipt CLI 可執行規劃（只規劃）

Objective：CLI 接受姓名與整數金額清單，輸出姓名與總額；空姓名或錯誤輸入須以非零狀態退出。
Background：原草案 A/B 互相依賴，C 引用不存在的 X；合併為一個完整結果，避免循環與驗收死鎖。
Materials：現有 tasks.md、project-setting.md、app.py（只有 total(values) 回傳 sum(values)）。
Boundaries：本次僅整理此清單與 evidence/；不實作、不執行 CLI、不委派、不安裝、不使用網路或外部服務。保留 other-plan.md、user-note.txt 與 app.py。
Assumptions：未指定介面，未來實作預設 python3 app.py NAME AMOUNT [AMOUNT ...]；至少一筆金額；負數與零合法；小數不合法；輸出單行 NAME: TOTAL。空字串必須拒絕，並建議拒絕純空白姓名。這些預設可在實作前調整，並同步更新驗收。
Definition of Done：本次完成無循環、無缺失依賴的規劃與具體驗證情境；CLI 完成另須以下所有驗收通過。
Authority：本檔 tasks.md 是唯一任務狀態來源；coordinator：當前規劃 agent /root/remfix2_61_plan。
Workspace / baseline：/private/tmp/task-harness-remfix2-aok63ea9/sol61/plan；Git revision 未確認，採檔案 SHA-256，見 evidence/plan-review.md。未進行實作變更。
Available tools / execution limits / permissions：可用檔案讀取與本機 shell/Python；本次寫入限 tasks.md 與 evidence/；無明示時間、成本或 token 預算；不授權未來執行或委派。

| ID | Outcome | Depends on | Owner / handle | State |
| --- | --- | --- | --- | --- |
| A | 實作並驗收 receipt CLI 全流程（含原 B 格式與 C 驗證） | none | unassigned / 尚未啟動 | pending |

## A
Write scope / shared resources：未來授權實作時，僅 app.py 與必要的一個可執行檢查檔；避免獨立 formatting 層或新增依賴。原 B/C 併入 A，不再保留不存在的 X。
Inputs and output location：現有 app.py 的 total(values) 應重用；輸入 argv，正常結果 stdout，錯誤訊息 stderr；預定 CLI 入口 app.py。
Acceptance：姓名不得為空；金額皆為整數；合法輸入輸出原姓名與正確總額並 exit 0；缺少參數、非法金額與空姓名 exit 非零，且不得輸出成功收據。格式與至少一筆金額依上述明示假設。
Verify（未執行，未來需授權實作後逐一記錄結果與各自 exit status）：
- python3 app.py Alice 10 20 → stdout「Alice: 30」，exit 0。
- python3 app.py '王 小明' -5 0 12 → stdout「王 小明: 7」，exit 0。
- python3 app.py Alice 0 → stdout「Alice: 0」，exit 0。
- python3 app.py '' 10 → stderr 錯誤、無成功收據、exit 非零。
- python3 app.py Alice abc 與 python3 app.py Alice 1.5 → 各自 stderr 錯誤、無成功收據、exit 非零。
- python3 app.py 與 python3 app.py Alice → 各自 stderr 錯誤、無成功收據、exit 非零。
- 使用 Python 標準函式庫 subprocess 留下一個可執行檢查，覆蓋上述正常與錯誤分支，並檢查 stdout/stderr 與退出碼。
Attempt / last update：0；2026-10-02 完成規劃，未啟動實作。
Evidence：evidence/plan-review.md 僅證明規劃結構與未修改保留檔案；不代表 CLI 驗收。
Blocker / next action：本次只規劃；收到明確實作授權後，A 無前置依賴，可由 coordinator 執行。

## Checkpoint
Completed and accepted：規劃整理與依賴修正完成；實作任務無已完成項。
Active worker handles and last observed state：無；未委派。
Unresolved work, decisions, and next ready tasks：A pending；實作前確認或沿用已列 CLI 介面、空清單與輸出格式假設。
Side effects attempted and receipt / unknown outcome：僅寫 tasks.md 與 evidence/plan-review.md；無外部副作用，無未知操作結果。
