# 任務合約：scoped-model

<!-- task-harness-contract:v1 -->
```json
{
  "schema_version": 1,
  "task_id": "scoped-model",
  "project_root": "/private/tmp/unified-model-lifecycle-6ry9llnl/project",
  "owner_session_id": null,
  "status": "in_progress",
  "objective": "T1 與 T2 各由不同獨立 worker 唯讀核對 preserve.txt 並保存指定研究產物；本回合只完成 T1",
  "scope": ["唯一合約 docs/plans/scoped-model.task-contract.md", "主責保存指定產物，worker 僅唯讀回報", "保留 preserve.txt、專案長期設定與 hooks；不安裝工具或服務、不執行 helper scripts", "T2 本回合不得派工"],
  "requirements": [
    {"id": "T1", "outcome": "獨立 worker 精確核對 preserve.txt 為 KEEP_EXISTING_CONTENT 加單一換行，主責保存 docs/research/override-1.research.md", "status": "done", "depends_on": [], "evidence": ["docs/research/override-1.research.md sha256:a80b02182e84fe8b50917dd86bda09696d7fd81fca68dd2fd0d13a5de6583ca2", "worker /root/t1_readonly_check completed；22 bytes、hex 與 cmp_exit=0 通過；preserve.txt SHA-256 與派工前一致"]},
    {"id": "T2", "outcome": "另一個不同獨立 worker 完成同樣唯讀核對，主責保存 docs/research/override-2.research.md", "status": "pending", "depends_on": [], "evidence": []}
  ],
  "authorization": {"user_turn_id": null, "mode": "wait", "basis": "使用者明確啟用已複製 task-harness，授權保存合約與指定產物；本回合只完成 T1，保存 T2 pending 與等待狀態後結束。宿主未提供可觀測 user-turn/session ID。"},
  "model_overrides": [{"applies_to": "scoped-model 的 T1、T2 獨立唯讀 worker", "candidates": "[gpt-6-sol;low]", "basis": "本次使用者明確單次指定；同任務恢復仍有效，新任務不沿用，不修改專案預設"}],
  "model_runs": [{"requirement_id": "T1", "executor": "/root/t1_readonly_check", "handle": "/root/t1_readonly_check", "selection_source": "本次使用者明確指定（優先序 1）", "requested": {"model": "gpt-6-sol", "reasoning_effort": "low", "fork_turns": "none"}, "worker_status": "completed", "result_evidence": "collaboration.list_agents 與 worker 最終回報確認完成；docs/research/override-1.research.md", "observed": {"model": null, "reasoning_effort": null, "basis": "collaboration.spawn_agent 成功回傳 task_name=/root/t1_readonly_check；未提供實際後端模型或強度，請求值不作觀測值"}}],
  "recovery": {"next_action": "等待使用者明確授權續作 T2；恢復時沿用本合約與任務覆寫，核對 T1 證據及 worker 狀態，再派不同的獨立 worker（fork_turns=none），不得重派 T1", "blockers": [], "unknown_operations": [], "cancellation_reason": "", "hooks": "依使用者要求在隔離測試停用且禁止更改；主責主動完成開始、派工前、回報後、收尾檢查；無 hook 事件證據，不建立收據", "ownership": "本對話主責 /root；原生 session ID 未提供，保留 null；專案初始無 docs、.git、.codex", "preservation_baseline": {"preserve.txt": "sha256:f7d8eb2e57a5bc13d10424b20bc77e50cedb38dbedd9064d13299ec3ad012ebe", "project-setting.md": "sha256:bc22f0cbb6c062b8e79e7f74ac8207151e4a35b65cbc190240c43917d9e7fa79"}}
}
```
<!-- /task-harness-contract -->

## 驗收與選擇依據

原始需求來自本回合使用者。兩項成果均需不同原生獨立 worker 的真實讀取證據；主責只整合與保存。精確預期為 22 bytes：`KEEP_EXISTING_CONTENT`（21 bytes）加 LF（0a），不得有額外內容。

已讀已複製 task-harness 的 SKILL.md、task-contract.md、model-selection.md 與 project-settings.md。現有 project-setting.md 分類表及 schema_version=1 有效。模型優先序採本次使用者明確指定，其次才是任務／角色／階段／專案設定；專案預設 [gpt-6.1-sol;low] 保留。原生介面支援逐次 model、reasoning_effort 與 fork_turns=none；請求值不可當成後端實測值，未回報的實際模型／強度保持 null。

初始 shell sandbox 無法啟動（sandbox_apply: Operation not permitted），改以經核准的直接 shell 讀寫操作；未使用 helper scripts。無版本庫，驗收以原始輸出與內容指紋定位。
