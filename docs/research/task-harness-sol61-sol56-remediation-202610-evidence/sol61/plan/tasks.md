# Run: receipt CLI 可執行清單（只規劃）

## Objective
CLI 接受姓名與整數金額清單，輸出姓名與總額；姓名不可為空字串，錯誤輸入須以非零狀態退出。

## Background / Materials
現有 tasks.md 的 A、B 相互依賴形成循環，C 引用不存在的 X。本次保留 A/B/C ID，將 A 定義為完整 CLI 行為、B 為輸出格式驗證、C 為整合驗收；不新增第二份 tracker。
現有 app.py 僅有 total(values): return sum(values)，未有 CLI。other-plan.md、user-note.txt 為既有使用者工作。

## Boundaries / Assumptions
本次只整理規劃，不實作、不執行 CLI 或測試、不委派、不連網、不安裝、不進行外部操作。
後續實作假設：介面為 python3 app.py NAME AMOUNT [AMOUNT ...]；至少一個金額，接受正整數、0、負整數；stdout 格式為 NAME: TOTAL 加換行，錯誤訊息送 stderr。空白姓名也視為無效。這些是規劃選擇，非已存在行為。

## Definition of Done
本次：清單具有有效且無循環依賴，每項有明確輸入、寫入範圍、驗收與具體檢查；完成規劃後停止。
後續實作：有效輸入得到姓名與總額，缺參數、空姓名、非整數輸入都失敗退出；當前 artifact 通過下述檢查。

Authority: 本 tasks.md；coordinator: 本次 task-harness 規劃代理。
Workspace / baseline: /private/tmp/task-harness-remfix-4199tvtt/sol61/plan；非 Git repository（rev-parse exit 128），無 revision/dirty 狀態可用。規劃前各檔 SHA-256 見 evidence/planning-baseline.json。
Available tools / execution limits / permissions: 本機讀檔、Python、shell；本次只允許寫 tasks.md 與 evidence/。其他 fixture 與 skill 唯讀；無額外時間、成本或 token 預算。未建立 worker、goal、chat 或 automation。

| ID | Outcome | Depends on | Owner / handle | State |
| --- | --- | --- | --- | --- |
| A | 完整 receipt CLI 與自身驗證 | none | unassigned / 無 | pending |
| B | 驗證 CLI 格式契約 | A | unassigned / 無 | pending |
| C | 最終有效與錯誤情境整合驗收 | B | unassigned / 無 | pending |

## A
Write scope / shared resources: 後續須取得執行授權；預定 app.py 與一份最小本機自我檢查，單一 writer；保留無關檔案。
Inputs and output location: 現有 app.py、上述介面契約；輸出仍為 app.py。
Acceptance: 重用 total；解析整數、驗證姓名及必填參數；成功輸出總額，錯誤非零退出。A 自身檢查通過即可接受，不等待 B/C。
Verify: 後續以 subprocess 檢查 python3 app.py Alice 10 -3 0 → exit 0、stdout 精確 Alice: 7\n；python3 app.py '' 1 與 python3 app.py Alice nope → 非零、stderr 有訊息、stdout 無 receipt。
Attempt / last update: 0；只完成規劃，未執行。
Evidence: 尚無實作證據；執行時記錄每次 command、exit status、stdout/stderr 與檔案 SHA-256。
Blocker / next action: 本次禁止實作；取得執行授權後由 coordinator 串行處理 A。

## B
Write scope / shared resources: 後續 app.py（僅格式缺陷修正）、同一份最小檢查；不新增 formatter 抽象。
Inputs and output location: 已接受且 fingerprint 仍有效的 A；沿用 app.py。
Acceptance: 姓名完整保留，格式固定 NAME: TOTAL 加換行，無多餘 stdout；B 自身檢查通過即可接受，不等待 C。
Verify: python3 app.py '王 小明' 2 3 → exit 0、stdout 精確 王 小明: 5\n；Alice 0 → Alice: 0\n。
Attempt / last update: 0；只完成規劃，未執行。
Evidence: 尚無格式驗證證據；記錄個別結果及 SHA-256。
Blocker / next action: A 必須 done 且有效；若 B 修改 A 行為，重開 A 的受影響驗收。

## C
Write scope / shared resources: 後續 evidence/ 與同一份最小檢查；如需修正 app.py，先記錄並重開受影響 A/B。
Inputs and output location: 當前已接受的 A/B；整合結果記錄於 evidence/。
Acceptance: 最終同一 app.py 通過所有需求，證據綁定當前版本；無缺項才標 done。
Verify: 重跑 A/B 場景，並檢查無參數、只有姓名、空白姓名、金額 1.5、金額 abc → 各自非零退出、stderr 有訊息、stdout 無 receipt；多筆 1 2 3 → Alice: 6\n。每個 invocation 單獨記錄 exit status。
Attempt / last update: 0；只完成規劃，未執行。
Evidence: 尚無整合驗收證據；後續記錄指令、個別 exit status、原始輸出與 app.py/檢查檔 fingerprint。
Blocker / next action: B 必須 done 且有效；完成後 reconcile 全部需求與 tracker。

## Checkpoint
Completed and accepted: 本次規劃整理與靜態清單驗證；實作 A/B/C 均未開始。
Active worker handles and last observed state: 無；未委派。
Unresolved work, decisions, and next ready tasks: A 為下一項，僅在新執行授權後可開始；B 等 A，C 等 B。依賴為 A → B → C，無不存在的 ID、自依賴或循環，也無 prerequisite 等待 successor 驗收。
Side effects attempted and receipt / unknown outcome: 僅 tasks.md 與 evidence/ 文件寫入；無外部副作用或未知結果。
