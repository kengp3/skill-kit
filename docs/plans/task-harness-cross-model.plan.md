# Task Harness 不同模型 review 與驗證

Objective：不同模型審查現在版本；以新的隔離 fixture 驗證、收集錯誤與重現證據；使用者最新指示將修正留待後續。
Scope：task-harness 本體、此次證據與報告；保留其他未提交工作，無安裝或發布。

| ID | 成果 | 依賴 | 狀態 | 驗收 |
| --- | --- | --- | --- | --- |
| M1 | gpt-6-astra 獨立指令審查 | none | done | findings 分類且有實際證據 |
| M2 | gpt-6-sol 隔離 plan/parallel/resume 測試 | none | done | 本輪受測版本、真實 artifacts、直接驗證與決策審查成立 |
| M3 | 錯誤清單、驗證結果及交接 | M1,M2 | done | 保留失敗與重現證據，不更改 skill，保存限制與覆蓋範圍 |

Authority：本檔；coordinator：root；由 coordinator 單獨更新。

Checkpoint：依最新指示完成錯誤收集，不進行 skill 修正。獨立審查沒有證實功能或授權缺陷；保存 1 項紀錄缺漏及 3 項證據／覆蓋缺口，原始 artifacts、hashes、實際 assertions、模型設定及 worker handles 均已封存。未宣稱真實時間重疊或完整狀態 trace 已驗證。
報告：../research/task-harness-cross-model-202610.research.md；evidence：../research/task-harness-cross-model-202610-evidence/。無活躍測試 workers，無外部操作。
