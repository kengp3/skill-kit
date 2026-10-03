# Run: 完成 receipt 計算與標籤整合

Scope / exclusions: 僅修改 `amounts.py`、`labels.py`、`receipt.py`、本 task state 與 `evidence/`；其餘 fixture 檔唯讀。
Materials and Definition of Done: `check.py` 所有 assertions 通過，並保存穩定來源的 receipt。
Authority: `tasks.md`
Current coordinator: `/root/remfix5_56_parallel`
Workspace / baseline: `/private/tmp/task-harness-remfix5-arjbvmfd/sol56/parallel`; 三個實作檔皆為 `NotImplementedError`。
Available tools / execution limits / permissions: 兩名原生 workers；無網路、安裝、外部動作；workers 不得再委派。

| ID | Outcome | Depends on | Owner / handle | State |
| --- | --- | --- | --- | --- |
| T1 | `subtotal` 計算 cents × quantity 總和，空清單為 0 | none | `/root/remfix5_56_parallel/amounts_worker` | done |
| T2 | `label` 去除前後空白，空白名稱為 Guest | none | `/root/remfix5_56_parallel/labels_worker` | done |
| T3 | `receipt` 整合並通過 `check.py` | T1, T2 | coordinator | done |

## Checkpoint
Completed and accepted: T1 via `evidence/T1-check-1.json`；T2 via `evidence/T2-check-1.json`；T3 via `evidence/T3-check-1.json`（皆 finished, returncode 0, sources stable；integration stdout `PASS receipt integration`）。
Active worker handles and last observed state: T1/T2 workers completed and returned；coordinator completed T3。
Unresolved work, decisions, and next ready tasks: none。
Side effects attempted and receipt / unknown outcome: none
