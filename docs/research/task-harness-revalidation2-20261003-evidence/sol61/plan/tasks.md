# Run: receipt CLI 可執行規劃

## Objective
將既有草案整理成可執行清單；本次只規劃，不實作或執行 CLI。

## Background / Materials
現有 app.py 只有 total(values)，直接加總輸入；尚無 CLI、姓名或錯誤輸入處理。材料：app.py、原 tasks.md、user-note.txt、project-setting.md。

## Boundaries / Assumptions
- 本次僅修改 tasks.md，規劃驗證證據放 evidence/；其他檔案保持唯讀。
- 未授權實作、委派、網路、安裝、外部副作用或 fixture 外變更。
- 建議未來介面：python3 app.py NAME AMOUNT [AMOUNT ...]；至少一個金額，以十進位整數解析，允許負數及零。
- 建議輸出：一行「NAME: TOTAL」。姓名依原文字輸出；空字串拒絕。只有空白的姓名是否拒絕未指定，先以非空字串契約規劃。
- 以上介面、格式及清單至少一項屬規劃假設；未來執行前若使用者有不同要求，先調整 A 的契約與驗收案例。

## Definition of Done
本次：建立唯一清單，修正依賴、保留原草案目的、列出輸入輸出契約與可觀察驗收；所有實作維持 pending。
未來 A：CLI 接受姓名及整數金額清單，正確輸出姓名與總額；姓名為空或其他錯誤輸入時非零退出，stderr 有錯誤說明，stdout 無成功收據；直接案例全部通過且有當次證據。

Authority: 本 tasks.md 是唯一任務狀態來源。
Current coordinator: /root/reval2_61_plan（本次規劃）
Workspace / baseline: /private/tmp/task-harness-reval2-3beplc9e/sol61/plan；檔案型 fixture，未取得 revision。基線 app.py 為兩行 total(values)；tasks.md 原有 A/B 循環及 C→X 缺失依賴。
Available tools / execution limits / permissions: 本次 shell/Python 3 僅讀取及寫入授權規劃檔與 evidence/；不執行產品程式；無指定時間、金錢或 token 預算；不使用委派。

## 草案修正
原 A 與 B 互相依賴，合併成 A 的完整 CLI outcome；原 B「格式化收據」納入 A 的輸出契約。原 C「驗證收據」與 A 驗收重複，納入 A 的直接案例及證據，不獨立排程。原 C 指向不存在的 X，移除此無材料依賴，不捏造 X。保留 A 作為穩定 ID；B、C 為已合併歷史 ID，並非完成的任務。

| ID | Outcome | Depends on | Owner / handle | Task attempt | State | Acceptance receipt |
| --- | --- | --- | --- | --- | --- | --- |
| A | 實作及驗證 receipt CLI 完整流程（含原 B/C） | none | unassigned | not started | pending | none |

## A
Write scope / shared resources: 未來執行須另獲授權；建議 app.py、必要測試及 evidence/A-*。不得修改 user-note.txt、other-plan.md、project-setting.md 或 skill；單一執行者負責產品寫入，協調者負責 tasks.md。
Inputs and output location: 本計畫契約及 app.py；輸出修改後 CLI、直接案例與當次 evidence/ 收據。
Task completion criteria: 正常流程、格式與錯誤退出符合 Definition of Done；保留可用的 total(values) 行為，檢查最終檔案及變更範圍，驗收證據符合當次來源指紋後才標記 done。
Verify（未執行）:
- python3 app.py Alice 10 20 → exit 0，stdout 為 Alice: 30 加換行。
- python3 app.py '王小明' 0 -5 12 → exit 0，stdout 為 王小明: 7 加換行。
- python3 app.py Alice 999999999999999999999 1 → exit 0，總額 1000000000000000000000。
- python3 app.py '' 1、python3 app.py Alice nope、python3 app.py Alice 1.5、python3 app.py Alice、python3 app.py → 每個案例非零退出、stderr 錯誤說明、stdout 無成功收據。
- 每個案例使用 skill/scripts/run_check.py 各存一份獨立 JSON，記錄 app.py 及測試來源指紋；以 JSON 的 finished、來源穩定及實際結果判定，錯誤案例依預期非零退出判定，不視為正常成功案例。
Check attempts: none；產品案例未執行。
Last update: 2026-10-03，本次僅完成規劃。
Evidence: none；沒有實作驗收證據。
Blocker / next action: 目前只允許規劃；取得執行授權後，核對假設、保存 A 的 owner、attempt 1、running checkpoint，再開始產品操作。

## 規劃文件驗證
Check ID: plan-structure；attempt: 1；receipt path: evidence/plan-structure-1.json。此檢查只驗證清單結構與必要內容，不驗證 CLI 或將 A 標記完成。

## Checkpoint
Completed and accepted: 草案依賴已整併，規劃產出完成；結構檢查結果見 evidence/plan-structure-1.json。
Active worker handles and last observed state: none；未啟動 worker。
Unresolved work, decisions, and next ready tasks: A pending，尚未實作。輸出格式、空清單及純空白姓名依上述假設；無需阻止本次規劃，但執行前應確認契約。
Side effects attempted and receipt / unknown outcome: 僅本 tasks.md 及規劃 evidence/ 的本機寫入；無產品或外部副作用。
