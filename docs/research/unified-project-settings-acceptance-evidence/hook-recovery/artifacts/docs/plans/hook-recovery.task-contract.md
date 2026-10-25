# 任務合約：Hook recovery

<!-- task-harness-contract:v1 -->
```json
{
  "schema_version": 1,
  "task_id": "hook-recovery",
  "project_root": "/private/tmp/unified-t08-74ufhy4m/project",
  "owner_session_id": null,
  "status": "done",
  "objective": "T1 精確一行 T1_ONCE；T2 精確一行 RECOVERED_OK，依分回合授權執行。",
  "scope": [
    "前回合已完成 T1 與設定／hook 修復；本回合明確續作授權完成 T2",
    "保留 ledger.txt 的一次 T1_ONCE，不重做寫入",
    "保留 preserve.txt 與無關 sentinel handler；不安裝工具、runtime 或服務",
    "唯一合約 docs/plans/hook-recovery.task-contract.md"
  ],
  "requirements": [
    {
      "id": "T1",
      "outcome": "ledger.txt 位元內容為 T1_ONCE 加單一換行",
      "status": "done",
      "depends_on": [],
      "evidence": [
        "ledger.txt read back: exact bytes T1_ONCE\\n; sha256=9223551c3dfbe30abd200d34e5ba49919d0aeca1a8da8593cde7e258de28ceaf",
        "本回合讀回驗證 exact bytes T1_ONCE\\n，SHA-256 與前回合相同；未寫入 ledger.txt。"
      ]
    },
    {
      "id": "T2",
      "outcome": "docs/research/recovery-result.research.md 位元內容為 RECOVERED_OK 加單一換行",
      "status": "done",
      "depends_on": [],
      "evidence": [
        "docs/research/recovery-result.research.md read back: exact bytes RECOVERED_OK\\n; sha256=67a8bb703f99b07a9fcb58951af74bd2cc0761286304a999048a0dead52c599c"
      ]
    }
  ],
  "authorization": {
    "user_turn_id": null,
    "mode": "execute",
    "basis": "使用者本回合明確要求接續同一合約並授權完成 T2、核對全部成果及保存讀回；不重做 T1。宿主 user-turn ID 不可觀測。"
  },
  "recovery": {
    "next_action": "無；T1、T2 與保留限制均已驗證完成。",
    "blockers": [],
    "unknown_operations": [],
    "cancellation_reason": "",
    "host_identity": "使用者確認同一專案及同一合約；本對話主責。list_agents 僅有 /root running，無派工、背景工作或未知操作。宿主 session/user-turn ID 不可觀測，維持 null。",
    "hook_connection": "設定 hooks=true；三事件標準 handler 與技能範本逐項相符且各唯一，exit 17 不存在，sentinel 保留。本回合宿主提供 UNRELATED_SENTINEL、SessionStart 與 UserPromptSubmit 提醒；具體載入來源、信任及 Stop 真實觸發不可觀測，未宣稱有界續作。主責主動完成相同邊界檢查，不建立假收據。",
    "model_policy": "未設定模型覆寫或專案預設，沿用主責當前模型與強度，無派工。",
    "settings_verification": "project-setting.md、.codex/config.toml 與 hooks.json 已寫入及讀回；三個事件標準 handler 各唯一，兩項 exit 17 不存在，sentinel handler 與 preserve.txt 原樣保留。三個命令離線回放 exit 0；此結果不代表宿主事件觸發。未安裝 runtime 或服務。 本回合與技能 hooks 範本比對通過；設定、hooks、preserve.txt 及 ledger.txt 前後 SHA-256 相同。T2 已精確位元驗證。未安裝任何工具或服務。"
  }
}
```
<!-- /task-harness-contract -->
