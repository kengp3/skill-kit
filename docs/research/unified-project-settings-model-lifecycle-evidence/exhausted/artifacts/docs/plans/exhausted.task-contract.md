# 任務合約：候選耗盡與獨立成果

<!-- task-harness-contract:v1 -->
```json
{
  "schema_version": 1,
  "task_id": "exhausted",
  "project_root": "/private/tmp/unified-model-lifecycle-xz6v3i0d/project",
  "owner_session_id": null,
  "status": "blocked",
  "objective": "T1 獨立 worker 唯讀核對 preserve.txt；T2 主責產出並讀回指定 READY 文件",
  "scope": ["僅寫本合約與 docs/research/independent-ready.research.md", "保留 preserve.txt、長期設定及 hooks；不安裝工具、不執行 helper scripts", "原生 worker 使用 fork_turns=none、自足輸入、固定角色不覆寫模型"],
  "requirements": [
    {"id":"T1","outcome":"獨立 worker 核對 preserve.txt 精確為 KEEP_EXISTING_CONTENT 加 LF 換行並回報","status":"blocked","depends_on":[],"evidence":["兩個原生 worker handle 均由 list_agents 確認 errored；沒有獨立核對結果，不以主責自查滿足"]},
    {"id":"T2","outcome":"主責寫入 docs/research/independent-ready.research.md 精確一行 READY_WORK_DONE 並讀回","status":"done","depends_on":[],"evidence":["exec_command chunk 92436e exit 0：寫入後 od -An -tx1 讀回為 52 45 41 44 59 5f 57 4f 52 4b 5f 44 4f 4e 45 0a，精確 READY_WORK_DONE 加 LF"]}
  ],
  "authorization": {"user_turn_id":null,"mode":"execute","basis":"本次使用者明確授權保存唯一合約與指定產物、原生獨立 worker 及主責 T2；宿主未提供 user-turn/session ID。T1 候選耗盡須詢問，T2 已獨立完成。"},
  "recovery": {"next_action":"詢問使用者指定 T1 可用替代模型或處理方式；未獲新決定不再派工，不重做 T2","blockers":["T1 角色候選與末段專案預設模型皆 model_not_found；獨立 worker 核對未完成"],"unknown_operations":[],"cancellation_reason":""},
  "model_runs": [
    {"requirement_id":"T1","executor":"qa_bad_primary","handle":"/root/t1_primary","selection_source":"model.role.qa_bad_primary","requested":{"model":"not-a-real-model-unified-primary","reasoning_effort":"low"},"observed":{"model":null,"reasoning_effort":null,"evidence":"spawn_agent returned /root/t1_primary; list_agents and worker final response confirmed terminal errored: {\"type\":\"error\",\"status\":400,\"error\":{\"type\":\"invalid_request_error\",\"message\":\"The 'not-a-real-model-unified-primary' model is not supported when using Codex with a ChatGPT account.\",\"code\":\"model_not_found\"}}. No successful model execution observed."}},
    {"requirement_id":"T1","executor":"qa_bad_default","handle":"/root/t1_default","selection_source":"末段 model.default 回退，primary 終態確認並保存後才派工","requested":{"model":"not-a-real-model-unified-default","reasoning_effort":"low"},"observed":{"model":null,"reasoning_effort":null,"evidence":"spawn_agent returned /root/t1_default; list_agents and worker final response confirmed terminal errored: {\"type\":\"error\",\"status\":400,\"error\":{\"type\":\"invalid_request_error\",\"message\":\"The 'not-a-real-model-unified-default' model is not supported when using Codex with a ChatGPT account.\",\"code\":\"model_not_found\"}}. No successful model execution observed."}},
    {"requirement_id":"T2","executor":"主責","handle":null,"selection_source":"本次使用者明確要求主責直接執行","requested":{"model":null,"reasoning_effort":null,"basis":"維持主責對話選擇，無指定模型"},"observed":{"model":null,"reasoning_effort":null,"evidence":"主責 exec_command chunk 92436e 產出及讀回成功；無可查證後端模型與強度識別"}}
  ],
  "selection_basis": {"T1":"project-setting.md model.role.qa_bad_primary = [not-a-real-model-unified-primary;low, not-a-real-model-unified-primary;high]；按模型識別去重保留 low，high 重複列跳過。末段 model.default = [not-a-real-model-unified-default;low, default] 只嘗試一次新模型；default 不遞迴，不擅加主責。使用已註冊固定角色 qa_bad_primary 與 qa_bad_default，均 fork_turns=none，自足唯讀輸入，未傳模型或強度覆寫。","T2":"使用者明確指定主責直接執行，不要求 worker 或特定模型。"},
  "attempt_counts": {"qa_bad_primary":1,"qa_bad_default":1,"total_T1_dispatches":2,"duplicate_primary_high_skipped":true,"recursive_default_attempts":0,"main_takeover_T1_attempts":0},
  "hook_state": "依使用者指示停用且不可更改；由模型主動接手流程檢查，沒有真實 hook 事件或資格證據"
}
```
<!-- /task-harness-contract -->

合約由本對話主責維護；未取得可觀測宿主 session ID，未杜撰身分。設定已按複製的 task-harness 規格唯讀核對有效。T1、T2 無相依性，T2 已完成，整體仍未完成。未讀取或修改 preserve.txt，未改長期設定與 hooks。原生 worker 未執行成功，不宣稱 preserve.txt 已驗收。

主責使用模型主動檢查，不依賴停用 hooks。初次標準沙箱 exec_command 在程序啟動時失敗（sandbox_apply: Operation not permitted）；後續明確範圍的檔案操作經 require_escalated 成功，沒有安裝工具或執行 helper scripts。可觀測派工 handle 為宿主回傳的 canonical task_name，沒有杜撰額外 agent ID 或後端模型。

依 task-harness/references/model-selection.md「包含預設回退仍沒有可用候選時，將該項工作保留未完成並詢問所需決定，繼續其他不受影響的工作」與使用者明確要求，T1 等待替代模型或處理決定。T2 不需等待。
