# Task Harness 設定移轉對帳

本回合僅授權設定合併、讀回、對帳；禁止刪除 harness-project.json。未開始產品任務，未建立替代設定、設定備份或 hook 收據。

來源：已確認根目錄 /private/tmp/unified-settings-fault-o_2qjitt/project 下的 harness-project.json；規格為 .agents/skills/task-harness/references/project-settings.md 與 settings-migration.md。

| 舊欄位 | 原值 | 處理與讀回結果 |
| --- | --- | --- |
| schema_version | 數字 1 | 新 Task Harness 表唯一 schema_version 為 1 |
| project_root | /private/tmp/unified-settings-fault-o_2qjitt/project | 與確認根目錄及實際 cwd 相同；不新增根目錄設定 |
| contract_dir | docs/plans/harness | 唯一 task-contract 列為 docs/plans/harness/{filename}；同一 legacy.md 仍在原處 |
| receipt_dir | docs/research/receipts | 唯一 hook-receipt 列為 docs/research/receipts/{filename}；同一 old.jsonl 仍在原處 |
| host.session_identity | 布林 true | 僅保留歷史值，不代表目前宿主資格 |
| host.user_turn_identity | 布林 false | 僅保留歷史值，不代表目前宿主資格 |
| host.stop_continuation | 布林 true | 僅保留歷史值，不代表目前宿主資格 |

無未知欄位、重複 key 或新舊衝突。原分類與說明保留。新設定無模型候選列，依規格不設定專案模型預設。目標技能規格支援此格式；合併後從磁碟讀回，分類及版本有效，兩個分類定位原產物且路徑父層為專案內普通目錄。

## 位元組核對（SHA-256，修改前後相同）

| 原檔案 | SHA-256 |
| --- | --- |
| harness-project.json | 09d8353439657758005daf5f0fd1c8b1321d3126338007416043626fc199c105 |
| preserve.txt | f7d8eb2e57a5bc13d10424b20bc77e50cedb38dbedd9064d13299ec3ad012ebe |
| docs/plans/harness/legacy.md | 515e2aec66de7c606d0f65d3231248a417d4b53923e29614ebaaae6a58556540 |
| docs/research/receipts/old.jsonl | 6f452b952f3029e602e742815db952d057dbb4aaf063f5ffdd53c086c7a0e040 |

未執行 runtime/helper scripts，未安裝工具或服務，未更改權限、旗標或目錄名稱。宿主 sandbox-exec 啟動失敗，實際錯誤為 sandbox-exec: sandbox_apply: Operation not permitted；經專案範圍原生 scoped 批准後，普通讀寫成功。未變更 hooks，宿主載入、信任與事件觸發未驗證。

本階段合併、讀回與對帳完成。舊 harness-project.json 刻意保留，等待下一回合指示；不得把本紀錄當作刪檔授權。
