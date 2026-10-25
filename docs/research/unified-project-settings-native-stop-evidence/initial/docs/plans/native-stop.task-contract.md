# 任務合約：原生停止

<!-- task-harness-contract:v1 -->
```json
{
  "schema_version": 1,
  "task_id": "native-stop",
  "project_root": "/private/tmp/unified-native-stop-goza49lv/project",
  "owner_session_id": null,
  "status": "in_progress",
  "objective": "保留一次ledger成果並產出STOP_RESUMED_OK",
  "scope": [
    "保留ledger與preserve",
    "使用同一任務合約",
    "本次canary前景命令僅供原生停止驗證"
  ],
  "requirements": [
    {
      "id": "T1",
      "outcome": "ledger.txt精確EXISTING_ONCE一行",
      "status": "done",
      "depends_on": [],
      "evidence": [
        "既有fixture成果，續作先核對實際檔案"
      ]
    },
    {
      "id": "T2",
      "outcome": "docs/research/stop-result.research.md精確STOP_RESUMED_OK一行",
      "status": "pending",
      "depends_on": [
        "T1"
      ],
      "evidence": []
    }
  ],
  "authorization": {
    "user_turn_id": null,
    "mode": "wait",
    "basis": "預置部分完成狀態；須本回合實際授權"
  },
  "recovery": {
    "next_action": "核對既有成果、保存授權，再進行canary與T2",
    "blockers": [],
    "unknown_operations": [],
    "cancellation_reason": ""
  }
}
```
<!-- /task-harness-contract -->
