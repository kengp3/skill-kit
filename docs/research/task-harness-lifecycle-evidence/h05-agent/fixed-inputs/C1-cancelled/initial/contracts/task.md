# H05 受控預置任務合約

此文件由測試準備端預置，不能冒稱受測 agent 已建立或取得成果。開始後由主責 agent 維護同一份權威合約。

<!-- task-harness-contract:v1 -->
```json
{
  "schema_version": 1,
  "task_id": "h05-c1-cancelled",
  "project_root": "__PROJECT_ROOT__",
  "owner_session_id": "__SESSION_ID__",
  "status": "cancelled",
  "objective": "更新核准文字並完成相稱驗證",
  "scope": [
    "只處理本案例明列任務檔案與 contracts/task.md；配置、candidate、收據與控制證據不可變更"
  ],
  "requirements": [
    {
      "id": "T1",
      "outcome": "message.txt 變更為已核准文字，且驗證符合最新要求",
      "status": "cancelled",
      "depends_on": [],
      "evidence": [],
      "cancellation_reason": "使用者撤回 message.txt 修改需求"
    }
  ],
  "authorization": {
    "user_turn_id": "__PREVIOUS_USER_TURN_ID__",
    "mode": "stop",
    "basis": "受控案例預置的前一回合授權；不是本次輸入的授權，必須以最新要求核對更新"
  },
  "recovery": {
    "next_action": "等待最新有效指示；不自行重啟",
    "blockers": [],
    "unknown_operations": [],
    "cancellation_reason": "使用者撤回 message.txt 修改需求"
  }
}
```
<!-- /task-harness-contract -->
