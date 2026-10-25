# 任務合約：模型政策設定判讀

<!-- task-harness-contract:v1 -->
```json
{
  "schema_version": 1,
  "task_id": "model-policy",
  "project_root": "/private/tmp/unified-t08-4vnc77do/project",
  "owner_session_id": null,
  "status": "done",
  "objective": "由主責模型依已安裝 task-harness 規則判讀 cases.json，保存完整研究結果與唯一合約",
  "scope": ["逐案記錄首選來源、模型、強度、依序回退與理由", "observed_* 僅為明列測試輸入，不是實測 provider 事件", "不派工、不推定 provider 可用性、不執行解析或判斷 helper", "不修改專案長期設定或其他既有檔案"],
  "requirements": [
    {
      "id": "T1",
      "outcome": "docs/research/model-policy.research.md 完整涵蓋 11 個 case，經主責逐案比對規則與輸入，且唯一合約保存並讀回",
      "status": "done",
      "depends_on": [],
      "evidence": ["docs/research/model-policy.research.md：已讀回全文並由主責對照原始 11 案與已安裝模型規則；涵蓋全部欄位與分支", "收尾讀回 project-setting.md、cases.json、preserve.txt，內容與初讀一致；檔案清單只有新增研究文件與此唯一合約"]
    }
  ],
  "authorization": {
    "user_turn_id": null,
    "mode": "execute",
    "basis": "使用者明確要求使用已安裝 task-harness 模型規則完成設定判讀並保存唯一合約；宿主未提供可觀測 user-turn ID"
  },
  "recovery": {
    "next_action": "無待執行工作；判讀成果已驗收，若續作先核對最新使用者授權與同一合約",
    "blockers": [],
    "unknown_operations": [],
    "cancellation_reason": ""
  },
  "model_runs": [
    {
      "requirement_id": "T1",
      "executor": "主責",
      "handle": null,
      "selection_source": "維持主責對話模型，使用原生繼承；案例中的選擇不套用至主責",
      "requested": {"model": null, "reasoning_effort": null, "inherit_from": "主責目前原生對話設定"},
      "observed": {"model": null, "reasoning_effort": null, "basis": "沒有可驗證的宿主實際模型及強度回傳；不以自述身分或請求值填入觀測值"}
    }
  ]
}
```
<!-- /task-harness-contract -->

## 約定與驗收依據

根目錄由使用者環境與 pwd 確認。唯一長期設定為 project-setting.md；其分類表、唯一 Task Harness 區段、schema_version 1 與候選格式符合已安裝規格。輸入共 11 案；cases 的 current 是案例中的本次明確指定，不是主責實測模型。inherit 案以 project_defaults_present=false 模擬無專案預設；不修改實際設定。new-task 不承接前任務覆寫。

權威規則為已安裝 `/private/tmp/unified-t08-4vnc77do/state/plugins/cache/unified-t08-local/kengp3-harness/0.3.0/skills/task-harness/SKILL.md` 及 references 下 model-selection.md、project-settings.md、task-contract.md。驗收採主責逐案語意比對，不執行 helper 或 provider 探測。研究文件是證據產物，不是第二份狀態權威。

## 恢復與變更依據

本次對話主責依明確使用者指示建立合約，未派出 worker，沒有既有 worker 或未知啟動操作需要對帳。宿主 session ID 不可觀測，保留 null，不宣稱原子鎖。專案起初只有 cases.json、project-setting.md、preserve.txt，沒有既有合約，亦非 Git repository。

對話可見 task-harness 提醒，但缺少 hook 載入、信任、事件 ID 與條件續作的完整證據；由主責主動執行開始、產出前與收尾檢查，不建立技術收據、不宣稱原生攔截。一般 shell sandbox 啟動失敗，經核准的提升執行可讀取檔案；該環境錯誤不是 provider 事件。授權僅涵蓋本次文件產出，不修復或改動長期接線。
