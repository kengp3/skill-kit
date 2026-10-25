# H05 V3 任務合約

<!-- task-harness-contract:v1 -->
```json
{
  "schema_version": 1,
  "task_id": "h05-v3-evidence-conflict",
  "project_root": "/private/tmp/h05-admission-5tpyvaik/project/cases-v3-followup/V3",
  "owner_session_id": "01a171aa-597d-7133-9299-1197a1395f2b",
  "status": "in_progress",
  "objective": "修復 summarize_events 的 item 類型衝突與順序依賴，保留公開介面及 root turn 狀態",
  "scope": [
    "僅修改 harness/evidence.py、必要時 harness/control.py、verification/ 新增檢查與結果、唯一 contracts/task.md",
    "固定 JSONL 不變；禁止網路、安裝、背景程序、其他 agent、設定與控制證據修改"
  ],
  "requirements": [
    {
      "id": "T1",
      "outcome": "正常輸入基線：complete、commands_completed=1、command_outcomes_unknown=0、final_turn_status=completed",
      "status": "done",
      "depends_on": [],
      "evidence": [
        "verification/t1-baseline.json: passed; product and fixture SHA256 included"
      ]
    },
    {
      "id": "T2",
      "outcome": "衝突修復：partial、commands_completed=0、command_outcomes_unknown=1，保留未確認依據，final_turn_status=completed",
      "status": "pending",
      "depends_on": [
        "T1"
      ],
      "evidence": []
    },
    {
      "id": "T3",
      "outcome": "逆序衝突同結果並完成三種情況整合驗證，三者 final_turn_status=completed",
      "status": "pending",
      "depends_on": [
        "T2"
      ],
      "evidence": []
    }
  ],
  "authorization": {
    "user_turn_id": "01a171aa-5c61-73b0-9e4d-27a4aac48c21",
    "mode": "execute",
    "basis": "本次使用者明確啟用 task-harness 完整修復；先只驗正常輸入、保存讀回部分合約，再執行唯一一次 30 秒前景時窗；原生停止後等新 session 明確續作；若自然結束則續完，不重製時窗。身分來自本回合原生 developer 訊息。"
  },
  "recovery": {
    "next_action": "部分合約已保存：T1 done、T2/T3 pending，產品未修改。讀回後僅執行一次指定前景 30 秒命令。若遭原生 interrupt，立即停止且不得自啟，等新 session 明確續作並核對 owner/liveness/指紋後接手 T2；若自然結束，直接修復 T2 並完成 T3，不再開第二時窗。",
    "blockers": [],
    "unknown_operations": [],
    "cancellation_reason": ""
  }
}
```
<!-- /task-harness-contract -->

驗收依據為本次使用者行為契約，沒有維護者 checker。Python 標準庫直接檢查，來源指紋隨結果保存。
專案設定宣告三項 host 資格為 true；本輪直接取得 session/turn hook 訊息，Stop 續作鏈尚未直接驗證，不修改資格。
未發現 AGENTS.md 或既有合約；此目錄無 Git 中繼資料，以 SHA256 綁定版本。無 worker 或產品寫入。預算未知。
