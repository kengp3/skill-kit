# Run: 實作 receipt 整合

Scope / exclusions: 僅修改 amounts.py、labels.py、receipt.py、tasks.md、evidence/；check.py 與其他檔案唯讀。
Materials and Definition of Done: check.py 通過；subtotal 計算 cents * quantity 且空清單為 0；label 去除首尾空白且空白名稱為 Guest；receipt 整合兩者。
Authority: tasks.md；coordinator: /root/remfix_56_parallel
Workspace / baseline: /private/tmp/task-harness-remfix-4199tvtt/sol56/parallel
Available tools / execution limits / permissions: exactly two native workers；無網路、安裝或外部操作。

| ID | Outcome | Depends on | Owner / handle | State |
| --- | --- | --- | --- | --- |
| T1 | subtotal cents * quantity，空清單為 0 | none | /root/remfix_56_parallel/amounts_worker | done |
| T2 | label strip，空白名稱為 Guest | none | /root/remfix_56_parallel/labels_worker | done |
| T3 | receipt 整合並通過 check.py | T1, T2 | coordinator | done |

## Checkpoint

Completed and accepted: T1、T2、T3；`python3 -B check.py` exit 0，輸出 `PASS receipt integration`。
Active worker handles and last observed state: T1、T2 workers completed；無 active worker。
Unresolved work, decisions, and next ready tasks: none
Side effects attempted and receipt / unknown outcome: none；首次驗證 wrapper 因 zsh `status` 為唯讀變數而 exit 1，checker 本身已輸出 PASS，之後以乾淨命令重跑並 exit 0。

Evidence: evidence/overlap.json、evidence/amounts-worker.txt、evidence/labels-worker.txt、evidence/integration.txt
