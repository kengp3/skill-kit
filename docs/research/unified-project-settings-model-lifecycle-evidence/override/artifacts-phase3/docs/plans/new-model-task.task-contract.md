# 任務合約：獨立核對 preserve.txt

<!-- task-harness-contract:v1 -->
```json
{
  "schema_version": 1,
  "task_id": "new-model-task",
  "project_root": "/private/tmp/unified-model-lifecycle-6ry9llnl/project",
  "owner_session_id": null,
  "status": "done",
  "objective": "派出唯一一個獨立唯讀 worker，核對 preserve.txt 精確為 KEEP_EXISTING_CONTENT 加 LF，保存研究證據。",
  "scope": ["只寫本合約及 docs/research/new-model-task.research.md", "保留 preserve.txt、長期設定、hooks 與所有舊任務產物", "不安裝工具或服務，不執行 helper scripts", "worker 使用 fork_turns=none 與自足輸入"],
  "requirements": [{"id": "T1", "outcome": "獨立 worker 完成逐位元組核對，主責保存真實 handle、模型選擇依據與研究產物並讀回驗收", "status": "done", "depends_on": [], "evidence": ["docs/research/new-model-task.research.md：22 bytes，完整 hex 以 0a 結尾，worker 與主責唯讀檢查一致", "collaboration.spawn_agent 回應與 /root/preserve_check 的 FINAL_ANSWER：唯一獨立 worker 完成 PASS，未寫入檔案"]}],
  "authorization": {"user_turn_id": null, "mode": "execute", "basis": "本回合使用者明確授權新任務、指定兩份新產物及一個獨立 worker；不承接 scoped-model 的任何覆寫。宿主未提供使用者回合 ID。"},
  "model_runs": [{"requirement_id": "T1", "executor": "/root/preserve_check", "handle": "/root/preserve_check", "selection_source": "project-setting.md model.default；優先序 5", "requested": {"model": "gpt-6.1-sol", "reasoning_effort": "low"}, "observed": {"model": null, "reasoning_effort": null, "basis": "原生 collaboration.spawn_agent 回傳 task_name=/root/preserve_check；fork_turns=none。回應未揭露後端模型及實際強度，故不把請求值當觀測值。"}}],
  "recovery": {"next_action": "無待執行工作；唯一 worker 已回報，主責完成證據整合及收尾檢查。實際後端模型與強度仍未揭露。", "blockers": [], "unknown_operations": [], "cancellation_reason": ""}
}
```
<!-- /task-harness-contract -->

## 約定與驗收依據

唯一設定來源 project-setting.md：schema_version=1；model.default=[gpt-6.1-sol;low]。本次角色為唯讀核對 worker，階段為驗證；無本次模型指定、任務覆寫、角色或階段設定，故採專案預設。候選只有 gpt-6.1-sol;low，原生 spawn_agent 支援明確請求此模型與強度。請求值不當作實際後端觀測值。主責維持當前對話模型。

## 恢復與限制

本次是獨立新任務，不讀取或複製舊合約的任務模型覆寫。宿主未提供主責 session ID，保留 null；由目前對話依明確新任務授權主責。hooks 依使用者要求停用且不可變更，由主責主動完成開始、派工前、回報後及收尾檢查，不宣稱原生 hook 事件。預設 shell 沙箱啟動報 sandbox_apply: Operation not permitted；唯讀 shell 已透過受審查的 require_escalated 成功。專案沒有 .codex，亦無 Git repository，不能用 Git 提供版本差異證據。檢查新產物路徑原先不存在，docs 目錄為一般目錄。
