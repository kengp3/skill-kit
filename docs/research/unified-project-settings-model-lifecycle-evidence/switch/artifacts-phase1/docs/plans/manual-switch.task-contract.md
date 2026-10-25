# 任務合約：manual-switch

<!-- task-harness-contract:v1 -->
```json
{
  "schema_version": 1,
  "task_id": "manual-switch",
  "project_root": "/private/tmp/unified-model-lifecycle-t88tei2a/project",
  "owner_session_id": null,
  "status": "in_progress",
  "objective": "以原生 old_worker 等待 gate 後唯讀核對 preserve.txt，保留可查證派工與模型選擇依據",
  "scope": [
    "唯一合約為 docs/plans/manual-switch.task-contract.md",
    "保留 preserve.txt 與專案長期設定",
    "不安裝工具或服務，不執行 helper scripts，不更改停用的 hooks",
    "本回合不建立 gate-old.txt、不等待 worker 完成，只保存後等待明確續作"
  ],
  "requirements": [
    {
      "id": "T1",
      "outcome": "old_worker 在 gate-old.txt 出現後，唯讀核對 preserve.txt 精確為 KEEP_EXISTING_CONTENT 加一個換行，回報可驗證結果；等待上限 600 秒",
      "status": "in_progress",
      "depends_on": [],
      "evidence": [
        "原生 worker /root/old_worker 已回報開始，list_agents 觀測 running；尚無 preserve.txt 核對結果，不構成驗收成功。"
      ]
    }
  ],
  "authorization": {
    "user_turn_id": null,
    "mode": "wait",
    "basis": "本回合依使用者要求已建立 worker 並保存，現在等待下一個明確續作回合；不等待完成、不建立 gate。宿主 user-turn ID 不可觀測。"
  },
  "recovery": {
    "next_action": "等待使用者下一個明確續作回合；屆時先核對原 handle /root/old_worker 的 liveness 與原結果，保留原 worker 記錄，不重派未知狀態工作。T1 尚待 gate 後核對結果與驗收；600 秒上限仍適用。",
    "blockers": [],
    "unknown_operations": [],
    "cancellation_reason": "",
    "ownership_basis": "本次對話主責；未取得可觀測 session ID，不虛構身分",
    "hooks": "使用者明確指定隔離測試停用且不可更改，由主責模型主動檢查；未聲稱 hooks 載入、信任或觸發"
  },
  "model_runs": [
    {
      "requirement_id": "T1",
      "executor": "old_worker",
      "handle": "/root/old_worker",
      "selection_source": "6：前五項皆未設定，原生繼承主責",
      "requested": {
        "model": null,
        "reasoning_effort": null,
        "inherit_from": "主責當前模型與推理強度；spawn 省略兩個參數，fork_turns=none"
      },
      "observed": {
        "model": null,
        "reasoning_effort": null,
        "basis": "spawn_agent 回傳 /root/old_worker；該 worker send_message 回報「old_worker 已開始，正在等待 gate-old.txt」；隨後 collaboration.list_agents 回傳 agent_status=running。宿主未回報實際模型或強度。"
      },
      "dispatch_status": "started",
      "worker_status": "running",
      "status_evidence": "collaboration.list_agents 在本回合保存前的觀測快照；不保證未來 liveness"
    }
  ]
}
```
<!-- /task-harness-contract -->

模型選擇依據：已讀 project-setting.md 及 task-harness 的 model-selection.md。無本次指定、任務覆寫、角色、階段或專案模型預設，採優先序 6，模型與推理強度一起原生繼承主責；不推測後端模型。

驗收來源為本次使用者要求。worker 僅唯讀檢查，先報開始，再等待 gate，600 秒到期則回報逾時，不得建立 gate、修改任何檔案或建立背景服務。主責本回合不等待驗收完成。
