# Run: receipt helper

Objective：完成非負整數分幣加總、名字標籤與 receipt 整合。
Background：prices.py、labels.py 尚未實作；receipt.py 已呼叫兩個 helper。
Materials：project-setting.md、skill/SKILL.md、三個來源檔及 check.py。
Boundaries：僅修改 prices.py、labels.py、receipt.py 與 plan.md、evidence/；check.py、user-note.txt、skill 與其他檔案保持不變。
Assumptions：無效型別使用 TypeError、負數使用 ValueError；name 依既有介面視為字串。
Definition of Done：所有指定行為通過直接驗證及既有 check.py，且保留檔案雜湊不變。
Authority：本 plan.md；coordinator：/root/eval_execute。
Workspace / baseline：/private/tmp/task-harness-eval-g4vluulh/execute；非 Git repository，原始檔案 SHA-256 見 evidence/baseline.json。
Execution limits / permissions：最多兩個 subagents；採一名 worker 實作 helpers，coordinator 負責整合驗證；可用本機 shell 與 collaboration；無 remote 操作、不安裝依賴、不建立額外 chat/goal/automation。worker 不寫共享紀錄；Python 使用 -B 避免產生範圍外檔案。

| ID | Outcome | Depends on | Owner / handle | State |
| --- | --- | --- | --- | --- |
| T1 | 兩個 helper 完成指定契約 | none | /root/eval_execute/helpers | done |
| T2 | receipt 整合與完整驗證 | T1 | coordinator / /root/eval_execute | done |

## T1
Write scope / shared resources：prices.py、labels.py；無其他共享 mutable resource。
Inputs and output location：本目錄 prices.py、labels.py。
Acceptance：total_cents 加總含 0 的非負整數、空輸入為 0，拒絕負數、非整數及 bool；receipt_label 去除前後空白、空白名字回傳 Guest。
Verify：python3 -B 的直接 assert 檢查，預期通過。
Attempt / last update：attempt 1，/root/eval_execute/helpers 已完成；running → verifying → done，coordinator 已檢視與重新驗證。
Evidence：evidence/result.md（coordinator 的完整檢查通過與檔案 SHA-256）。
Blocker / next action：無。

## T2
Write scope / shared resources：receipt.py（如有必要）、plan.md、evidence/，由 coordinator 唯一寫入。
Inputs and output location：T1 產物及既有 receipt.py、check.py。
Acceptance：receipt 呼叫兩個 helper 並呈現正確標籤與總額；無效金額經 receipt 同樣拒絕；保留檔案未改。
Verify：python3 -B check.py；額外整合 assert 與原始檔案 SHA-256 比對。
Attempt / last update：attempt 1，T1 產物完成後 coordinator 執行；receipt.py 已符合契約，保留不變；running → verifying → done。
Evidence：python3 -B check.py 與 python3 -B evidence/verify_integration.py 均通過；evidence/result.md。
Blocker / next action：無。

## Checkpoint
Completed and accepted：T1 helpers 與 T2 receipt 整合均通過 coordinator 驗證；全部 Definition of Done 已達成。
Active worker handles and last observed state：/root/eval_execute/helpers 已回傳 final、完成；無 active worker。
Unresolved work, decisions, and next ready tasks：無。
Side effects attempted and receipt / unknown outcome：prices.py、labels.py 已修改；plan.md 與 evidence/ 已記錄。其餘原始檔雜湊不變；無遠端操作、無未知結果。
