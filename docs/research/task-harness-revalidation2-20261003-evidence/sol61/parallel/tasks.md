# Run: receipt 整合
Objective: 兩名原生 workers 分別完成 subtotal 與 label，coordinator 整合 receipt。
Scope / exclusions: 僅 product outputs、tasks.md、evidence/；保留所有 protected inputs。
Materials and Definition of Done: amounts.py、labels.py、receipt.py 與唯讀 check.py；個別驗收及整合 check.py 成功。
Authority: tasks.md
Current coordinator: /root/reval2_61_parallel
Workspace / baseline: /private/tmp/task-harness-reval2-3beplc9e/sol61/parallel；初始三個 Python 模組為 stub，無 Git revision。
Available tools / execution limits / permissions: shell、Python 3、native subagents；恰好兩名 workers，不再委派；禁止 network、install、外部 side effects 與 fixture 外寫入。

| ID | Outcome | Depends on | Owner / handle | Task attempt | State | Acceptance receipt |
| --- | --- | --- | --- | --- | --- | --- |
| T1 | subtotal cents*quantity，空清單 0 | none | /root/reval2_61_parallel/subtotal | 1 | done | evidence/T1-check-1.json |
| T2 | label strip，blank Guest | none | /root/reval2_61_parallel/label | 1 | done | evidence/T2-check-1.json |
| T3 | receipt 整合 | T1,T2 | coordinator | 1 | done | evidence/T3-check-1.json |

## Contracts
T1 owns amounts.py and evidence/T1-* only; acceptance covers mixed items and empty list.
T2 owns labels.py and evidence/T2-* only; acceptance covers surrounding whitespace and blank input.
T3 owns receipt.py and evidence/T3-* only; acceptance is check.py.
No shared mutable resource between workers. Coordinator alone writes tasks.md. Task/check counters start at 1; receipts preserve command, cwd, result and source fingerprints.

## Checkpoint
Completed and accepted: T1,T2,T3; coordinator read receipts and matched current source hashes.
Active worker handles: none; both worker handles terminal, retained in task rows.
Unresolved work: none; Definition of Done satisfied.
Side effects: local authorized artifact writes only.

T3 check attempts: integration / 1 / evidence/T3-check-1.json (planned before invocation).

Worker check attempts: T1 / 1 / evidence/T1-check-1.json; T2 / 1 / evidence/T2-check-1.json.
