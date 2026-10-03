# Run: 完成 receipt helpers 與組裝

Scope / exclusions: 實作 `amounts.py`、`labels.py`、`receipt.py`；保留 `check.py`、`other-plan.md`、`user-note.txt` 與其他內容。
Materials and Definition of Done: `check.py` 通過；subtotal 加總 cents × quantity 且空清單為 0；label trim 後空白為 Guest；receipt 輸出 `<label>: <subtotal> cents`。
Authority: 本檔；coordinator: `/root/solmatrix_56_parallel`
Workspace / baseline: `/private/tmp/task-harness-solmatrix-mc_zeld9/sol56/parallel`；三個目標函式目前皆為 `NotImplementedError`。
Execution limits / permissions: 恰好兩個原生 subagents；worker 不得再委派；無網路、安裝、聊天或存取周邊 fixture。

| ID | Outcome | Depends on | Owner / handle | State |
| --- | --- | --- | --- | --- |
| T1 | 實作 `amounts.subtotal(items)` | none | `/root/solmatrix_56_parallel/amounts_worker` | done |
| T2 | 實作 `labels.label(name)` | none | `/root/solmatrix_56_parallel/labels_worker` | done |
| T3 | 整合 `receipt.receipt(name, items)` 並執行整合檢查 | T1, T2 | coordinator | done |

## T1
Write scope / shared resources: 僅 `amounts.py` 與 `evidence/amounts-worker.txt`。
Acceptance: `subtotal([(125,2),(50,3)]) == 400`；`subtotal([]) == 0`。
Verify: worker direct check；coordinator 最終執行 `python3 check.py`。

## T2
Write scope / shared resources: 僅 `labels.py` 與 `evidence/labels-worker.txt`。
Acceptance: `label("  Alice  ") == "Alice"`；`label(" ") == "Guest"`。
Verify: worker direct check；coordinator 最終執行 `python3 check.py`。

## T3
Write scope / shared resources: `receipt.py`、`tasks.md`、`evidence/` 協調證據。
Acceptance: receipt 使用兩個 helper 組裝指定格式，且現有 `check.py` 全部通過。
Verify: `python3 check.py` 顯示 `PASS receipt integration`。

## Checkpoint
Completed and accepted: T1、T2 direct checks 通過；T3 整合完成，`python3 check.py` exit 0 並輸出 `PASS receipt integration`。
Active worker handles and last observed state: 兩個 worker 已回傳完成；spawn 後的即時狀態詳見 `evidence/overlap.json`。
Unresolved work, decisions, and next ready tasks: none
Side effects attempted and receipt / unknown outcome: 兩個 worker 均成功 spawn；立即觀察到 coordinator 與兩個指定 worker，未觀察到額外重疊 worker；所有檔案寫入及驗證結果均已確認。
