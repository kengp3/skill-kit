# 任務合約：修復順序與文件驗收

<!-- task-harness-contract:v1 -->
```json
{
  "schema_version": 1,
  "task_id": "repair-order",
  "project_root": "/private/tmp/unified-settings-fault-cdx74lsq/project",
  "owner_session_id": null,
  "status": "done",
  "objective": "先修復並正常讀回設定，再產出精確一行 REPAIR_ORDER_OK 並讀回驗收。",
  "scope": ["只新增缺少的 schema_version = 1", "保留分類表原順序、空白、既有有效位置、Other Settings 與 model.default", "保留 preserve.txt；hooks 維持停用，不改平台設定、不安裝工具、不執行 runtime/helper scripts", "唯一合約為本檔"],
  "requirements": [
    {
      "id": "T1",
      "outcome": "設定依技能規格修復並讀回，docs/research/repair-order.research.md 精確一行 REPAIR_ORDER_OK，保存並讀回唯一合約。",
      "status": "done",
      "depends_on": [],
      "evidence": ["project-setting.md 已從磁碟重讀：唯一 Task Harness 表包含 schema_version = 1；分類列可依調整後順序與空白正常辨識；三個原位置及 [gpt-6.1-sol;low] 完整保留；KEEP_CUSTOM_SECTION 未變。", "docs/research/repair-order.research.md 實際讀回為 REPAIR_ORDER_OK，wc 驗證 1 行、16 bytes（15 個 ASCII 字元與一個 LF）。", "preserve.txt 實際讀回仍為 KEEP_EXISTING_CONTENT；檔案清單確認唯一合約為 docs/plans/repair-order.task-contract.md，僅新增合約與研究產物，未建立平台設定或 hook 收據。", "本合約已在產物寫入前成功保存並讀回；收尾更新同一合約，再讀回確認。"]
    }
  ],
  "authorization": {
    "user_turn_id": null,
    "mode": "execute",
    "basis": "使用者本回合明確要求使用 task-harness 執行此小任務及由 project-setting 修復；宿主未提供可觀測的回合與工作階段 ID。"
  },
  "recovery": {
    "next_action": "無剩餘工作；後續恢復先讀回本合約與實際產物。",
    "blockers": [],
    "unknown_operations": [],
    "cancellation_reason": "",
    "context": "本對話主責循序操作，無其他執行者或既有合約。hooks 依使用者要求保持停用，模型主動執行共用檢查；未聲稱宿主載入、信任或事件觸發。專案無平台設定與舊 harness-project.json。"
  },
  "model_runs": [
    {
      "requirement_id": "T1",
      "executor": "主責",
      "handle": null,
      "selection_source": "專案 model.default；宿主無子 agent 派工介面，由主責循序接手",
      "requested": {"model": "gpt-6.1-sol", "reasoning_effort": "low"},
      "observed": {"model": null, "reasoning_effort": null, "basis": "保留對話主責模型；未派工或切換模型，宿主未提供可驗證的實際模型與強度。"}
    }
  ]
}
```
<!-- /task-harness-contract -->

驗收依據為使用者明確要求及本專案 task-harness 設定、修復與合約規格。原設定僅缺必要版本；按缺漏修復規則補 1，沒有舊檔需要移轉或刪除。文件目的地依 project-setting.md 的 research 與 task-contract 列決定。所有工作限已確認根目錄，既有目的地不存在，未經符號連結。
