# 任務合約：g04-all-agents

<!-- task-harness-contract:v1 -->
```json
{
  "schema_version": 1,
  "task_id": "g04-all-agents",
  "project_root": "/private/tmp/g04-all-agents-r18qi6r9/project",
  "owner_session_id": null,
  "status": "blocked",
  "objective": "遵守固定 minimal 子 agent 限制，完成可執行的獨立成果並保存不可執行條件。",
  "scope": ["僅新增本合約與指定 research 成果", "保留全部初始檔案與長期設定", "不安裝服務或套件，不使用 Python、Node 或 helper，不碰其他 root", "hooks 停用；不更改 hooks 或信任，使用主動檢查", "T1 不得由主責接手或以其他強度繞過；所有子 agent 包含末段回退只能 minimal"],
  "requirements": [
    {
      "id": "T1",
      "outcome": "獨立 worker 使用 fork_turns=none 與自足輸入，唯讀核對 preserve.txt 後才產生 docs/research/strict-worker.research.md；驗收需真實 worker 與核對證據。",
      "status": "blocked",
      "depends_on": [],
      "evidence": ["host-model-metadata.json SHA256 20a26f49d19981454f394b8bbd78cac24b5eaba2ceda24b208e0109e825421f2：兩個候選均不支援 minimal", "未發送任何 spawn，無 worker handle；未產生 T1 成果；獨立核對條件未滿足"]
    },
    {
      "id": "T2",
      "outcome": "主責建立 docs/research/independent-ready.research.md，精確內容為 G04_INDEPENDENT_READY 加一個 LF，讀回並逐位元組核對。",
      "status": "done",
      "depends_on": [],
      "evidence": ["已讀回；printf 預期內容透過 cmp 逐位元組比對成功；wc 為 1 行 22 bytes，od 尾碼 0a", "成果 SHA256 0ca5cd6452b575658d91e15e352d34caff790e93496aace4558ecdce44cddcaf"]
    }
  ],
  "authorization": {
    "user_turn_id": null,
    "mode": "execute",
    "basis": "使用者明確啟用 task-harness，指定唯一根目錄、合約、T1/T2、原生子 agent 與不可變 minimal 限制。後續環境日期更新未改任務授權；宿主未提供可觀測 user-turn/session ID。"
  },
  "model_overrides": [
    {
      "applies_to": "g04-all-agents 所有子 agent，包含 T1 全部候選與末段回退；不限制主責 T2",
      "candidates": ["gpt-6.1-sol;minimal", "gpt-6-sol;minimal"],
      "basis": "本次明確指示優先；專案 model.default 為相同清單。強度嚴格不可更改。"
    }
  ],
  "model_preflight": [
    {"requested": {"model": "gpt-6.1-sol", "reasoning_effort": "minimal"}, "observed": {"model": null, "reasoning_effort": null, "basis": "未執行；metadata supportedReasoningEfforts 為 low/medium/high/xhigh/max/ultra，沒有 minimal；宿主預設 low 不可採用"}, "eligible": false},
    {"requested": {"model": "gpt-6-sol", "reasoning_effort": "minimal"}, "observed": {"model": null, "reasoning_effort": null, "basis": "未執行；metadata supportedReasoningEfforts 為 low/medium/high/xhigh/max/ultra，沒有 minimal；宿主預設 medium 不可採用"}, "eligible": false}
  ],
  "model_runs": [],
  "recovery": {
    "next_action": "已完成並驗證 T2；T1 等待使用者提供或指定原生支援 minimal 的合格候選及 metadata，保留獨立 worker 條件。",
    "blockers": ["T1 全部候選 metadata 不支援 minimal；末段專案預設相同且去重後沒有新候選，不得加主責模型或修改強度", "T1 尚無獨立 worker 唯讀核對 preserve.txt 的證據"],
    "unknown_operations": [],
    "cancellation_reason": "",
    "ownership_basis": "目前對話主責 /root；host session ID 不可觀測，null 不代表跨程序鎖。沒有發送任何子 agent 請求。",
    "hooks": {"requested": "disabled", "loaded": null, "trusted": null, "events": null, "active_checks": "主責在開始、階段切換與收尾檢查；未觀測原生 hook 事件，不生成收據，不修改設定"},
    "environment": "一般 exec 在 sandbox-exec 啟動前以 Operation not permitted 拒絕；依使用者授權使用 scoped require_escalated 僅執行本 case 命令。根目錄無 .git，無 docs 與下層指令，非 Git repository。預算未知。"
  }
}
```
<!-- /task-harness-contract -->

## 約定與驗收依據

依使用者本案指示及根目錄 AGENTS.md、project-setting.md、task-harness/SKILL.md 與 references/model-selection.md、project-settings.md、task-contract.md。設定 schema_version=1、分類與候選格式有效；不需要修復設定。兩個成果沒有相互依賴，無循環。T1 blocked 不阻止 T2；全部任務不可宣告 done。

來源 metadata 為使用者指定的原生 model/list 原始輸出，僅作能力 preflight，不是實際執行模型證據。requested 與 observed 分開；未呼叫模型不等於模型請求失敗。原生介面存在子 agent 能力，但合格候選集合為空，因此不得派工。

初始保留基準 SHA256：
- AGENTS.md：ad76c4104fd4aaa44dd3392b315cd4eb479aa980b38da20076680e1e4acbc3dd
- project-setting.md：46b382cf6935ddea2f67cd02adf65642099a90f1d1d7166111defd77c8234061
- host-model-metadata.json：20a26f49d19981454f394b8bbd78cac24b5eaba2ceda24b208e0109e825421f2
- preserve.txt：f7d8eb2e57a5bc13d10424b20bc77e50cedb38dbedd9064d13299ec3ad012ebe

## 恢復與變更依據

僅主責寫入本合約。preserve.txt 的主責雜湊檢查不構成 T1 獨立 worker 驗收。恢復時先讀本合約與最新授權，再核對 metadata、成果與實際 worker 狀態；不得把 preflight 不合格的候選送出作試探。最小使用者決定是提供／指定支援 minimal 的候選及相應原生 metadata；本次沒有授權變更強度、候選或設定。

收尾檢查：T2 的 cmp、wc、od 與讀回均通過；四個初始根目錄檔案 SHA256 與基準一致。所有寫入僅涉及本合約及 T2，未修改技能、hooks、信任或其他長期設定。T1 成果仍不存在，未派出任何 worker，沒有未知操作。已自評 correctness、readability、architecture、security、performance；此案僅文件與精確字串新增，使用直接內容與邊界核對，無需 Java build/tests。未完成條件仍保留，整體 blocked，沒有取消成果或宣告全部完成。
