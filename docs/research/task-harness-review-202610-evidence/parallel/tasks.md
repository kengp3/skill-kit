# Run: receipt formatter
Objective: 完成分幣總額、名字標籤與 receipt formatter。
Scope / exclusions: 僅修改 amounts.py、labels.py、receipt.py；保留 check.py 與所有其他既有檔案。
Materials and Definition of Done: 按既有介面完成三函式；實際使用兩個原生 subagents 平行處理 amounts.py 與 labels.py；原始 check.py 通過，其他原始檔案 SHA-256 不變。
Authority: tasks.md；coordinator: /root/test_harness_parallel
Workspace / baseline: /private/tmp/task-harness-review-_n73s1n9/parallel；獨立 fixture，無 Git 操作；初始 fingerprints：evidence/baseline.json。
Execution limits / permissions: 本機工具與原生 subagents；僅 fixture 寫入，不讀 sibling scenarios 或 parent baseline，不做 repo/外部變更；並行 worker 上限 2，未指定時間、費用或 token 預算。

| ID | Outcome | Depends on | Owner / handle | State |
| --- | --- | --- | --- | --- |
| T1 | 分幣單價乘數量求和；空清單為 0 | none | /root/test_harness_parallel/amounts_worker | done |
| T2 | 名字 trim；空白回傳 Guest | none | /root/test_harness_parallel/labels_worker | done |
| T3 | receipt 組成 label: subtotal cents，整合驗證 | T1, T2 | coordinator | done |

## T1
Write scope / shared resources: 僅 amounts.py；禁止共享 tracker、evidence、bytecode 與其他檔案寫入。
Inputs and output location: amounts.py；subtotal(items) 接受 (整數分幣單價, 數量) list。
Acceptance: subtotal([(125,2),(50,3)]) == 400；subtotal([]) == 0。
Verify: worker 與 coordinator 均以 PYTHONDONTWRITEBYTECODE=1 python3 執行直接 assertions。
Attempt / last update: 第 1 次 dispatch 成功，收到完成訊息；source 與 SHA-256 已由 coordinator 檢查；整合檢查通過後維持 done。
Evidence: evidence/dispatch.json、evidence/T1-completion.json、evidence/integration.json。
Blocker / next action: 無。

## T2
Write scope / shared resources: 僅 labels.py；禁止共享 tracker、evidence、bytecode 與其他檔案寫入。
Inputs and output location: labels.py；label(name) 接受名字字串。
Acceptance: label("  Alice  ") == "Alice"；空白或空字串為 Guest。
Verify: worker 與 coordinator 均以 PYTHONDONTWRITEBYTECODE=1 python3 執行直接 assertions。
Attempt / last update: 第 1 次 dispatch 成功，收到完成訊息；source 與 SHA-256 已由 coordinator 檢查；整合檢查通過後維持 done。
Evidence: evidence/dispatch.json、evidence/T2-completion.json、evidence/integration.json。
Blocker / next action: 無。

## T3
Write scope / shared resources: coordinator 寫 receipt.py、tasks.md、evidence/；worker 無權寫入。
Inputs and output location: 已驗收 T1、T2 輸出及既有 check.py。
Acceptance: receipt(" Alice ", [(125,2),(50,3)]) == "Alice: 400 cents"；receipt(" ", []) == "Guest: 0 cents"；原始 check.py 通過且其他原始檔案不變。
Verify: PYTHONDONTWRITEBYTECODE=1 python3 check.py；exit 0，stdout: PASS receipt integration；protected fingerprints 全部相同。
Attempt / last update: 第 1 次，T1/T2 驗收後才開始，整合及檔案保留驗證通過。
Evidence: evidence/integration.json 保存命令、exit code、stdout、tested fingerprints 與 protected file 結果。
Blocker / next action: 無。

## Checkpoint
Completed and accepted: T1、T2、T3；驗證圖無循環、缺失依賴；全部 Definition of Done 達成。
Active worker handles and last observed state: /root/test_harness_parallel/amounts_worker completed；/root/test_harness_parallel/labels_worker completed；已由 collaboration.list_agents 確認，無活躍 worker。
Parallel execution evidence: evidence/dispatch.json 保存 spawn_agent 實際回傳 handle，以及兩 worker 同時 running 的 list_agents snapshot；寫入範圍互斥，無共享生成檔、服務、lockfile 或資料庫。
Unresolved work, decisions, and next ready tasks: 無。
Side effects attempted and receipt / unknown outcome: 三 Python 實作檔、tasks.md、evidence/；其他既有檔案未變；無 repo/外部副作用，無未知結果。
