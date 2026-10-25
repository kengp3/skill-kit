# 任務合約：basic-result

<!-- task-harness-contract:v1 -->
```json
{
  "schema_version": 1,
  "task_id": "basic-result",
  "project_root": "/private/tmp/unified-t02-B/project",
  "owner_session_id": null,
  "status": "done",
  "objective": "產出 docs/research/basic-result.research.md，僅一行 BASIC_TASK_OK，讀回驗收並保留 preserve.txt",
  "scope": ["初始化必要 project-setting 設定與本合約", "建立指定成果並讀回驗收", "保留 preserve.txt", "不安裝 runtime、服務或 helper scripts"],
  "requirements": [{"id": "T1", "outcome": "指定成果精確一行且 preserve.txt 保持原內容", "status": "done", "depends_on": [], "evidence": ["讀回為 BASIC_TASK_OK；cmp 精確比對成功，wc 為 1 行 14 bytes", "成果 SHA-256: 8dd1530cee450065ded339b4c4d56c8a1160d11f4c4cf37ef753ab9cf77794aa", "preserve.txt cmp 基線成功，1 行 22 bytes，SHA-256: f7d8eb2e57a5bc13d10424b20bc77e50cedb38dbedd9064d13299ec3ad012ebe", "project-setting.md 已讀回；必要分類唯一、schema_version 為 1"] }],
  "authorization": {
    "user_turn_id": "unavailable",
    "mode": "execute",
    "basis": "本回合使用者明確要求使用已安裝 task-harness 完成產出、讀回並允許必要初始化；unavailable 表示宿主未提供可觀測 turn ID，非真實識別值"
  },
  "recovery": {"next_action": "無待辦；若續作，先核對本合約與成果指紋", "blockers": [], "unknown_operations": [], "cancellation_reason": ""}
}
```
<!-- /task-harness-contract -->

## 約定與驗收依據

依使用者明確指定，成果應等於 `BASIC_TASK_OK` 加一個換行。preserve.txt 基線為 `KEEP_EXISTING_CONTENT` 加一個換行（22 bytes）。採 shell 原生讀回、cmp、wc 與 SHA-256 取證；此任務無程式碼或既有測試套件。

## 恢復與變更依據

本對話主責為 /root；宿主 session／user-turn ID 不可取得，owner 保持 null，不宣稱跨對話綁定或原子鎖。依使用者環境說明無 hooks，採模型主動檢查；不產生虛假 hook 收據，不宣稱宿主載入、信任或自動攔截合格。沿用主責目前模型與強度，未要求覆寫；宿主精確模型版本與強度無可驗證證據。無背景工作或其他寫入者。預設 sandbox shell 啟動失敗，改用經核准的本地命令執行；未安裝任何工具。
