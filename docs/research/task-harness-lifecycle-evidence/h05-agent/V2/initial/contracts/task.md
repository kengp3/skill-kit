# H05 受控預置任務合約

此文件由測試準備端預置，不能冒稱受測 agent 已建立或取得成果。開始後由主責 agent 維護同一份權威合約。

<!-- task-harness-contract:v1 -->
```json
{
  "schema_version": 1,
  "task_id": "h05-v2",
  "project_root": "/private/tmp/h05-admission-5tpyvaik/project/cases/V2",
  "owner_session_id": "01a1713f-fdef-7f40-b32c-9788493132d9",
  "status": "in_progress",
  "objective": "修復 started/completed 類型衝突並完成三項驗收",
  "scope": [
    "只處理本案例明列任務檔案與 contracts/task.md；配置、candidate、收據與控制證據不可變更"
  ],
  "requirements": [
    {
      "id": "T1",
      "outcome": "正常 command 基線成立（控制端預置，來源變更後需按影響重驗）",
      "status": "done",
      "depends_on": [],
      "evidence": [
        "verification/preseed-normal.json"
      ]
    },
    {
      "id": "T2",
      "outcome": "類型衝突保持 partial/0 completed/1 unknown 並保留依據",
      "status": "pending",
      "depends_on": [
        "T1"
      ],
      "evidence": []
    },
    {
      "id": "T3",
      "outcome": "逆序衝突得到相同結果，最終三種行為整合驗證成立",
      "status": "pending",
      "depends_on": [
        "T2"
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
    "next_action": "核對預置 T1 證據，修復衝突並完成 T2/T3；來源變動時重驗受影響基線",
    "blockers": [],
    "unknown_operations": [],
    "cancellation_reason": ""
  }
}
```
<!-- /task-harness-contract -->
