# 任務合約：harness-g01-smoke

<!-- task-harness-contract:v1 -->
```json
{
  "schema_version": 1,
  "task_id": "harness-g01-smoke",
  "project_root": "/Users/kengp3/Workspaces/mine/demo-002",
  "owner_session_id": null,
  "status": "done",
  "objective": "以原生主責及單一合約完成無破壞性 smoke task，產出並驗證精確的一行檔案。",
  "scope": [
    "只新增 docs/plans/harness-g01-smoke.task-contract.md 與 docs/research/harness-g01-smoke.research.md，保留其他既有檔案與設定",
    "不讀取或執行 .planning；不跑 Java/Maven、Python/Node/helper；不安裝服務或套件；不派子代理",
    "不修改信任 db、不 bypass、不建立第二 tracker 或假 hook 收據"
  ],
  "requirements": [
    {
      "id": "T1",
      "outcome": "成功保存且完整讀回本合約後，建立 research 檔案，精確內容為 G01_NATIVE_DEMO_OK 加一個 LF（19 bytes）；實際讀回驗收，再保存 done 合約並完整重讀。",
      "status": "done",
      "depends_on": [],
      "evidence": [
        "初始完整合約保存並 cat 讀回成功（exec chunk b1606d，exit 0）；主責確認唯一 JSON、核心欄位、無重複 keys、T1 無依賴及授權後才建立產物。",
        "docs/research/harness-g01-smoke.research.md 實際讀回（exec chunk 9bf1b4，exit 0）：cmp 與 printf 預期內容逐 byte 相等；wc 為 1 行、19 bytes；od 為 47 30 31 5f 4e 41 54 49 56 45 5f 44 45 4d 4f 5f 4f 4b 0a；cat 為 G01_NATIVE_DEMO_OK。",
        "目前產物 SHA-256：ca833e26cc7c39f3c69a5f7ecf3a2a09d44ea2a73194ce26c4e6386dd2503a4f。",
        "收尾前主責審查通過：只新增兩個指定檔案、無第二 tracker、無收據、無子代理；AGENTS.md、project-setting.md、兩份 .codex 設定及 SKILL 的前後 SHA-256 相同；git 既有變更保留。"
      ]
    }
  ],
  "authorization": {
    "user_turn_id": null,
    "mode": "execute",
    "basis": "本次使用者明確啟用 $task-harness，指定唯一 root/task_id/合約、兩個新增檔案及 T1 驗收；後附技能內容未撤銷授權。宿主未提供可觀測 user-turn ID，故為 null。"
  },
  "model_overrides": [
    {
      "applies_to": "harness-g01-smoke 的 T1，由原生主責執行",
      "candidates": ["gpt-6.1-sol;low"],
      "basis": "使用者本次明確指定；不切換對話模型、不派子代理。"
    }
  ],
  "model_runs": [
    {
      "requirement_id": "T1",
      "executor": "主責",
      "handle": null,
      "selection_source": "本次使用者明確指定",
      "requested": {"model": "gpt-6.1-sol", "reasoning_effort": "low"},
      "observed": {
        "model": null,
        "reasoning_effort": null,
        "basis": "可觀測宿主為 Codex 原生工具介面；沒有主責實際模型、強度或 provider weights 的可查證回報，不把 requested 當 observed。"
      }
    }
  ],
  "recovery": {
    "next_action": "正常收尾：完整讀回本次 done 合約，核對唯一 T1 的當前驗收與宿主證據缺口後交付；若保存或讀回異常，修復同一合約，不重做產物。",
    "blockers": [],
    "unknown_operations": [],
    "cancellation_reason": "",
    "host_identity_gap": "owner_session_id 與 user_turn_id 均不可觀測；目前對話主責依本次明確要求執行，沒有可觀測的其他 writer，無跨程序原子鎖保證。",
    "hook_connection": "已讀 .codex/config.toml：features.hooks=true；.codex/hooks.json 的三個 harness 事件無 matcher，完整 handler 與技能 assets/codex-hooks.json 相符，另有既有 project-setting 提醒。未取得實際載入來源清單、信任、事件注入或條件續作證據；不宣稱已信任或觸發。依使用者禁止改設定，主責在同一合約主動接手開始、階段轉換與收尾檢查；沒有 worker 回報時點，也不建立收據。",
    "limits": "時間、token 預算與人工作業節省量未量測；不宣稱原生 hook 環境資格通過。"
  }
}
```
<!-- /task-harness-contract -->

## 約定與驗收依據

唯一需求來源為本次使用者要求；唯一根目錄已由使用者與 pwd 確認。已讀現行 AGENTS.md、project-setting.md、安裝的 task-harness SKILL 與 provider 的 project-settings、task-contract、model-selection 規格；技能目錄列出 ai-code-review、define-task、project-setting、task-harness。本次無須修改設定或啟用其他技能。

已重讀 project-setting.md：單一 Task Harness 區段、唯一 schema_version=1、兩個必要分類列與 research 分類有效，未設定模型列，未發現已檢查位置的 legacy harness-project.json。docs 無下層 AGENTS.md；根與既有 docs 父目錄非符號連結，兩個目標尚不存在。原有 .gitignore、AGENTS.md 修改及 .agents/skills、.codex、project-setting.md 未追蹤狀態保留；git 初次 fsmonitor 診斷屬既有環境問題，後續以單次 core.fsmonitor=false 讀取，不修改設定。未讀取 .planning 內容。

低風險純文字新增，採逐 byte 比對、長度、十六進位與 SHA-256 驗收，不執行專案 Java/Maven tests。主責審查 correctness、readability、architecture、security、performance；本次不改程式架構、執行行為或共享資源。

## 恢復與變更依據

此檔為唯一權威合約。開始與階段轉換由主責主動檢查，非 hook 技術收據。保存失敗或未知時先讀回同一檔案，不重建 tracker 或盲目重做產物。
