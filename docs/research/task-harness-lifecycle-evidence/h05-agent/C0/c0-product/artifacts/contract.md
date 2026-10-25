# C0 product task contract

<!-- task-harness-contract:v1 -->
```json
{
  "schema_version": 1,
  "task_id": "c0-product",
  "project_root": "/private/tmp/h05-admission-5tpyvaik/project",
  "owner_session_id": "01a17135-2c81-73e2-8f1a-ee21d21e4432",
  "status": "done",
  "objective": "Complete the staged C0 product-hook integration check.",
  "scope": [
    "Create first.txt containing FIRST and second.txt containing SECOND.",
    "T1 initially; T2 only after native Stop reconciliation. No candidate, hook, configuration or receipt changes."
  ],
  "requirements": [
    {
      "id": "T1",
      "outcome": "Create first.txt containing FIRST and verify exact content.",
      "status": "done",
      "depends_on": [],
      "evidence": [
        "first.txt read back as exactly FIRST (5 bytes); Python byte equality assertion passed initially and at final reconciliation."
      ]
    },
    {
      "id": "T2",
      "outcome": "Create second.txt containing SECOND and verify exact content.",
      "status": "done",
      "depends_on": [
        "T1"
      ],
      "evidence": [
        "second.txt read back as exactly SECOND (6 bytes); Python byte equality assertion passed after native Stop reconciliation."
      ]
    }
  ],
  "authorization": {
    "user_turn_id": "01a17135-2c8b-7a93-b54d-51ab458f6b7f",
    "mode": "execute",
    "basis": "Original user authorizes both outcomes with T1 initially and T2 only upon native Stop reconciliation; continuation grants no new authority."
  },
  "recovery": {
    "next_action": "None. Both authorized outcomes verified; native Stop reconciliation completed under the original user turn and authorization.",
    "blockers": [],
    "unknown_operations": [],
    "cancellation_reason": ""
  }
}
```
<!-- /task-harness-contract -->

Acceptance source: original user request; verify exact marker contents.
