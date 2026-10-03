# Run: 實作收據計算與標籤整合

Scope / exclusions: 僅修改 `amounts.py`、`labels.py`、`receipt.py`、`tasks.md` 與 `evidence/`；保留唯讀材料。
Materials and Definition of Done: `project-setting.md`、`check.py`；`python3 check.py` 輸出 `PASS receipt integration`。
Authority: 本檔；coordinator: `/root/remfix3_56_parallel`
Workspace / baseline: `/private/tmp/task-harness-remfix3-1nis2bc6/sol56/parallel`；三個實作檔目前皆為 `NotImplementedError`。
Available tools / execution limits / permissions: 兩名原生 workers，互斥檔案 scope；無網路、安裝或外部動作；不可再委派。

| ID | Outcome | Depends on | Owner / handle | State |
| --- | --- | --- | --- | --- |
| T1 | `amounts.py` 實作 `subtotal` | none | `/root/remfix3_56_parallel/amounts_worker` | done |
| T2 | `labels.py` 實作 `label` | none | `/root/remfix3_56_parallel/labels_worker` | done |
| T3 | `receipt.py` 整合並通過 checker | T1, T2 | coordinator | done |

## T1
Write scope / shared resources: 僅 `amounts.py`。
Acceptance: `subtotal([(125,2),(50,3)]) == 400` 且空清單為 0。
Verify: worker 執行最小直接檢查；coordinator 最終執行 `python3 check.py`。

## T2
Write scope / shared resources: 僅 `labels.py`。
Acceptance: 去除首尾空白；blank 回傳 `Guest`。
Verify: worker 執行最小直接檢查；coordinator 最終執行 `python3 check.py`。

## T3
Write scope / shared resources: `receipt.py`、`tasks.md`、`evidence/`。
Acceptance: 組合 label 與 subtotal，格式為 `<label>: <subtotal> cents`；完整 checker 通過。
Verify: `python3 check.py` 預期輸出 `PASS receipt integration`。
Attempt / last update: T1/T2 worker checks exit 0，coordinator 已核對檔案 SHA-256；T3 整合與完整 checker 已完成。
Evidence: `python3 -B check.py` exit 0，輸出 `PASS receipt integration`；詳見 `evidence/integration.txt`。

## Checkpoint
Completed and accepted: T1、T2、T3；整體 Definition of Done 完成。
Active worker handles and last observed state: 第二次 spawn 後立即呼叫 native `list_agents`；`amounts_worker` 與 `labels_worker` 均為 `running`；目前皆已完成回報。
Unresolved work, decisions, and next ready tasks: 無。
Side effects attempted and receipt / unknown outcome: T1/T2 workers 完成；T3 checker exit 0；無 unknown outcome。
