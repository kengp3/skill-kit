# Run: 實作 receipt 整合

Scope / exclusions: 僅修改 amounts.py、labels.py、receipt.py、tasks.md 與 evidence/；保留其他檔案。
Materials and Definition of Done: check.py 全部 assertions 通過，並保存 task-harness receipt。
Authority: tasks.md
Current coordinator: /root/reval03_56_parallel
Workspace / baseline: /private/tmp/task-harness-reval03-rmiru6z0/sol56/parallel；三個模組皆為 NotImplementedError。
Available tools / execution limits / permissions: 兩名原生 workers；不得再委派；無網路、安裝或外部動作。

| ID | Outcome | Depends on | Owner / handle | State |
| --- | --- | --- | --- | --- |
| T1 | amounts.py subtotal | none | /root/reval03_56_parallel/amounts_worker | done |
| T2 | labels.py label | none | /root/reval03_56_parallel/labels_worker | done |
| T3 | receipt.py 整合並通過 check.py | T1, T2 | coordinator | done |

## T1
Write scope / shared resources: amounts.py only.
Task completion criteria: `subtotal(items)` 回傳 cents * quantity 的總和；空清單為 0。
Verify: worker direct checks；最終由 T3 receipt 驗證。

## T2
Write scope / shared resources: labels.py only.
Task completion criteria: `label(name)` strip 後回傳；blank 回傳 Guest。
Verify: worker direct checks；最終由 T3 receipt 驗證。

## T3
Write scope / shared resources: receipt.py、evidence/、tasks.md。
Task completion criteria: receipt 組合 label 與 subtotal，`python3 check.py` 成功。
Verify: task-harness run_check receipt state finished、returncode 0、sources stable。

## Checkpoint
Completed and accepted: T1、T2、T3；完整整合檢查通過。
Active worker handles and last observed state: amounts_worker、labels_worker terminal.
Unresolved work, decisions, and next ready tasks: none.
Side effects attempted and receipt / unknown outcome: evidence/T3-check-1.json（finished、returncode 0、sources stable）。
