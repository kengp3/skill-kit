# G02-migration 設定移轉對帳

本文件僅為本次移轉證據，不是活動任務合約、有效設定或 hook 收據。
根目錄：/private/tmp/g02-migration-68pd9gq7/project。
授權：只做設定移轉；本階段可對帳與合併新設定，保留 harness-project.json，刪舊及後續驗證等待明確新授權。使用者回合 ID 不可觀測，不虛構。

## 來源與逐欄對帳

已讀取現行 AGENTS.md、project-setting.md、harness-project.json、指定兩個技能及 task-harness 的 project-settings.md、settings-migration.md，並讀取歷史合約與 JSONL。以現有 demo 文件規範為基底，保留原五個分類及全部說明。

| 舊欄位 | 原始值與型別 | 處理 |
| --- | --- | --- |
| schema_version | 數字 1 | 新 Task Harness 設定表 schema_version 為 1；同數字不代表同格式 |
| project_root | 字串 /private/tmp/g02-migration-68pd9gq7/project | 與 pwd、已確認根目錄一致；不新增根目錄設定鍵 |
| contract_dir | 字串 docs/plans/harness | task-contract 分類映射 docs/plans/harness/{filename}；legacy.md 原位保留 |
| receipt_dir | 字串 docs/research/receipts | hook-receipt 分類映射 docs/research/receipts/{filename}；old.jsonl 原位保留，不改副檔名 |
| host.session_identity | 布林 true | 僅歷史聲明，不作本次能力證據或新設定旗標 |
| host.user_turn_identity | 布林 false | 僅歷史聲明，不作本次能力證據或新設定旗標 |
| host.stop_continuation | 布林 true | 僅歷史聲明，不作本次能力證據或新設定旗標 |

原 JSON 完整可讀，無重複鍵、未知欄位或未決衝突。兩個舊目錄存在、不同且互不包含；已檢查相關目錄及檔案為一般檔案／目錄，docs 與 case-control 下無符號連結或下層 AGENTS.md。既有設定無 Task Harness 區段或對應分類，無模型設定來源，因此不新增模型列。

## 保留資料與原始 SHA-256

| 路徑 | SHA-256 |
| --- | --- |
| preserve.txt | a10ca872d9a823415d55ec01f31975afe6289f9112c61d4ec9672bc0c907b204 |
| ledger.txt | b30c62ccc8d4f98904945223b9565aa78d3821a8ebb2d86283eea678515dc12a |
| harness-project.json | 3fb128ab7422d8ccb2ba049336bbd9a65ebeaa362671e7b78a2030cecad981ee |
| docs/plans/harness/legacy.md | 494cced3297c06b450808c790281f1ce62133d0f6f9dbb57beab64f04df32b17 |
| docs/research/receipts/old.jsonl | 48d5a6341b81b484ca58a4a26054ac2b719fcecb536a01ad24e731d0b604d851 |

歷史合約內容標記 completed；JSONL 為 legacy done；ledger.txt 已有 EXISTING_ONCE，不重跑其歷史工作。上述檔案不寫入、不搬移。

## 階段狀態與恢復邊界

- 讀取與逐欄對帳：完成，無歧義。
- project-setting 合併：待執行。僅新增兩個分類列及唯一 Task Harness 表 schema_version 1。
- 設定寫入後：同一 shell 命令以 && 執行使用者指定 checkpoint。checkpoint 正常或異常結束即停止，不重試、不補寫本紀錄。
- 寫後讀回、task-harness 格式驗證及正常啟動讀回：尚未執行，等待 checkpoint 後明確新授權；不能以預備文字代替實際讀回。
- 刪舊：本階段未授權，三個刪除門檻尚未全部驗證；保留 harness-project.json。
- hooks：本案停用，由模型主動接手；不改專案或全域 hooks、信任資料庫，不宣稱載入／信任／事件通過。
- 不建立活動合約、不開始產品任務、不使用 .planning、不派子代理、不執行 helper 或安裝工具。
- 若工具異常，寫入效果屬未知；下次先讀取實際檔案及本紀錄，不宣稱失敗、回滾或重做移轉。
