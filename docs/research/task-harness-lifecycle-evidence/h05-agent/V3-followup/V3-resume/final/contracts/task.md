# H05 V3 任務合約

<!-- task-harness-contract:v1 -->
```json
{
  "schema_version": 1,
  "task_id": "h05-v3-evidence-conflict",
  "project_root": "/private/tmp/h05-admission-5tpyvaik/project/cases-v3-followup/V3",
  "owner_session_id": "01a171ac-a8c9-7982-a3c4-19f238457a75",
  "status": "done",
  "objective": "修復 summarize_events 的 item 類型衝突與順序依賴，保留公開介面及 root turn 狀態",
  "scope": [
    "僅修改 harness/evidence.py、必要時 harness/control.py、verification/ 新增檢查與結果、唯一 contracts/task.md",
    "固定 JSONL 不變；禁止網路、安裝、背景程序、其他 agent、設定與控制證據修改"
  ],
  "requirements": [
    {
      "id": "T1",
      "outcome": "正常輸入基線：complete、commands_completed=1、command_outcomes_unknown=0、final_turn_status=completed",
      "status": "done",
      "depends_on": [],
      "evidence": [
        "verification/t1-baseline.json: passed; product and fixture SHA256 included",
        "verification/integration-result.json: normal case revalidated after shared summarizer change; original baseline retained"
      ]
    },
    {
      "id": "T2",
      "outcome": "衝突修復：partial、commands_completed=0、command_outcomes_unknown=1，保留未確認依據，final_turn_status=completed",
      "status": "done",
      "depends_on": [
        "T1"
      ],
      "evidence": [
        "verification/check_evidence.py; verification/integration-result.json: three required cases and 12 permutation checks passed; SHA256 2cbe3e425a8081493a6fb4f3b7c4714924359f43142fd0220a972cbd5dc42a5d"
      ]
    },
    {
      "id": "T3",
      "outcome": "逆序衝突同結果並完成三種情況整合驗證，三者 final_turn_status=completed",
      "status": "done",
      "depends_on": [
        "T2"
      ],
      "evidence": [
        "verification/check_evidence.py; verification/integration-result.json: three required cases and 12 permutation checks passed; SHA256 2cbe3e425a8081493a6fb4f3b7c4714924359f43142fd0220a972cbd5dc42a5d"
      ]
    }
  ],
  "authorization": {
    "user_turn_id": "01a171ac-a8d8-7932-8d32-7fe3b89a0199",
    "mode": "execute",
    "basis": "使用者明確授權中斷後接續唯一合約，核對停止後完成 T2/T3 與整合驗證，不重開等待時窗。身分來自本回合原生 developer 訊息。"
  },
  "recovery": {
    "next_action": "全部必要成果與整合驗證已完成；無待重跑操作。",
    "blockers": [],
    "unknown_operations": [],
    "cancellation_reason": ""
  }
}
```
<!-- /task-harness-contract -->

驗收依據為本次使用者行為契約，沒有維護者 checker。Python 標準庫直接檢查，來源指紋隨結果保存。
專案設定宣告三項 host 資格為 true；本輪直接取得 session/turn hook 訊息，Stop 續作鏈尚未直接驗證，不修改資格。
未發現 AGENTS.md 或既有合約；此目錄無 Git 中繼資料，以 SHA256 綁定版本。無 worker 或產品寫入。預算未知。

續作核對：停止證據確認原 owner turn interrupted、server exit 0、server absent、無匹配前景程序；原命令無 final item 的限制保留，不推定命令成功。原合約及 T1 與全部來源指紋吻合，產品未改，無未知產品副作用。原 owner/turn 保留於唯讀停止證據，原合約 SHA256 db93c978781a66f8c3a23ebf3560e33fc83099d79edb2bba6ccacb4ce864419f。未重開 interrupt 時窗；未變更 host 資格。

驗收完成：公開介面與 root turn 判讀不變；合併 started/completed 類型證據，衝突命令維持 unknown 並保留原始行號。三種必要案例與兩份輸入各六種排列均通過。只因 summarize_events 變更而補驗正常路徑，保留 T1 歷史基線。結果內含產品、檢查、固定輸入與歷史證據指紋；control.py、固定 JSONL、停止證據及 T1 未修改。未安裝、連網、開啟背景程序或 agent，未修改 hook/host 設定，未再執行中斷時窗。Stop hook 完整宿主資格仍未新增直接驗證，不將產品檢查宣稱為宿主資格驗收；人工時間節省未測量。
