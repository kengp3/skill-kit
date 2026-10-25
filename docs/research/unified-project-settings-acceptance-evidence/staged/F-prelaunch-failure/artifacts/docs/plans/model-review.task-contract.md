# 任務合約：獨立模型審查

<!-- task-harness-contract:v1 -->
```json
{
  "schema_version": 1,
  "task_id": "model-review",
  "project_root": "/private/tmp/unified-F/project",
  "owner_session_id": null,
  "status": "blocked",
  "objective": "獨立 model_reviewer 審查 preserve.txt 精確為 KEEP_EXISTING_CONTENT 加 LF，交付證據報告",
  "scope": [
    "只建立本次合約與研究報告",
    "保留 preserve.txt 與所有長期設定；不安裝工具或服務"
  ],
  "requirements": [
    {
      "id": "T1",
      "outcome": "原生獨立 model_reviewer 完成精確位元組審查並以實際證據驗收",
      "status": "blocked",
      "depends_on": [],
      "evidence": [
        "collaboration.spawn_agent 原生角色 model_reviewer 建立失敗；完整錯誤見研究報告，沒有成功 handle"
      ]
    },
    {
      "id": "T2",
      "outcome": "產出 docs/research/model-review.research.md，分離請求、宿主觀測與未知，並核對保留檔",
      "status": "done",
      "depends_on": [],
      "evidence": [
        "docs/research/model-review.research.md",
        "主責精確 bytes equality=True；22 bytes；preserve.txt 與 project-setting.md 前後 SHA-256 相同"
      ]
    }
  ],
  "authorization": {
    "user_turn_id": null,
    "mode": "execute",
    "basis": "本回合使用者明確要求 task-harness、獨立審查及文件交付；宿主未提供回合 ID"
  },
  "recovery": {
    "next_action": "宿主修復 thread-store / model context 後，沿用本合約再建立獨立 model_reviewer，補齊 T1 並重新驗收；不需修改專案設定",
    "blockers": [
      "collab spawn failed: Fatal error: failed to load model context for thread 01a17292-828f-7553-9493-e8570e3100b0: invalid thread-store request: no rollout found for thread id 01a17292-828f-7553-9493-e8570e3100b0"
    ],
    "unknown_operations": [],
    "cancellation_reason": "",
    "host_limits": "session ID 未提供；無真實 hook 注入證據，主責主動執行同一合約邊界檢查；不是 Git repository"
  },
  "model_runs": [
    {
      "requirement_id": "T1",
      "executor": "model_reviewer",
      "handle": null,
      "selection_source": "優先序 3：model.role.model_reviewer；本次與任務均無模型覆寫",
      "requested": {
        "model": "gpt-6-sol",
        "reasoning_effort": "low"
      },
      "observed": {
        "model": null,
        "reasoning_effort": null,
        "basis": "collab spawn failed: Fatal error: failed to load model context for thread 01a17292-828f-7553-9493-e8570e3100b0: invalid thread-store request: no rollout found for thread id 01a17292-828f-7553-9493-e8570e3100b0",
        "host_role_declaration": "model_reviewer 固定 gpt-6-sol / low；僅為宿主角色宣告，不是實際執行結果",
        "agent_created": false
      }
    }
  ]
}
```json
{
  "schema_version": 1,
  "task_id": "model-review",
  "project_root": "/private/tmp/unified-F/project",
  "owner_session_id": null,
  "status": "in_progress",
  "objective": "獨立 model_reviewer 審查 preserve.txt 精確為 KEEP_EXISTING_CONTENT 加 LF，交付證據報告",
  "scope": [
    "只建立本次合約與研究報告",
    "保留 preserve.txt 與所有長期設定；不安裝工具或服務"
  ],
  "requirements": [
    {
      "id": "T1",
      "outcome": "原生獨立 model_reviewer 完成精確位元組審查並以實際證據驗收",
      "status": "in_progress",
      "depends_on": [],
      "evidence": []
    },
    {
      "id": "T2",
      "outcome": "產出 docs/research/model-review.research.md，分離請求、宿主觀測與未知，並核對保留檔",
      "status": "pending",
      "depends_on": [],
      "evidence": []
    }
  ],
  "authorization": {
    "user_turn_id": null,
    "mode": "execute",
    "basis": "本回合使用者明確要求 task-harness、獨立審查及文件交付；宿主未提供回合 ID"
  },
  "recovery": {
    "next_action": "派原生 model_reviewer，保存 handle 後收取實際審查證據",
    "blockers": [],
    "unknown_operations": [],
    "cancellation_reason": "",
    "host_limits": "session ID 未提供；無真實 hook 注入證據，主責主動執行同一合約邊界檢查；不是 Git repository"
  },
  "model_runs": [
    {
      "requirement_id": "T1",
      "executor": "model_reviewer",
      "handle": null,
      "selection_source": "優先序 3：model.role.model_reviewer；本次與任務均無模型覆寫",
      "requested": {
        "model": "gpt-6-sol",
        "reasoning_effort": "low"
      },
      "observed": {
        "model": null,
        "reasoning_effort": null,
        "basis": "待派工；宿主工具宣告固定角色 gpt-6-sol / low，尚非執行證據"
      }
    }
  ]
}
```
<!-- /task-harness-contract -->

驗收：精確比較 b"KEEP_EXISTING_CONTENT\n"；獨立 agent 無法建立則 T1 保持未完成。模型自稱不作模型證據。
