# 任務合約：恢復

<!-- task-harness-contract:v1 -->
```json
{
  "schema_version": 1,
  "task_id": "resume-once",
  "project_root": "/private/tmp/unified-E/project",
  "owner_session_id": null,
  "status": "done",
  "objective": "ledger保持一次APPENDED_ONCE並產出resume-result",
  "scope": [
    "只核對既有ledger副作用並產出指定結果",
    "保留既有成果"
  ],
  "requirements": [
    {
      "id": "T1",
      "outcome": "ledger僅有一行APPENDED_ONCE",
      "status": "done",
      "depends_on": [],
      "evidence": [
        "ledger.txt 既有一次寫入，恢復時重新核對",
        "本次恢復直接讀取 ledger.txt：位元組精確為 APPENDED_ONCE\\n，共一行；前次 append 已成功，不重送。"
      ]
    },
    {
      "id": "T2",
      "outcome": "產出docs/research/resume-result.research.md精確RESUMED_OK",
      "status": "done",
      "depends_on": [
        "T1"
      ],
      "evidence": [
        "docs/research/resume-result.research.md 讀回位元組精確為 RESUMED_OK\\n，僅一行；SHA-256=2ee6c1844f122a60d784ac6e07c0297e201d393ca2770bdedea83e8587111b1e"
      ]
    }
  ],
  "authorization": {
    "user_turn_id": null,
    "mode": "execute",
    "basis": "本次使用者明確授權在已確認 cwd 接續同一任務；未提供可觀測宿主 user_turn_id。"
  },
  "recovery": {
    "next_action": "無；T1、T2 與 preserve.txt 保留檢查皆通過。",
    "blockers": [],
    "unknown_operations": [],
    "cancellation_reason": "",
    "takeover": "本次主責 /root 依使用者明確續作接手原合約；宿主 session ID 不可觀測，owner_session_id 保留 null。原合約無已綁定 owner 或 worker handle；使用者指明前次中斷，ps 受環境限制無法列出程序，不宣稱具原子鎖或已驗證所有程序停止。",
    "workflow": "依使用者提供環境無可用 hooks、無 helper scripts，主責主動執行相同流程檢查；未產生 hook 收據。專案設定 schema_version=1、必要分類與目的地核對有效；沿用當前模型與強度。",
    "preserve_sha256": "f7d8eb2e57a5bc13d10424b20bc77e50cedb38dbedd9064d13299ec3ad012ebe",
    "final_verification": "逐位元組核對 T1 與 T2；preserve.txt SHA-256 與接手前一致。無重送 append、無另建合約。小型文字成果採直接內容檢查；非 Git 專案，無測試套件或 Git revision 可用。"
  }
}
```
<!-- /task-harness-contract -->
