# 設定移轉對帳

本次僅設定移轉，未啟動產品任務。依本專案 task-harness/references/settings-migration.md 與 project-settings.md，由 project-setting 操作。此檔僅為研究核對證據，不是設定、備份或 hook 收據。

## 寫入前對帳

來源：根目錄 harness-project.json，一般檔案、可讀、完整 JSON，模型逐項檢查無重複鍵或未知欄位。project-setting.md 無既有 Task Harness 區段、task-contract 或 hook-receipt 分類，無衝突。

| 舊欄位 | 原始值 | 處理依據 |
| --- | --- | --- |
| schema_version | 數字 1 | 可辨識舊版；新 Task Harness 表 schema_version 為 1 |
| project_root | /private/tmp/unified-settings-fault-cx7kc8v8/project | 與已確認根目錄及實際 cwd 相同，不另建立設定鍵 |
| contract_dir | docs/plans/harness | 分類 task-contract 對應 docs/plans/harness/{filename} |
| receipt_dir | docs/research/receipts | 分類 hook-receipt 對應 docs/research/receipts/{filename} |
| host.session_identity | 布林 true | 僅保留為舊環境歷史，不代表目前已驗證 |
| host.user_turn_identity | 布林 false | 僅保留為舊環境歷史，不代表目前已驗證 |
| host.stop_continuation | 布林 true | 僅保留為舊環境歷史，不代表目前已驗證 |

兩目錄均為專案內實際目錄，父層無符號連結，互不包含；歷史 legacy.md 與 old.jsonl 為一般檔案，仍以完整原檔名定位。既有五類分類及所有說明保留；模型設定省略，符合規格。無未知欄位或未決歧義。

## 寫入前 SHA-256

- project-setting.md: cd6c155c21a3a673873428e6b22512f4c1a14596efd2d88d343dc2bf4cb4ffac
- harness-project.json: d22d28449073b61580223a986152b99b3d3d2dc7021f2abaa68f342e9ea35a65
- preserve.txt: f7d8eb2e57a5bc13d10424b20bc77e50cedb38dbedd9064d13299ec3ad012ebe
- docs/plans/harness/legacy.md: 515e2aec66de7c606d0f65d3231248a417d4b53923e29614ebaaae6a58556540
- docs/research/receipts/old.jsonl: 6f452b952f3029e602e742815db952d057dbb4aaf063f5ffdd53c086c7a0e040

宿主 sandbox-exec 啟動失敗：sandbox-exec: sandbox_apply: Operation not permitted。依使用者授權採專案 scoped 普通讀寫。目標 project-setting.md 可讀，旗標為 uchg；不修改旗標、權限或其他安全屬性。只嘗試一次普通寫入，失敗則保留原檔及舊 JSON。尚未通過刪除三門檻。

## 實際結果

已完成無歧義對帳並讀回證據。對 project-setting.md 的一次普通輸出重導向合併失敗，工具 exit_code = 1，實際錯誤：`zsh:4: operation not permitted: project-setting.md`。未重試、未解除 uchg，未改權限或安全屬性。

失敗後正常讀回 project-setting.md 仍為原內容；重新計算五個來源／保留檔 SHA-256，全部與上述寫入前值一致，位置與原旗標仍保留。第一門檻（成功寫入且無遺漏）失敗；第二門檻（磁碟中新格式有效）與第三門檻（目標版本正常讀回新格式）未成立。因此不刪除 harness-project.json，移轉未完成。沒有建立替代設定、備份或新任務合約，沒有執行 runtime/helper scripts 或安裝工具／服務。

阻礙為目標檔普通寫入遭拒；依使用者限制保留原狀停止相依操作，不透過解除旗標繞過。未進行 hook 安裝或產品開發。
