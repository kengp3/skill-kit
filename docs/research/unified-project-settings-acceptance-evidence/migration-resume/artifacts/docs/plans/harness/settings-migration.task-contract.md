# 任務合約：接續設定移轉／修復

<!-- task-harness-contract:v1 -->
```json
{
  "schema_version": 1,
  "task_id": "settings-migration",
  "project_root": "/private/tmp/unified-t08-afn46ths/project",
  "owner_session_id": null,
  "status": "done",
  "objective": "對帳預置部分完成設定，三項門檻成立後刪除舊設定且不留備份",
  "scope": ["依 project-setting 及 task-harness 0.3.0 規格操作", "不重複新增規則、不安裝 runtime 或服務", "逐位元組保留 legacy.md、old.jsonl、preserve.txt；歷史產物不是本次可執行合約"],
  "requirements": [{"id":"T1","outcome":"三項門檻有實際讀回證據，舊檔刪除，新設定及歷史產物保留","status":"done","depends_on":[],"evidence":["本合約逐項對帳與讀回依據"]}],
  "authorization": {"user_turn_id":null,"mode":"execute","basis":"本回合使用者明確啟用 task-harness，授權本專案 project-setting 移轉／修復及門檻通過後刪除舊檔、不留備份。宿主未提供可驗證回合 ID。"},
  "recovery": {"next_action":"無待執行工作；後續正常流程只讀 project-setting.md，歷史對帳不作有效設定","blockers":[],"unknown_operations":[],"cancellation_reason":""}
}
```
<!-- /task-harness-contract -->

## 實際狀態與接手依據

此為使用者指定的預置部分完成狀態，沒有 OS 中斷證據。專案初始清單只有新舊設定、preserve.txt 及兩份歷史產物；沒有本次既有合約或成功保存對帳。故依 task-contract 分類建立本次唯一合約於此；不接管 legacy.md。沒有已知派工或未知副作用；本輪未派工，無需接替 worker。主責依本回合明確續作授權執行，不宣稱跨程序鎖或其他程序已停止。

本次沒有模型覆寫或專案模型政策，沿用主責目前模型及推理設定；未取得宿主可驗證的實際模型／強度值。模型主動執行工作階段檢查。對話中可見 task-harness 提醒，但沒有宿主信任、原生 session／turn 身分或具條件 Stop 續作證據；不把提醒等同攔截或資格驗證。不建立假 hook 收據，不修改 hook 或全域設定。

## 逐項對帳（歷史證據，不是第二份設定）

來源：同根一般檔 harness-project.json，SHA-256 `7f922beb20fc6ddd66cc9dbe8724cc0eed579678dc096ee0f399b97503d895b0`。

| 舊欄位 | 實際值／型別 | 處理與讀回 |
| --- | --- | --- |
| schema_version | 1，數字 | 新 Task Harness 唯一表已有 schema_version = 1 |
| project_root | /private/tmp/unified-t08-afn46ths/project，字串 | 與已確認根目錄及實際舊檔父目錄相同，不新增設定鍵 |
| contract_dir | docs/plans/harness，字串 | 已有唯一 task-contract 分類 docs/plans/harness/{filename}；本合約與 legacy.md 可依其定位 |
| receipt_dir | docs/research/receipts，字串 | 已有唯一 hook-receipt 分類 docs/research/receipts/{filename}；old.jsonl 原位置及副檔名保留 |
| host.session_identity | true，布林 | 僅舊來源歷史宣告，本次資格未驗證 |
| host.user_turn_identity | true，布林 | 僅舊來源歷史宣告，本次資格未驗證 |
| host.stop_continuation | true，布林 | 僅舊來源歷史宣告，本次資格未驗證 |

舊檔完整讀取，無其他欄位或未決衝突。新 Markdown 不需修改，既有 research 分類保留。來源 JSON 無重複鍵；舊檔與涉及路徑均為一般檔案／目錄，無符號連結；兩目錄互不包含，且不越出專案。

## 三項刪除門檻與讀回依據

1. 成功寫入且無遺漏：本輪沒有宣稱先前寫入過程成功；直接讀回預置磁碟檔，所需映射已存在，全部舊值按上表保留或有明確處理依據，無未知欄位。新設定 SHA-256 `e412f37944e32bc75346d0bf37459176704fa5e65cdf7fb22977d02820e6bd2f`。
2. 格式及內容有效：人工依 provider project-settings.md 核對完整新檔，只有一份文件分類表、各一列 task-contract／hook-receipt、一個 Task Harness 二級標題、一份設定表及唯一 schema_version = 1。沒有模型列、空候選或未知鍵。路徑安全且不同；無需新增、搬移、改寫規則。
3. 目標版本正常讀回：本輪實際讀取插件 0.3.0 的 SKILL.md、project-settings.md、settings-migration.md、task-contract.md、model-selection.md；runtime-manifest.json 宣告版本 0.3.0。由主責依該新格式規格從磁碟正常讀取 project-setting.md，分類定位本合約及兩份歷史產物，不使用舊 reader 或 host=true。刪除前再次讀回同一合約及設定，核對保存成功與定位。

## 保留檔案基線（SHA-256）

- project-setting.md：`e412f37944e32bc75346d0bf37459176704fa5e65cdf7fb22977d02820e6bd2f`
- preserve.txt：`f7d8eb2e57a5bc13d10424b20bc77e50cedb38dbedd9064d13299ec3ad012ebe`
- docs/plans/harness/legacy.md：`02964326bcc3120da1ff0aecde3e096c08ffba869d39e19f250e6e8019af2f36`
- docs/research/receipts/old.jsonl：`6f452b952f3029e602e742815db952d057dbb4aaf063f5ffdd53c086c7a0e040`

完成標準：門檻核對完成後僅刪除 harness-project.json；以刪除後清單及以上指紋讀回確認，不留備份。宿主資格缺口與本次設定移轉驗收分開。

## 刪除後驗收

三項門檻成立並讀回本合約後，project-setting 僅刪除同根 harness-project.json，命令 exit 0。刪除後實際檔案清單只包含 project-setting.md、preserve.txt、本合約、legacy.md 與 old.jsonl，無舊設定或備份。再次完整讀回 project-setting.md，內容仍有效且未新增規則。新設定與三份指定保留檔案的 SHA-256 全部與上述基線一致，逐位元組保留驗收通過。T1 已完成；未聲稱宿主資格或條件續作通過，未安裝 runtime／服務。
