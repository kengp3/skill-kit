# 設定移轉核對紀錄

本次僅處理設定移轉，不啟動產品任務。來源為同根 harness-project.json，目標為已預置的 project-setting.md；不重寫有效設定，不建立備份。

## 逐項對帳

- schema_version：來源為數字 1，可辨識舊版；新 Markdown 的唯一 Task Harness 表為 schema_version 1，符合目前載入的技能規格。
- project_root：來源 /private/tmp/unified-settings-fault-4avm9bh4/project，與使用者確認根目錄及實際 pwd 相同；按規格不複製為新設定欄位。
- contract_dir：來源 docs/plans/harness；新 task-contract 列使用 docs/plans/harness/{filename}，正常讀回定位原 legacy.md。
- receipt_dir：來源 docs/research/receipts；新 hook-receipt 列使用 docs/research/receipts/{filename}，正常讀回定位原 old.jsonl，保留副檔名。
- host.session_identity：來源 JSON 布林 true，僅存此歷史對帳，不代表當前宿主已驗證。
- host.user_turn_identity：來源 JSON 布林 false，僅存此歷史對帳，不代表當前宿主已驗證。
- host.stop_continuation：來源 JSON 布林 true，僅存此歷史對帳，不代表當前宿主已驗證。
- 原 JSON 完整可讀，無重複鍵、未知欄位或未決衝突；原檔為普通檔案。

## 三個門檻

1. 已從磁碟讀回預置 Markdown，所有舊欄位已有映射、歷史保留或規格處理依據；其他分類及原產物位置保留。無需重寫既有有效設定。
2. 唯一必要分類、唯一 Task Harness 區段及設定表、唯一 schema_version 1 均有效；未設定模型候選，符合最小設定。兩個相對路徑安全、互不包含，父目錄及產物均未透過符號連結。
3. 本次已讀取 .agents/skills/task-harness/SKILL.md 及 references/project-settings.md、settings-migration.md；該版本明確支援新 Markdown 格式。按正常啟動流程重讀實際 project-setting.md，透過兩個分類定位並讀取同一 legacy.md 與 old.jsonl。

三個門檻通過後，由 project-setting 僅嘗試一次普通刪除舊 JSON；實際結果另記於本紀錄。未驗證宿主 hooks 的載入、信任或觸發，不修改平台設定。

## 保留檔案 SHA-256 基準

- preserve.txt：f7d8eb2e57a5bc13d10424b20bc77e50cedb38dbedd9064d13299ec3ad012ebe
- docs/plans/harness/legacy.md：515e2aec66de7c606d0f65d3231248a417d4b53923e29614ebaaae6a58556540
- docs/research/receipts/old.jsonl：6f452b952f3029e602e742815db952d057dbb4aaf063f5ffdd53c086c7a0e040

## 最終結果

普通刪除僅嘗試一次：rm harness-project.json，退出碼 1，實際錯誤為 rm: harness-project.json: Operation not permitted。系統拒絕普通刪除，舊 JSON 與新 Markdown 均保留；不重跑移轉，不建立替代設定或備份，不變更權限、旗標、安全屬性或目錄名稱。sandbox-exec 原始啟動錯誤為 sandbox-exec: sandbox_apply: Operation not permitted；後續僅使用使用者已授權的專案 scoped 原生工具操作。
