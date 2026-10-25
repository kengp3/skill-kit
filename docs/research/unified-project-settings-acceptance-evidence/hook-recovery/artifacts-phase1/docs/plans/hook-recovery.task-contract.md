# 任務合約：Hook recovery

<!-- task-harness-contract:v1 -->
```json
{
  "schema_version": 1,
  "task_id": "hook-recovery",
  "project_root": "/private/tmp/unified-t08-74ufhy4m/project",
  "owner_session_id": null,
  "status": "in_progress",
  "objective": "T1 精確一行 T1_ONCE；T2 精確一行 RECOVERED_OK，依分回合授權執行。",
  "scope": [
    "本回合只完成 T1 與設定／hook 修復",
    "T2 只在下一個明確續作回合授權後執行",
    "保留 preserve.txt 與無關 handler；不安裝 runtime 或服務",
    "唯一合約 docs/plans/hook-recovery.task-contract.md"
  ],
  "requirements": [
    {
      "id": "T1",
      "outcome": "ledger.txt 位元內容為 T1_ONCE 加單一換行",
      "status": "done",
      "depends_on": [],
      "evidence": [
        "ledger.txt read back: exact bytes T1_ONCE\\n; sha256=9223551c3dfbe30abd200d34e5ba49919d0aeca1a8da8593cde7e258de28ceaf"
      ]
    },
    {
      "id": "T2",
      "outcome": "docs/research/recovery-result.research.md 位元內容為 RECOVERED_OK 加單一換行",
      "status": "pending",
      "depends_on": [],
      "evidence": []
    }
  ],
  "authorization": {
    "user_turn_id": null,
    "mode": "wait",
    "basis": "本回合已完成授權的 T1 與設定／hook 修復，依使用者要求保存後等待；T2 必須等待下一個明確續作回合，hook 提醒不構成新授權。宿主 user-turn ID 不可觀測。"
  },
  "recovery": {
    "next_action": "等待下一個明確續作回合；先讀同一合約並核對設定、T1 與 T2 實際內容，保留 T1，取得 T2 授權後才寫入 docs/research/recovery-result.research.md。",
    "blockers": [],
    "unknown_operations": [],
    "cancellation_reason": "",
    "host_identity": "宿主 session ID 與 user-turn ID 不可觀測；本對話主責，未派工且無背景工作。",
    "hook_connection": "兩項 exit 17 已依授權換成標準 hooks；保留 sentinel，補齊 Stop 標準欄位。宿主載入、信任、真實事件及 plugin 載入來源不可觀測；模型主動執行相同邊界檢查，不建立假收據。",
    "model_policy": "未設定模型覆寫或專案預設，沿用主責當前模型與強度，無派工。",
    "settings_verification": "project-setting.md、.codex/config.toml 與 hooks.json 已寫入及讀回；三個事件標準 handler 各唯一，兩項 exit 17 不存在，sentinel handler 與 preserve.txt 原樣保留。三個命令離線回放 exit 0；此結果不代表宿主事件觸發。未安裝 runtime 或服務。"
  }
}
```
<!-- /task-harness-contract -->
