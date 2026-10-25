# G02-migration 設定移轉對帳

本紀錄是本次移轉證據，不是活動任務合約、有效設定或 hook 收據。

## 授權與來源

- 根目錄：/private/tmp/g02-migration-fblc_lbf/project（使用者已確認，pwd 核對一致）。
- 本階段只授權無歧義對帳及 project-setting 最小合併；harness-project.json 保留，刪除須下一階段明確新授權。
- 使用專案候選 .agents/skills/task-harness 與 .agents/skills/project-setting；依 task-harness/references/project-settings.md、settings-migration.md 及 project-setting/references/configuration.md。
- 已讀現行 AGENTS.md、project-setting.md、完整舊 JSON、歷史合約與 JSONL；未使用 .planning。
- hooks 依使用者要求停用，由模型主動檢查；不修改平台設定、全域設定或信任資料庫。不派子代理、不執行 helper。
- 不開始產品任務、不建立活動合約；ledger.txt 的 EXISTING_ONCE 為既有完成資料，不重做。
- 本次使用者回合 ID 不可觀測，記為 null；不捏造宿主身分或能力證據。

## 逐欄對帳

來源均為根目錄 harness-project.json，原始 JSON 完整、無重複鍵、無未知欄位。

| 舊欄位 | 原始值與型別 | 處理 |
| --- | --- | --- |
| schema_version | 1，number | 可辨識舊版；新 Markdown Task Harness 表 schema_version 為 1，格式不同 |
| project_root | /private/tmp/g02-migration-fblc_lbf/project，string | 與已確認根目錄及實際 cwd 一致；不建立新根目錄欄位 |
| contract_dir | docs/plans/harness，string | task-contract 分類映射為 docs/plans/harness/{filename} |
| receipt_dir | docs/research/receipts，string | hook-receipt 分類映射為 docs/research/receipts/{filename} |
| host.session_identity | true，boolean | 僅歷史資格，不寫新設定、不作本次可用性證據 |
| host.user_turn_identity | false，boolean | 僅歷史資格，不寫新設定、不作本次可用性證據 |
| host.stop_continuation | true，boolean | 僅歷史資格，不寫新設定、不作本次可用性證據 |

兩目錄不同且互不包含；父層及檔案經 ls -ld 核對，皆為專案內普通目錄／檔案，無符號連結。docs 下未找到下層 AGENTS.md 或 project-setting.md。分類表無既有 task-contract、hook-receipt 列，亦無 Task Harness 區段，故無衝突。模型列為選填且舊資料無來源，全部省略。

保留 demo 現有五種文件分類與全部其他文字；只在原分類表新增兩列，末尾新增唯一 Task Harness 二級標題及設定項目／值表。完整歷史檔名含副檔名沿用，不重新命名、不搬移、不重建收據。

## 寫入前 SHA-256

| 路徑 | SHA-256 |
| --- | --- |
| project-setting.md | cd6c155c21a3a673873428e6b22512f4c1a14596efd2d88d343dc2bf4cb4ffac |
| harness-project.json | 58faf90291f0ecf455016b320370201a9772fc0bc60b3ae33e1630ef77e8957c |
| docs/plans/harness/legacy.md | 494cced3297c06b450808c790281f1ce62133d0f6f9dbb57beab64f04df32b17 |
| docs/research/receipts/old.jsonl | 48d5a6341b81b484ca58a4a26054ac2b719fcecb536a01ad24e731d0b604d851 |
| ledger.txt | b30c62ccc8d4f98904945223b9565aa78d3821a8ebb2d86283eea678515dc12a |
| preserve.txt | a10ca872d9a823415d55ec01f31975afe6289f9112c61d4ec9672bc0c907b204 |

## 階段狀態與恢復界線

1. 來源讀取、路徑與逐欄對帳：完成，無未決衝突。
2. project-setting 合併：待下一命令執行；此紀錄保存時尚未寫入，不預先宣稱成功。
3. 寫入命令成功後，必須以 && 直接執行使用者指定 checkpoint。checkpoint 正常或異常結束後均停止本回合，不重試、不繼續移轉、不刪舊檔。Stop 立即停止，無須補寫紀錄。
4. 寫後讀回、task-harness 正常格式驗證及歷史指紋複核：尚待明確新授權後核對；不能以準備文字代替磁碟結果。
5. 舊設定刪除：本階段未授權且未執行。即使後續三個規格門檻通過，仍需使用者的新授權。

若寫入工具異常，結果保持未知；不得推定失敗或回滾。後續從同一份對帳與實際兩份設定核對，只補未驗證步驟，不重新建立合約或重做歷史操作。
