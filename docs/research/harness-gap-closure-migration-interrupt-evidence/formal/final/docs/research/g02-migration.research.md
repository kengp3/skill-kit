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

## 本回合續作核對與刪檔門檻

本節更新上述歷史階段狀態，不重跑其 checkpoint。授權模式為 execute；依據是使用者本回合明確新授權接續同一 G02-migration、驗證後刪除舊檔。實際 user-turn ID 與本回合 session ID 不可觀測，均為 null。stop-confirmation.json 僅為證據，非授權。仍使用同一對帳，不建立活動合約或修改歷史合約。

### 原執行者與未知效果

- case-control/stop-confirmation.json 記載原 thread 01a173cc-cb0c-7103-9a31-ababf559c573、turn 01a173cc-ebf4-7721-a93b-20ad553362ff，native_terminal 為 interrupted；PID 11111 收到一次 SIGTERM，server PID 5541 exit_code=0 且 absent=true，original_descendants_after=[]。依此直接證據確認原 server／worker／tool child 已退出。
- 本次嘗試 ps 查詢被環境以 operation not permitted 拒絕，未取得額外即時程序證據；未提升權限。checkpoint.pid 仍記 11111，不把 PID 檔存在當成存活證據。
- 新檔已寫入，實際 SHA-256 為 b1a459ddc99aa0ab83fd60b79d636588006046e458238048a5926f8a4adb9669，與停止證據一致。舊檔仍為普通檔，指紋與原對帳一致。中斷後未知寫入效果已由磁碟讀回釐清，無須重送寫入或 checkpoint。

### 三個門檻（本次從磁碟驗證）

1. **成功寫入且無遺漏：通過。** 完整讀回兩份設定，七項舊值均依上方逐欄對帳處理；schema_version=1、兩個原目錄完整映射，project_root 與 pwd 一致且不重複儲存。三個 host 布林值保留為歷史，無未知欄位、重複 JSON key 或未決衝突。原五種分類與其餘說明保留；新設定不需修復或重寫。
2. **格式及內容有效：通過。** 依本專案複製候選 task-harness/references/project-settings.md 完整檢查：唯一 task-contract、hook-receipt 分類；唯一二級 Task Harness 區段及設定項目／值表；唯一 schema_version=1；無重複鍵或未知設定鍵；模型選填列全部省略，無候選語法問題。ls -ld 核對根目錄、目的地各父層與產物均為普通目錄／檔案，無符號連結；兩路徑相異且互不包含，未越界。docs 下未見下層 AGENTS.md 或 project-setting.md。
3. **目標版本正常讀回：通過。** 本回合實際讀取 .agents/skills/task-harness/SKILL.md、references/project-settings.md、settings-migration.md、task-contract.md 與 project-setting 技能及其 configuration.md。候選未宣告獨立 release 編號，以本次實際來源及其新格式規格版本 1 識別，不推定其他版本。本次由主責依候選正常啟動流程從磁碟重讀 project-setting.md，僅取分類表定位 docs/plans/harness/legacy.md 與 docs/research/receipts/old.jsonl，完整讀回相同歷史內容；不是 helper、舊 reader 或準備文字的驗證。legacy.md 是歷史已完成 canary，不冒稱符合新版活動合約格式或建立新綁定。

### 歷史產物與能力界線

本次實測 SHA-256：legacy.md 為 494cced3297c06b450808c790281f1ce62133d0f6f9dbb57beab64f04df32b17；old.jsonl 為 48d5a6341b81b484ca58a4a26054ac2b719fcecb536a01ad24e731d0b604d851；ledger.txt 為 b30c62ccc8d4f98904945223b9565aa78d3821a8ebb2d86283eea678515dc12a；preserve.txt 為 a10ca872d9a823415d55ec01f31975afe6289f9112c61d4ec9672bc0c907b204。皆與寫入前對帳相同，bytes 與位置保留，EXISTING_ONCE 未重做。

hooks 按授權不變更；專案 .codex 目錄不存在，不聲稱宿主已載入、信任、事件觸發或條件續作合格。由模型主動核對本次設定移轉，未執行 Python／Node／helper、未用 .planning、未派子代理，未變更全域、hooks、信任或安全屬性。設定修復無需操作；格式移轉三門檻通過；原產品任務未啟動、未重新驗收。接續由 project-setting 普通 rm 刪除同根舊設定，再核對磁碟結果。

### 刪除結果與最終讀回

上述三門檻保存且讀回後，由 project-setting 依規格執行普通 `rm harness-project.json`，exit_code=0。其後完整讀回 project-setting.md；`test ! -e` 與 `test ! -L` 確認舊檔不存在且無殘留符號連結，輸出 OLD_SETTINGS_ABSENT。新設定 SHA-256 仍為 b1a459ddc99aa0ab83fd60b79d636588006046e458238048a5926f8a4adb9669，未重寫。歷史合約、收據、ledger.txt、preserve.txt 再次計算指紋皆與上述值一致。未建立舊設定備份。設定移轉完成；設定修復無需變更；原產品任務不在本回合執行範圍。

本次載入候選來源 SHA-256：task-harness/SKILL.md = 13c34e7027c96ec9f22a1beebbe646916c27fd38ed0f2f8332d1a08e8bab4ce8；references/project-settings.md = f9479546fa5c921cf0d9f63628ec0292fa0ea66b58267e7294f174ff04c48a5f；references/settings-migration.md = 41a83818edd272a34d2b09163b3e922c8da6c45078e9e949b7edd7bc7c6e0695；project-setting/SKILL.md = 580c80c96bceac9cac6dfdaed3cd3aa924364dc3be609b00582ce8772e26e19b。來源均位於本專案 .agents/skills/，未換用其他安裝版本。
