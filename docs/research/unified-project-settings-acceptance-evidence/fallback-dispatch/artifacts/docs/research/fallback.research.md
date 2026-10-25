# 實際模型回退驗收

原生派工回退流程及唯讀檢查通過。實際模型識別與強度的獨立宿主觀測不可得；下列請求值不能冒充實際執行模型證明。

## 範圍與來源

已確認根目錄 `/private/tmp/unified-t08-g994b31u/project`。唯一合約為 `docs/plans/fallback.task-contract.md`。依 `project-setting.md` 的 `model.role.unavailable_worker`，候選依序為 `not-a-real-model-for-unified-test;low`、`gpt-6.1-sol;low`。只寫合約與本證據文件，不改長期設定、主責模型，不安裝服務。兩次派工均 `fork_turns=none`，自足指示相同，worker 僅唯讀檢查，不得寫檔、建立 agent 或安裝工具。

## 首選真實失敗與查明狀態

`collaboration.spawn_agent` 使用固定原生角色 `unavailable_worker`，未傳入模型或強度覆寫。取得真實 handle `/root/fallback_first`。第一次 `list_agents` 為 `running`，因此當時沒有回退；隨後宿主 FINAL_ANSWER 回傳錯誤，再次 `list_agents` 確認 `errored`，原始錯誤如下：

```json
{"type":"error","status":400,"error":{"type":"invalid_request_error","message":"The 'not-a-real-model-for-unified-test' model is not supported when using Codex with a ChatGPT account.","code":"model_not_found"}}
```

這是模型請求遭拒的終態，沒有成功模型回合、工具執行或檔案檢查結果。先查明此 handle 失敗及沒有工作執行，保存同一合約後，才依同一清單前進第二候選。未以沙箱錯誤冒充模型失敗，未偽造失敗或盲目重派。

## 第二候選與成功結果

固定角色禁止直接覆寫模型，因此使用使用者授權的通用原生 `default` agent，請求 `model=gpt-6.1-sol`、`reasoning_effort=low`、`fork_turns=none`。成功 handle 為 `/root/fallback_second`，已保存於同一合約。`list_agents` 先為 `running`，最終為 `completed`；首選仍為 `errored`，沒有重派首選。

宿主可觀測：原生介面接受上述參數並返回 handle；生命週期及完成回報可查。宿主沒有返回實際模型與推理強度欄位，故合約 `observed.model`、`observed.reasoning_effort` 均為 null。不能僅憑請求值或 agent 自述宣稱實際模型已獨立核實。拒絕訊息明確指出首選模型名稱，但沒有首選成功執行模型。

worker 完成回報：

- 實際 bytes：`b'KEEP_EXISTING_CONTENT\n'`
- 長度：22 bytes
- 與指定 bytes 精確相等：`True`
- 未修改檔案。
- worker 引用讀取工具 chunk `457e76`：一般 exec 因 `sandbox-exec: sandbox_apply: Operation not permitted` 回傳 exit 71；獲宿主批准 `require_escalated` 後同一唯讀 Python 檢查 exit 0。此 chunk 由 worker 回報，主責另行直接驗證產物。

主責直接以 Python `read_bytes()` 驗證相等與 22 bytes，通過；SHA-256 與派工前相同：

| 檔案 | 前後相同的 SHA-256 |
| --- | --- |
| preserve.txt | f7d8eb2e57a5bc13d10424b20bc77e50cedb38dbedd9064d13299ec3ad012ebe |
| project-setting.md | 2ed696b2b649f7fabc6a4149b66ad152febec06754439926133f60bd266807f6 |
| .codex/agents/unavailable_worker.toml | aa6d9900565743daa1f0125d25aaac0ecaa8c7423bf3de16a57acc3c02b263ff |

## 流程驗收及限制

首選真實拒絕、handle 終態核對、安全順序回退、第二 worker 完成、精確 bytes 檢查及既有檔案保留均有證據。模型請求被接受與實際模型獨立證明分開記錄；後者未提供，不能宣稱通過該較強條件。依本次要求保存可觀測值與限制完成驗收。

主責已收到 task-harness 提醒；未取得 hooks 載入與信任的完整證據，依使用者禁止長期設定變更，以同一合約執行開始、派工前、回報後與收尾四時點模型檢查，不建立假 hook 收據。宿主未提供 session ID 與 user-turn ID，合約保留 null。主責普通 exec 同樣遇到沙箱啟動限制，必要讀寫經宿主批准 require_escalated 執行，未安裝或修改環境。
