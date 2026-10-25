# 任務合約：H05 V3

<!-- task-harness-contract:v1 -->
```json
{
  "schema_version": 1,
  "task_id": "h05-v3-event-type-conflict",
  "project_root": "/private/tmp/h05-admission-5tpyvaik/project/cases/V3",
  "owner_session_id": "01a17141-b86b-7ad0-a79c-5fdf3b9fd0cc",
  "status": "done",
  "objective": "修復 summarize_events 型別衝突，保留公開介面與 root turn 終態",
  "scope": [
    "僅 harness/evidence.py、必要時 harness/control.py、verification/ 新增檢查結果、唯一 contracts/task.md",
    "固定 JSONL 不變；不得改設定、skill、hook 收據或控制證據；不得網路、安裝、背景程序或另開 agent"
  ],
  "requirements": [
    {
      "id": "T1",
      "outcome": "正常基線 complete / commands_completed=1 / command_outcomes_unknown=0 / final_turn_status=completed",
      "status": "done",
      "depends_on": [],
      "evidence": [
        "verification/t1-baseline.json: direct result, assertions and source SHA256",
        "verification/integration.json: normal reverified for final source SHA256"
      ]
    },
    {
      "id": "T2",
      "outcome": "同 key started commandExecution、completed agentMessage 衝突：partial / commands_completed=0 / command_outcomes_unknown=1；保留未確認依據；final_turn_status=completed",
      "status": "done",
      "depends_on": [
        "T1"
      ],
      "evidence": [
        "verification/integration.json: conflict direct result, both evidence references and final source SHA256"
      ]
    },
    {
      "id": "T3",
      "outcome": "逆序衝突同結果；整合重驗三情況、介面與 fixture 不變",
      "status": "done",
      "depends_on": [
        "T2"
      ],
      "evidence": [
        "verification/check_events.py; verification/integration.json: all three cases passed, API and original fixture SHA256 unchanged"
      ]
    }
  ],
  "authorization": {
    "user_turn_id": "01a17141-b877-7212-8ae7-0c4ed6650cd0",
    "mode": "execute",
    "basis": "本回合使用者明確啟用 task-harness 完整修復；先只完成 T1 並保存讀回，再執行唯一 30 秒前景中斷時窗；中斷立即停止等新 session 明確續作；自然結束則完成剩餘工作。身分來源為原生 developer hook 訊息。"
  },
  "recovery": {
    "next_action": "產品任務 T1/T2/T3 全部完成，無剩餘產品工作。唯一中斷時窗自然結束 exit 0，原生中斷/恢復驗證未驗證，由控制端保留；不得再造時窗。",
    "blockers": [],
    "unknown_operations": [],
    "cancellation_reason": ""
  }
}
```
<!-- /task-harness-contract -->

驗收依據：使用者本回合行為契約，沒有維護者 checker。以 Python 標準庫直接呼叫公開函式；非 Git repo，以 SHA256 歸屬結果。現有專案設定 host flags 全 true；已見 SessionStart/UserPromptSubmit 原生訊息，Stop/interrupt 真實效果仍待控制端驗證，不更改資格。skill 來源：使用者提供 personal-harness/0.2.1/skills/task-harness/SKILL.md。預算未知。
