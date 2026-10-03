# Run: receipt 整合
Objective: 兩名原生 workers 完成 subtotal 與 label，coordinator 整合 receipt。
Scope / exclusions: 僅 amounts.py、labels.py、receipt.py、tasks.md、evidence/；其餘輸入唯讀。
Materials and Definition of Done: subtotal cents*quantity、空清單 0；label strip、blank Guest；receipt 格式與 check.py 通過。
Authority: tasks.md
Current coordinator: /root/followup2_61_parallel
Workspace / baseline: /private/tmp/harness-followup2-465i825d/sol61/parallel；原始三個 stub；無 Git revision。
Available tools / execution limits / permissions: 本地 shell/Python3、恰好兩名 native workers；無網路、安裝、外部影響；workers 不再委派。

| ID | Outcome | Depends on | Owner / handle | Task attempt | State | Acceptance receipt |
| --- | --- | --- | --- | --- | --- | --- |
| T1 | subtotal | none | /root/followup2_61_parallel/amounts | 1 | done | evidence/T1-check-1.json |
| T2 | label | none | /root/followup2_61_parallel/labels | 1 | done | evidence/T2-check-1.json |
| T3 | receipt 整合 | T1,T2 | /root/followup2_61_parallel | 1 | done | evidence/T3-check-1.json |

## T1
Write scope: amounts.py、evidence/T1-*；subtotal(items) 接收 (cents,quantity)。
Verify: mixed items 400、empty 0；worker 以 run_check.py 留 receipt。
Check attempts: T1-check attempt 1, evidence/T1-check-1.json
## T2
Write scope: labels.py、evidence/T2-*；label(name) 去空白，空字串 Guest。
Verify: padded Alice、blank；worker 以 run_check.py 留 receipt。
Check attempts: T2-check attempt 1, evidence/T2-check-1.json
## T3
Write scope: receipt.py、evidence/T3-*；receipt(name,items) -> '<label>: <subtotal> cents'。
Verify: run_check.py 執行 python3 check.py 並 fingerprint 三個產品檔與 check.py。
Check attempts: T3-check attempt 1, evidence/T3-check-1.json
## Checkpoint
Completed and accepted: T1,T2,T3；個別與整合 receipts 均已讀取，fingerprints 與當前檔案一致
Active worker handles: none；兩個歷史 handles 已回傳 final
Unresolved work: none；Definition of Done 已通過。
Side effects: 僅本地可逆檔案寫入。
