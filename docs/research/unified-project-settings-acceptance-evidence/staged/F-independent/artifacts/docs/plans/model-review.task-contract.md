# 任務合約：獨立模型審查

<!-- task-harness-contract:v1 -->
```json
{
  "schema_version": 1,
  "task_id": "model-review",
  "project_root": "/private/tmp/unified-F-persistent/project",
  "owner_session_id": null,
  "status": "done",
  "objective": "以原生 model_reviewer 獨立審查 preserve.txt 的精確位元組並保存模型及成果證據",
  "scope": [
    "只新增本任務合約、審查研究文件與證據",
    "保留 preserve.txt、project-setting.md 與其他長期設定；不安裝工具或服務"
  ],
  "requirements": [
    {
      "id": "T1",
      "outcome": "原生 model_reviewer 獨立審查 preserve.txt 是否等於 b\"KEEP_EXISTING_CONTENT\\n\"，保留 handle 與宿主證據",
      "status": "done",
      "depends_on": [],
      "evidence": [
        "docs/research/model-review.research.md",
        "preserve.txt SHA-256 f7d8eb2e57a5bc13d10424b20bc77e50cedb38dbedd9064d13299ec3ad012ebe",
        "/root/model_reviewer FINAL_ANSWER: exact bytes match; command exit 0"
      ]
    },
    {
      "id": "T2",
      "outcome": "產出 docs/research/model-review.research.md，區分 requested、宿主可觀測與未知，驗證受保護檔案不變",
      "status": "done",
      "depends_on": [],
      "evidence": [
        "docs/research/model-review.research.md",
        "preserve.txt SHA-256 f7d8eb2e57a5bc13d10424b20bc77e50cedb38dbedd9064d13299ec3ad012ebe",
        "/root/model_reviewer FINAL_ANSWER: exact bytes match; command exit 0"
      ]
    }
  ],
  "authorization": {
    "user_turn_id": null,
    "mode": "execute",
    "basis": "本回合使用者明確啟用 task-harness 並要求獨立審查及研究文件；宿主未提供 user-turn ID"
  },
  "recovery": {
    "next_action": "無必要未完成成果；若 preserve.txt 改變則重開受影響驗收；後端執行模型遙測未知已如實揭露",
    "blockers": [],
    "unknown_operations": [],
    "cancellation_reason": "",
    "host_identity": "主責為目前對話 /root；沒有可觀測 session ID，保持 null",
    "hooks": "未取得載入、信任或實際 hook 事件證據；由主責主動執行同一合約的流程邊界檢查，不變更設定"
  },
  "model_runs": [
    {
      "requirement_id": "T1",
      "executor": "model_reviewer",
      "handle": "/root/model_reviewer",
      "selection_source": "priority 3: project-setting.md model.role.model_reviewer",
      "requested": {
        "model": "gpt-6-sol",
        "reasoning_effort": "low"
      },
      "observed": {
        "model": null,
        "reasoning_effort": null,
        "basis": "spawn_agent(agent_type=model_reviewer, fork_turns=none) 回傳 task_name=/root/model_reviewer；原生角色介面宣告固定 gpt-6-sol/low，屬宿主角色綁定資訊；啟動回應未揭露執行模型或強度。未傳覆寫參數。",
        "evidence": "原生 spawn_agent 回傳 handle；list_agents running；同 handle FINAL_ANSWER 與完整檢查輸出，詳見 docs/research/model-review.research.md。宿主未提供實際模型/強度。"
      }
    }
  ]
}
```
<!-- /task-harness-contract -->

驗收來源：本回合使用者指示。無本次或既有任務覆寫；角色設定優先於階段設定，選擇 gpt-6-sol / low。獨立條件不得由主責自查替代。
