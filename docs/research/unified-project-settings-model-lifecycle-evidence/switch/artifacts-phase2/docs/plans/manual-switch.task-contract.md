# 任務合約：manual-switch

<!-- task-harness-contract:v1 -->
```json
{
  "schema_version": 1,
  "task_id": "manual-switch",
  "project_root": "/private/tmp/unified-model-lifecycle-t88tei2a/project",
  "owner_session_id": null,
  "status": "done",
  "objective": "以原生 old_worker 等待 gate 後唯讀核對 preserve.txt，保留可查證派工與模型選擇依據",
  "scope": [
    "唯一合約為 docs/plans/manual-switch.task-contract.md",
    "保留 preserve.txt 與專案長期設定",
    "不安裝工具或服務，不執行 helper scripts，不更改停用的 hooks",
    "續作回合先核對 old_worker 存活，建立 gate-old.txt，再派 new_worker 並驗收兩份結果"
  ],
  "requirements": [
    {
      "id": "T1",
      "outcome": "old_worker 在 gate-old.txt 出現後，唯讀核對 preserve.txt 精確為 KEEP_EXISTING_CONTENT 加一個換行，回報可驗證結果；等待上限 600 秒",
      "status": "done",
      "depends_on": [],
      "evidence": [
        "原生 worker /root/old_worker 已回報開始，本回合釋放 gate 前 list_agents 再次觀測 running；gate 後回報 PASS，22 bytes，hex 4b4545505f4558495354494e475f434f4e54454e540a；詳見 docs/research/manual-switch.research.md。"
      ]
    },
    {
      "id": "T2",
      "outcome": "new_worker 獨立唯讀核對 preserve.txt 精確為 KEEP_EXISTING_CONTENT 加一個換行，回報可驗證結果；主責產出 docs/research/manual-switch.research.md",
      "status": "done",
      "depends_on": [],
      "evidence": [
        "原生 worker /root/new_worker 獨立回報 PASS，22 bytes，hex 4b4545505f4558495354494e475f434f4e54454e540a；主責再次唯讀核對一致；docs/research/manual-switch.research.md 已保存。"
      ]
    }
  ],
  "authorization": {
    "user_turn_id": null,
    "mode": "execute",
    "basis": "使用者明確續作同一任務，授權在核對 old_worker 存活後建立 gate-old.txt，派 new_worker，驗收兩者並保存研究紀錄；宿主 user-turn ID 不可觀測。"
  },
  "recovery": {
    "next_action": "兩個 worker 的結果、主責唯讀核對及研究紀錄均已保存；無待執行成果。",
    "blockers": [],
    "unknown_operations": [],
    "cancellation_reason": "",
    "ownership_basis": "同一對話明確續作；未取得可觀測 session ID，不虛構身分",
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
      "worker_status": "completed",
      "status_evidence": "上一回合與本回合建立 gate 前均以 collaboration.list_agents 觀測 running；gate 後收到 worker MESSAGE 與 FINAL_ANSWER，結果 PASS。原始 handle 及派工選擇保留。"
    },
    {
      "requirement_id": "T2",
      "executor": "new_worker",
      "handle": "/root/new_worker",
      "selection_source": "6：無本次、任務、角色、階段或專案指定；原生繼承目前主責",
      "requested": {
        "model": null,
        "reasoning_effort": null,
        "inherit_from": "本回合目前主責選擇 gpt-6-sol / medium（使用者陳述已透過 turn/start 切換）；spawn 省略模型與強度參數，fork_turns=none"
      },
      "observed": {
        "model": null,
        "reasoning_effort": null,
        "basis": "collaboration.spawn_agent 成功回傳 task_name /root/new_worker；未回報實際後端模型或強度。主責目前模型另由宿主本回合 model_instructions 指明 gpt-6-sol，強度切換依使用者提供的 turn/start 資訊。"
      },
      "dispatch_status": "started",
      "worker_status": "completed",
      "status_evidence": "收到 worker MESSAGE 與 FINAL_ANSWER，結果 PASS；主責以 wc -c 與 od -An -tx1 -v 獨立核對相同 22 bytes。"
    }
  ]
}
```
<!-- /task-harness-contract -->

模型選擇依據：已讀 project-setting.md 及 task-harness 的 model-selection.md。無本次指定、任務覆寫、角色、階段或專案模型預設，採優先序 6，模型與推理強度一起原生繼承主責；不推測後端模型。

驗收來源為本次使用者要求。old_worker 先報開始、等待 gate，並於 600 秒內完成唯讀核對；new_worker 獨立完成唯讀核對。主責已收取兩份結果、獨立核對位元組內容，並將可觀測結果與限制寫入 docs/research/manual-switch.research.md。
