# Receipt CLI 執行計畫

## Objective
CLI 接受姓名與整數金額清單，輸出姓名與金額總和；姓名不得為空字串，錯誤輸入以非零退出碼結束。

## Background / Materials
現有 app.py 僅有 total(values)，使用 sum(values)。草案 A 與 B 互相依賴，C 指向不存在的 X，原圖無法執行。
沿用 total(values)；A、B、C 合併為一個端到端任務 A，保留格式與驗證要求於其驗收條件中，消除循環及缺失依賴。B、C 是原草案來源識別，不再是待執行任務。
材料：app.py、project-setting.md、原 tasks.md；other-plan.md 與 user-note.txt 為保留的其他工作。

## Boundaries / Assumptions
本次僅規劃；只寫 tasks.md，沒有實作、測試 CLI、委派、網路、安裝或外部操作。
未來實作須另外取得授權，可修改 app.py 並增加一個最小可執行檢查；不可修改其他計畫或使用者筆記。
採用最小介面：python3 app.py NAME AMOUNT [AMOUNT ...]；至少一筆金額、接受正負及零整數；成功 stdout 為 NAME: TOTAL，失敗訊息送至 stderr。空字串姓名失敗；全空白姓名亦視為無效。

## Definition of Done
實作與最小檢查完成後，成功案例正確輸出姓名與總額且退出 0；空姓名、空白姓名、缺少金額與非整數輸入退出非零。驗證涵蓋負數及零，保留可重跑的檢查與實際結果；僅完成計畫不代表以上已通過。

## 任務狀態
Authority：本檔 tasks.md。
Current coordinator：本 agent /root/remfix4_61_plan（只負責本次計畫）。
Workspace / baseline：/private/tmp/task-harness-remfix4-4pdrhfjg/sol61/plan；已讀取目前檔案，未確認 Git revision；app.py SHA-256 為 3251dbf18617cd67c47707cb9bd1611dbac212ff0ee9814a75b8ce1f34b85aad。
工具 / 限制：本次使用 shell 讀取與寫入指定計畫；未指定時間、金額或 token 預算。沒有執行或委派授權。

| ID | Outcome | Depends on | Owner / handle | State |
| --- | --- | --- | --- | --- |
| A | 實作並驗證完整 receipt CLI（含原 B 格式與 C 檢查） | none | unassigned | pending |

## A
Write scope / shared resources：未來 app.py 與單一最小檢查檔；執行前重新確認授權及檔案狀態。任務狀態由當時 coordinator 寫入 tasks.md，不與其他 writer 重疊。
Inputs / output：現有 app.py 的 total(values)；產出可執行 CLI 與可重跑檢查。
Acceptance：
- 解析 NAME 與一筆以上整數金額，沿用 total(values)，成功輸出 NAME: TOTAL 並退出 0。
- 空字串或全空白姓名、缺少姓名／金額、非整數金額均失敗且退出非零，stderr 有錯誤訊息。
- 用同一最小檢查驗證正常加總、零與負數，以及上述失敗案例。
Verify（未執行的預定案例）：python3 app.py Alice 10 -3 0 → stdout「Alice: 7」、exit 0；python3 app.py '' 1、python3 app.py ' ' 1、python3 app.py、python3 app.py Alice、python3 app.py Alice 1.5、python3 app.py Alice abc → exit 非零。檢查使用 subprocess 收集每次 stdout、stderr、returncode 並 assert。
Attempt / last update：未啟動；本次整理計畫。
Evidence：目前僅有材料讀取與 app.py 指紋，沒有 CLI 執行／驗收結果。未來保存實際 invocation、逐次結果及受測檔案指紋；報告或證據若需另存，依規則置於 evidence/。
Blocker / next action：沒有技術依賴阻塞；執行授權尚未提供。取得授權後重讀規則與檔案，先記錄 A 的 owner、attempt、running，成功寫入狀態後才開始實作。

## Checkpoint
Completed and accepted：計畫整理完成；依賴只有 A → none，沒有循環、自我依賴或不存在的 ID。
Active worker handles：無；未啟動任何 worker。
Unresolved work / next ready task：A 尚未執行；取得執行授權後可開始。
Side effects：僅更新本 tasks.md；沒有產品或外部狀態變更。
