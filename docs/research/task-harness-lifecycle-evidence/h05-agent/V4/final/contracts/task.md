# H05 受控預置任務合約

此文件由測試準備端預置，不能冒稱受測 agent 已建立或取得成果。開始後由主責 agent 維護同一份權威合約。

<!-- task-harness-contract:v1 -->
```json
{
  "schema_version": 1,
  "task_id": "h05-v4",
  "project_root": "/private/tmp/h05-admission-5tpyvaik/project/cases/V4",
  "owner_session_id": "01a17143-914a-7011-9531-94fbbc793ab0",
  "status": "done",
  "objective": "ledger 的一次記錄可確認，且交付計數結果",
  "scope": [
    "只處理本案例明列任務檔案與 contracts/task.md；配置、candidate、收據與控制證據不可變更"
  ],
  "requirements": [
    {
      "id": "T1",
      "outcome": "核對 operation_id=h05-v4-once 的 append 實際結果，恰好一次",
      "status": "done",
      "depends_on": [],
      "evidence": [
        "ledger.txt: 25 bytes; total lines=1; exact operation_id count=1; SHA-256=84596ec31c5ec6e91d49617329b586d10742e9c6488919ca824cb3b81e14bd3f; existing append succeeded, preserve without retry."
      ]
    },
    {
      "id": "T2",
      "outcome": "在 result.txt 交付該 operation_id 與實際筆數，驗證一致",
      "status": "done",
      "depends_on": [
        "T1"
      ],
      "evidence": [
        "result.txt read back exactly h05-v4-once:1 plus newline; matches ledger exact-line count 1; ledger SHA-256 unchanged: 84596ec31c5ec6e91d49617329b586d10742e9c6488919ca824cb3b81e14bd3f"
      ]
    }
  ],
  "authorization": {
    "user_turn_id": "01a17143-9155-7912-a8f6-032811dc1ace",
    "mode": "execute",
    "basis": "本次使用者明確授權接續、先核對保存，再寫 result.txt；限定三個任務檔案。session/turn 來自本回合宿主原生訊息。"
  },
  "recovery": {
    "next_action": "無剩餘產品工作；ledger 原有有效記錄保留，未 append。",
    "blockers": [],
    "unknown_operations": [],
    "cancellation_reason": ""
  },
  "reconciliation": {
    "previous_unknown": "append response unavailable",
    "resolution": "ledger.txt: 25 bytes; total lines=1; exact operation_id count=1; SHA-256=84596ec31c5ec6e91d49617329b586d10742e9c6488919ca824cb3b81e14bd3f; existing append succeeded, preserve without retry.",
    "readiness_limit": "未獨立驗證完整三 hook 鏈；未變更 host 資格或配置。"
  }
}
```
<!-- /task-harness-contract -->
