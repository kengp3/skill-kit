# Run: receipt CLI 可執行計畫

## Objective
CLI 接受姓名與整數金額清單，輸出姓名與總額；姓名不得為空字串，錯誤輸入以非零退出碼結束。

## Background / Materials
原草案 A 與 B 互相依賴，C 依賴不存在的 X。現有 app.py 只有 total(values)，使用 sum(values)。本計畫將 A（CLI）、B（格式）及 C（驗證）合併為一個完整成果，保留全部驗收要求，消除循環與缺失依賴；驗證是成果的接受條件，不能等待後繼任務。
材料：本目錄的 app.py、project-setting.md、tasks.md；other-plan.md、user-note.txt 為須保留的他人內容。

## Boundaries / Assumptions
本次只規劃，唯一寫入檔案為 tasks.md。不得實作、執行 CLI、委派、使用網路、安裝或進行外部操作；其餘材料唯讀。
供後續實作使用的最小介面假設：python3 app.py NAME [AMOUNT ...]；整數可為負數，空清單總額為 0，輸出單行「NAME: TOTAL」。僅空字串姓名非法；不另加空白姓名或金額正值限制。

## Definition of Done
計畫完成：單一權威清單、有效依賴、明確寫入範圍與逐項驗收，保留他人內容。
實作完成：以下 A 的全部驗收在當前檔案上通過並保留實際結果；本次不宣稱實作完成。

Authority: 本 tasks.md；coordinator: 當前規劃 agent /root/remfix3_61_plan。
Workspace / baseline: /private/tmp/task-harness-remfix3-1nis2bc6/sol61/plan；非 Git 基準，使用材料 SHA-256。app.py 基準為 3251dbf18617cd67c47707cb9bd1611dbac212ff0ee9814a75b8ce1f34b85aad。
Available tools / limits / permissions: 本次使用 exec_command 讀取材料與寫入計畫；未指定時間或費用預算。後續實作須另獲授權，Python 3 可用性尚未驗證。

| ID | Outcome | Depends on | Owner / handle | State |
| --- | --- | --- | --- | --- |
| A | 完成 receipt CLI、輸出格式及直接驗證 | none | unassigned / 無 worker | pending |

## A
Write scope / shared resources: 後續授權後僅 app.py 與一個最小可執行檢查檔；由 coordinator 單獨更新 tasks.md，驗證紀錄依規則放 evidence/。保留 other-plan.md、user-note.txt、project-setting.md；無共享服務。
Inputs / output: 沿用 app.py 的 total(values)，以標準函式庫解析參數，結果仍在本專案；不新增依賴。
Acceptance / Verify（以下為待執行情境，不是執行證據）:
- python3 app.py Alice 10 20 → stdout 為 Alice: 30，退出碼 0。
- python3 app.py Alice -5 2 → stdout 為 Alice: -3，退出碼 0。
- python3 app.py Alice → stdout 為 Alice: 0，退出碼 0。
- python3 app.py '' 10 → 非零退出碼，stderr 有錯誤說明，不輸出成功收據。
- python3 app.py Alice abc，以及 python3 app.py Alice 1.5 → 各自非零退出碼，stderr 有錯誤說明。
- python3 app.py（缺姓名）→ 非零退出碼，stderr 有錯誤說明。
用一個 subprocess 型最小 runnable check 收集各情境的 stdout、stderr、returncode；不以最後一個命令的退出碼代表全部結果。驗收不依賴其他任務。保留實際命令、工具回條、結果與測試時檔案指紋於 evidence/，再將 A 設為 done。
Attempt / last update: 尚未開始，2026-10-02 只整理計畫。
Evidence: 本次僅讀取材料，exec_command 回條 dc8934 顯示上述原始草案及 total(values)；b8f9d3 記錄材料指紋。沒有 CLI 執行或驗收結果。
Blocker / next action: 本次授權止於規劃；取得實作授權後重新讀取規則與材料，確認 Python 3，先成功保存 A=running，再實作與驗證。

## Checkpoint
Completed and accepted: 規劃已完成；原 A/B/C 合併理由與所有需求已保留，依賴只有 A→none，無循環、缺失 ID 或自我依賴。
Active worker handles: 無；未委派。
Unresolved / next ready tasks: A 尚未開始，依賴就緒但未獲本次實作授權。
Side effects: 僅更新 tasks.md；無產品或外部操作。
