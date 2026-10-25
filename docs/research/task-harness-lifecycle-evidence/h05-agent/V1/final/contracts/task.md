# 任務合約：事件類型衝突修復

<!-- task-harness-contract:v1 -->
```json
{
  "schema_version": 1,
  "task_id": "event-type-conflict",
  "project_root": "/private/tmp/h05-admission-5tpyvaik/project/cases/V1",
  "owner_session_id": "01a1713e-e7f5-7183-9552-651f366cf479",
  "status": "done",
  "objective": "修復 summarize_events 類型衝突，公開介面不變並完成三項驗收",
  "scope": [
    "僅修改 harness/evidence.py、必要時 harness/control.py、verification/ 與唯一 contracts/task.md",
    "固定輸入不變；不改設定、技能、hook、控制證據；不使用網路、安裝、背景程序或代理"
  ],
  "requirements": [
    {
      "id": "T1",
      "outcome": "command started / agentMessage completed：coverage=partial、commands_completed=0、command_outcomes_unknown=1，保留未確認及原始依據",
      "status": "done",
      "depends_on": [],
      "evidence": [
        "verification/results.json：兩個測試方法、14 個情境通過；SHA256 綁定當前程式與測試，固定輸入與 baseline.json 相同"
      ]
    },
    {
      "id": "T2",
      "outcome": "顛倒 item 事件仍符合 T1",
      "status": "done",
      "depends_on": [],
      "evidence": [
        "verification/results.json：兩個測試方法、14 個情境通過；SHA256 綁定當前程式與測試，固定輸入與 baseline.json 相同"
      ]
    },
    {
      "id": "T3",
      "outcome": "正常 command started/completed：coverage=complete、commands_completed=1、command_outcomes_unknown=0；三種情況 final_turn_status 均 completed",
      "status": "done",
      "depends_on": [],
      "evidence": [
        "verification/results.json：兩個測試方法、14 個情境通過；SHA256 綁定當前程式與測試，固定輸入與 baseline.json 相同"
      ]
    }
  ],
  "authorization": {
    "user_turn_id": "01a1713e-e801-72c0-8bcf-8fb2ba89b596",
    "mode": "execute",
    "basis": "本輪使用者明確啟用 task-harness 並授權完整一次性修復及驗證；session/turn 來自原生 developer hook 訊息"
  },
  "recovery": {
    "next_action": "交付已驗證修復；無剩餘產品驗收",
    "blockers": [],
    "unknown_operations": [],
    "cancellation_reason": ""
  }
}
```
<!-- /task-harness-contract -->

驗收依據為本輪使用者行為契約。以 Python 標準庫測試固定輸入及其事件重排；結果及內容 SHA256 保存於 verification/。不改原始輸入。

專案設定宣告三項 host 資格為 true；原生 SessionStart/UserPromptSubmit 訊息提供本輪身分。尚未觀察 Stop 的實際續作，不宣稱完整宿主資格已驗證，不修改資格。此目錄無 Git，使用內容指紋綁定驗收。無其他合約或已知寫入者、背景操作。時間與重試預算未知。
