# 任務合約：實際模型回退驗收

<!-- task-harness-contract:v1 -->
```json
{
  "schema_version": 1,
  "task_id": "fallback",
  "project_root": "/private/tmp/unified-t08-g994b31u/project",
  "owner_session_id": null,
  "status": "done",
  "objective": "實際驗收原生 unavailable_worker 模型失敗後依序回退並唯讀驗證 preserve.txt",
  "scope": [
    "只保存本合約及 docs/research/fallback.research.md",
    "worker 僅唯讀；不修改長期設定、不安裝服務、不改主責模型",
    "使用 fork_turns=none 自足上下文；固定角色不覆寫模型"
  ],
  "requirements": [
    {
      "id": "T1",
      "outcome": "保留首選真實失敗並確認未執行後，以 gpt-6.1-sol/low 原生 worker 驗證精確 bytes，保存證據與讀回合約",
      "status": "done",
      "depends_on": [],
      "evidence": [
        "docs/research/fallback.research.md：首選原始錯誤及 handle 終態、第二 handle completed、worker 精確檢查、主責 bytes 與三檔指紋複驗"
      ]
    }
  ],
  "authorization": {
    "user_turn_id": null,
    "mode": "execute",
    "basis": "使用者本回合明確啟用 task-harness、確認根目錄、授權唯一合約與結果及兩候選原生派工。宿主未提供可觀測 user turn ID。"
  },
  "recovery": {
    "next_action": "無剩餘授權工作；完成後讀回同一合約及結果。實際模型/強度獨立觀測未提供，已明示限制。",
    "blockers": [],
    "unknown_operations": [],
    "cancellation_reason": "",
    "ownership": "本對話 /root 完成唯一合約維護；兩 worker 終態已查明，無執行中 worker 或未知操作。宿主 session ID 不可得。",
    "hooks": "已收到 task-harness 提醒；載入與信任詳細狀態不可觀測。依使用者不改長期設定限制，由模型主動執行四時點檢查；不建立假收據。",
    "environment": "普通 exec sandbox-exec 啟動失敗 exit 71；經宿主批准 require_escalated 執行必要讀寫，不將此環境問題算作模型失敗。"
  },
  "model_runs": [
    {
      "requirement_id": "T1",
      "executor": "unavailable_worker /root/fallback_first",
      "handle": "/root/fallback_first",
      "selection_source": "project-setting.md model.role.unavailable_worker 第一候選；使用者明確要求原生固定角色",
      "requested": {
        "model": "not-a-real-model-for-unified-test",
        "reasoning_effort": "low"
      },
      "observed": {
        "model": null,
        "reasoning_effort": null,
        "basis": "spawn 返回 handle 後 list_agents 先為 running；其後 FINAL_ANSWER 與再次 list_agents 均確認 errored，HTTP 400 invalid_request_error model_not_found: The 'not-a-real-model-for-unified-test' model is not supported when using Codex with a ChatGPT account. 模型請求遭拒，沒有成功模型回合或工具工作；不能將暫態 running 視為已執行。"
      }
    },
    {
      "requirement_id": "T1",
      "executor": "default /root/fallback_second",
      "handle": "/root/fallback_second",
      "selection_source": "model.role.unavailable_worker 第二候選；首選 errored 後依使用者授權以通用原生 agent 接線",
      "requested": {
        "model": "gpt-6.1-sol",
        "reasoning_effort": "low"
      },
      "observed": {
        "model": null,
        "reasoning_effort": null,
        "basis": "spawn_agent 接受 default、model=gpt-6.1-sol、reasoning_effort=low、fork_turns=none，返回 handle；list_agents running。宿主回傳沒有實際模型或強度欄位，請求值不充作觀測值。 最終 list_agents completed；worker 回報精確相等 True、22 bytes，主責直接複驗通過，見 docs/research/fallback.research.md。"
      }
    }
  ]
}
```
<!-- /task-harness-contract -->
