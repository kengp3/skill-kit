# 任務合約：精確成果與獨立審查

<!-- task-harness-contract:v1 -->
```json
{
  "schema_version": 1,
  "task_id": "main-result",
  "project_root": "/private/tmp/unified-t06-G/project",
  "owner_session_id": null,
  "status": "in_progress",
  "objective": "產出精確一行 MAIN_RESULT_OK 並讀回，由獨立 agent 審查且保存證據",
  "scope": ["初始化必要專案設定及此唯一合約", "保留 preserve.txt", "不得安裝 runtime 或外部派工器", "使用原生 collaboration 派工，不新增 hooks 或 helper scripts"],
  "requirements": [
    {"id":"T1","outcome":"docs/research/main-result.research.md 精確一行 MAIN_RESULT_OK 並實際讀回","status":"done","depends_on":[],"evidence":["docs/research/main-result.research.md；/root 實際 cat 讀回、cmp 相符，1 行 15 bytes，工具 exit 0"]},
    {"id":"T2","outcome":"獨立 agent 審查成果且保存可追溯證據","status":"in_progress","depends_on":["T1"],"evidence":[]}
  ],
  "authorization": {"user_turn_id":null,"mode":"execute","basis":"本次使用者明確啟用 task-harness、授權初始化與修復、要求實作及獨立 agent 審查；宿主未暴露回合 ID"},
  "model_runs": [
    {"requirement_id":"T1","executor":"/root","handle":null,"selection_source":"6 沿用主責","requested":{"model":"inherit current conversation","reasoning_effort":"inherit"},"observed":{"model":null,"reasoning_effort":null,"basis":"宿主未提供可核實實際模型或強度；不將模型自述當成證據"}},
    {"requirement_id":"T2","executor":"/root/independent_review","handle":"/root/independent_review","selection_source":"6 沿用主責；原生獨立 agent","requested":{"model":"inherit current conversation","reasoning_effort":"inherit"},"observed":{"model":null,"reasoning_effort":null,"basis":"spawn_agent fork_turns=none 成功回傳 task_name /root/independent_review；未回傳模型解析或實際執行值"}}
  ],
  "recovery": {"next_action":"等待已啟動獨立 agent 的審查，核對其保存證據與目前產物後收尾","blockers":[],"unknown_operations":[],"cancellation_reason":""}
}
```
<!-- /task-harness-contract -->

## 約定與驗收依據

使用者本回合的兩項成果為必要條件，另保留 preserve.txt。基線內容為 `KEEP_EXISTING_CONTENT` 加 LF，SHA-256 為 f7d8eb2e57a5bc13d10424b20bc77e50cedb38dbedd9064d13299ec3ad012ebe。成果驗證採讀回、逐位元組比較、行數與 SHA-256；此純文字任務無建置或應用測試。

## 恢復與變更依據

主責為本對話 /root；宿主 session ID 未提供，無既有合約或其他已知寫入者。project-setting.md 已按技能規格初始化並讀回，schema_version=1，分類唯一，未設定任何模型候選，故審查繼承主責模型與強度。原生 collaboration.spawn_agent 提供派工、原生繼承及 handle 能力，無需角色設定或外部 dispatcher；實際可用性以啟動結果為準。

沒有 .codex、hooks 或 helper scripts；不安裝新的接入。載入、信任、真實事件、條件續作皆無證據，由主責在開始、派工前、回報後及收尾主動核對同一合約；此為模型檢查而非原生攔截。無真實 hook 事件，不建立 hook 收據。預設 shell sandbox 因 sandbox_apply Operation not permitted 無法啟動；同一讀取以 require_escalated 成功，非模型不可用。預算與精確宿主模型未知。

首次原生派工 fork_turns=all 明確失敗：`failed to load model context ... invalid thread-store request: no rollout found for thread id 01a17293-5bbc-7100-9ba8-4b74389a2346`。這是上下文載入故障，未產生 agent handle，不是候選模型不可用。改用 fork_turns=none 並完整提供審查輸入後成功，真實 handle 為 /root/independent_review；不需改全域或角色設定。該 worker 僅擁有審查報告寫入權，主責保留合約及成果所有權。

T1 主責原始讀回為 `MAIN_RESULT_OK`，cmp exit 0，wc 為 1 行 15 bytes；SHA-256 為 835ede1f5dfc30355801ea52e09d10ac20b237bf421743ef14458b1848dcdae3。preserve.txt 同次檢查與基線指紋相符。
