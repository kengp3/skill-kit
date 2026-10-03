# Receipt CLI 可執行清單（僅規劃）

## 任務定義
Objective：CLI 接受姓名與整數金額清單，輸出姓名與總額；姓名為空字串或其他錯誤輸入時，以非零狀態退出。
Background：既有 app.py 僅含 total(values)，使用 sum(values) 計算總額，尚無 CLI。
Materials：app.py、原 tasks.md 草案、project-setting.md、user-note.txt；other-plan.md 是另一項未完成工作。
Boundaries：本次只整理此 tasks.md，不實作、不執行 CLI；其餘現有檔案唯讀。未授權網路、安裝、委派或外部操作。
Assumptions：後續以 `python3 app.py NAME AMOUNT [AMOUNT ...]` 為介面；金額至少一個，接受零與負整數，不接受小數或非整數。成功輸出一行 `NAME: TOTAL`；保留姓名內容。空白姓名未另訂規則，本清單僅要求拒絕空字串。
Definition of Done：本次完成條件是清單具有有效依賴、驗收情境與恢復點；CLI 的完成條件另列於 A，尚未驗證或完成。

Authority：此 tasks.md 是唯一任務狀態來源。
Current coordinator：/root/reval03_61_plan；後續實作者未指派。
Workspace / baseline：/private/tmp/task-harness-reval03-rmiru6z0/sol61/plan；非 Git repository，沒有 revision；基準為上述現有檔案，本次僅修改 tasks.md。
Available tools / execution limits / permissions：本次使用本機檔案讀取與編輯；僅 tasks.md 可寫。後續實作需另行授權，Python 3 與檢查 runner 的實際可執行性尚未驗證；無指定時間、金錢或 token 預算。

## 草案依賴修正
原 A 與 B 互相依賴，形成循環；格式化屬 CLI 同一端到端成果，將 B 併入 A。原 C 指向不存在的 X，且只重複 CLI 驗收，將 C 的驗證責任併入 A。保留 A 的穩定 ID；B、C 為已合併草案項目，不標記 done。沒有獨立 X 或第二份 tracker。

| ID | Outcome | Depends on | Owner / handle | State |
| --- | --- | --- | --- | --- |
| A | 實作並驗證 receipt CLI，包含輸入驗證、總額與輸出格式 | none | unassigned | pending |

## A
Write scope / shared resources：未來授權後，最小修改 app.py，新增一個使用標準函式庫 subprocess 的 check_receipt.py；驗證 receipts 放 evidence/。保留其餘檔案；實作者不得更新共享 tasks.md，由當時 coordinator 更新。這些未來寫入範圍並非本次執行授權。
Inputs and output location：同一專案的 app.py 與本清單；沿用 total(values)，由 CLI 呼叫既有 sum 計算流程。
Task completion criteria：在同一成果內完成 argv 解析、姓名與整數驗證、總額及格式；錯誤輸入非零退出，錯誤訊息送 stderr，不輸出成功 receipt；留下一個可重跑的 check_receipt.py，所有下列情境通過且來源指紋穩定後才能接受 A。
Verify（以下皆為未執行的預定情境）：

| 情境 | 呼叫範例 | 預期結果 |
| --- | --- | --- |
| 多筆金額 | `python3 app.py Alice 10 20` | 狀態 0，stdout 為 `Alice: 30` 加換行 |
| Unicode 與空格姓名 | `python3 app.py '王 小明' 5` | 狀態 0，stdout 為 `王 小明: 5` 加換行 |
| 零、負值 | `python3 app.py Alice 0 -3 7` | 狀態 0，stdout 為 `Alice: 4` 加換行 |
| 空字串姓名 | `python3 app.py '' 10` | 非零退出、stderr 有錯誤、無成功 receipt |
| 缺少姓名與金額 | `python3 app.py` | 非零退出、stderr 有錯誤、無成功 receipt |
| 缺少金額 | `python3 app.py Alice` | 非零退出、stderr 有錯誤、無成功 receipt |
| 非整數／小數 | `python3 app.py Alice nope`；`python3 app.py Alice 1.5` | 每次皆非零退出、stderr 有錯誤、無成功 receipt |
| 混合有效與錯誤值 | `python3 app.py Alice 10 nope` | 非零退出，不產生部分總額 receipt |

預定 receipt 指令（非本次實際 invocation；單一 checker 驗證上表）：
```sh
python3 /private/tmp/task-harness-reval03-rmiru6z0/sol61/skill/scripts/run_check.py --output evidence/A-check-1.json --source app.py --source check_receipt.py -- python3 check_receipt.py
```
在專案根目錄執行；重試另用獨立 receipt 檔名。讀取 receipt，只有 state=finished、command returncode=0 且來源穩定才能接受；Python 3 不可用或結果 unknown 時不得宣稱完成。
Attempt / last update：0；僅完成規劃，未啟動實作或驗收。
Evidence：尚無 CLI 驗收 receipt；上方指令僅供後續重現。
Blocker / next action：實作未獲本次授權；取得執行授權後重讀規則與現有檔案，確認工具、寫入範圍及 A 無衝突，再先由 coordinator 保存 running checkpoint，才開始 A。

## Checkpoint
Completed and accepted：規劃整理完成；沒有實作任務被接受。
Active worker handles and last observed state：無。
Unresolved work, decisions, and next ready tasks：A 為 pending、無依賴，但仍須後續執行授權；介面與金額數量是上列明示假設。
Side effects attempted and receipt / unknown outcome：只編輯此 tasks.md；未執行 app.py，沒有外部副作用或未知執行結果。本次到此停止。
