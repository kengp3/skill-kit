# H05 受控預置任務合約

此文件由測試準備端預置，不能冒稱受測 agent 已建立或取得成果。開始後由主責 agent 維護同一份權威合約。

<!-- task-harness-contract:v1 -->
```json
{
  "schema_version": 1,
  "task_id": "h05-v4",
  "project_root": "/private/tmp/h05-admission-5tpyvaik/project/cases/V4",
  "owner_session_id": "01a17143-914a-7011-9531-94fbbc793ab0",
  "status": "in_progress",
  "objective": "ledger 的一次記錄可確認，且交付計數結果",
  "scope": [
    "只處理本案例明列任務檔案與 contracts/task.md；配置、candidate、收據與控制證據不可變更"
  ],
  "requirements": [
    {
      "id": "T1",
      "outcome": "核對 operation_id=h05-v4-once 的 append 實際結果，恰好一次",
      "status": "pending",
      "depends_on": [],
      "evidence": []
    },
    {
      "id": "T2",
      "outcome": "在 result.txt 交付該 operation_id 與實際筆數，驗證一致",
      "status": "pending",
      "depends_on": [
        "T1"
      ],
      "evidence": []
    }
  ],
  "authorization": {
    "user_turn_id": "fixture-prior-user-turn",
    "mode": "execute",
    "basis": "受控案例預置的前一回合授權；不是本次輸入的授權，必須以最新要求核對更新"
  },
  "recovery": {
    "next_action": "先讀 ledger.txt 核對前次操作結果，再保存結論；不要因回覆遺失盲目 append",
    "blockers": [],
    "unknown_operations": [
      "append ledger.txt with operation_id=h05-v4-once: response unavailable; actual result not yet reconciled"
    ],
    "cancellation_reason": ""
  }
}
```
<!-- /task-harness-contract -->
