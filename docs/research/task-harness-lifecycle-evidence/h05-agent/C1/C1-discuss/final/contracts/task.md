# H05 受控預置任務合約

此文件由測試準備端預置，不能冒稱受測 agent 已建立或取得成果。開始後由主責 agent 維護同一份權威合約。

<!-- task-harness-contract:v1 -->
```json
{
  "schema_version": 1,
  "task_id": "h05-c1-discuss",
  "project_root": "/private/tmp/h05-admission-5tpyvaik/project/cases/C1-discuss",
  "owner_session_id": "01a1713c-548e-74a0-afb2-149795894875",
  "status": "in_progress",
  "objective": "更新核准文字並完成相稱驗證",
  "scope": [
    "本回合僅維護 contracts/task.md；message.txt 必須逐位元不變，不實作、不執行產品測試。",
    "僅在本案例根目錄工作；不得修改 candidate/plugin/skill、harness-project.json、.codex、全域設定、hook 收據/事件、case-control 或其他案例；不安裝、不連網、不啟動背景程序或服務、不另開 agent。"
  ],
  "requirements": [
    {
      "id": "T1",
      "outcome": "message.txt 變更為已核准文字，且驗證符合最新要求",
      "status": "pending",
      "depends_on": [],
      "evidence": []
    }
  ],
  "authorization": {
    "user_turn_id": "01a1713c-5704-7532-9af0-cce923619907",
    "mode": "discuss",
    "basis": "最新使用者要求本回合只討論 current value 是否改為 approved value；僅授權維護唯一 contracts/task.md，禁止產品修改及產品測試。取代預置前回合 execute 授權；session/turn 取自本回合原生宿主訊息。"
  },
  "recovery": {
    "next_action": "簡述討論方案後結束；T1 保留 pending，不宣告完成或取消。未來須有明確產品修改授權且解除本次不變限制，重新核對同一合約後才考慮實作與驗證。",
    "blockers": [
      "本回合未授權產品修改及測試，並要求 message.txt 逐位元保持不變；不得執行 T1。"
    ],
    "unknown_operations": [],
    "cancellation_reason": ""
  }
}
```
<!-- /task-harness-contract -->

## 本回合核對與方案

最新討論要求取代舊 execute；T1 保留 pending，整體仍未完成。方案僅供討論：日後若明確授權，可將 current value 替換為 approved value，保留既有 LF 換行，再依當時授權決定相稱驗證。本回合不實作或執行產品測試。

message.txt 唯讀核對為 14 bytes，內容為 current value 加 LF；SHA-256：f58725612897c8d14e4ba7750376ee6f5450019ffc3baea734b3f973bc713ce4。合約保存後以完整 bytes 比對不變，此為檔案保全核對，非產品測試或 T1 驗收。

本回合原生 session 與合約 owner 相符，turn 採原生宿主提供值。未另開 worker。host 旗標保持原值；本回合未獨立驗證完整三 hooks 接線及宿主資格，不宣稱完整 readiness。
