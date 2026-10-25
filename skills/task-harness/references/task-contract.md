# 任務合約與必要 hooks 使用說明

本版以單一 Markdown 任務合約保存約定與恢復資訊，由主責 agent 維護。原生 tracker 只有在能保存完整合約、跨對話恢復，且具有等效 hook adapter 時才能取代它；目前實作路徑是 Markdown，不假定宿主原生清單已符合條件。

## 使用方式

接入完成後，在任務開始時說「使用 `$task-harness` 完成這項任務」即可。agent 核對授權、建立並成功保存合約後推進，使用者不必手動維護狀態表。

- 同一任務後續回合與明確續作沿用原合約；新任務不自動繼承。
- 跨對話可說「使用 `$task-harness` 接續這份任務合約：`<合約路徑>`」。agent 先核對現況與原執行者，再保存接手資訊。
- 「先討論，不修改」只授權討論；正常收尾 hook 不得因此啟動實作。
- 使用者 Stop 後須有明確續作指示；不能保證 Stop 前最後一次保存已完成。

## 專案接入

需要 Python 3 標準函式庫與三個 hooks：`SessionStart`、`UserPromptSubmit`、`Stop`。Python 3.10+ 是相容目標；本輪開發環境為 Python 3.15，不能據此宣稱已測過所有最低版本。缺少 runtime、hook 載入、宿主信任或能力資格均是完整 harness 的缺口；不自動安裝、修改全域環境或其他專案。

完整候選套件應保留 skill、相依 skills、references、Python hooks 與 plugin 接線；單獨讀取此 skill 不代表完整 harness 已接入。專案明確 opt-in 與宿主要求的信任設定是一次接入條件，不是每次任務的人工審查或監看。接入驗證須確認實際載入路徑／版本、事件及資格，不能只看設定檔存在。

首版驗收以 Codex 的實際 agent 與 hook 行為為準，可使用既有 CLI／app-server 原生入口，不以 Desktop 視窗或專屬接入作為前置條件。這不代表所有入口已合格，也不把共通 skill 格式當成跨宿主 hook 相容保證。

在明確採用的專案根目錄建立 `harness-project.json`。以下是可複製的設定結構；由 agent 代入已確認的絕對根目錄及符合專案文件規範的路徑。資格預設全部未驗證：

```json
{
  "schema_version": 1,
  "project_root": "/absolute/project",
  "contract_dir": "docs/plans/harness",
  "receipt_dir": "docs/research/harness-hook-receipts",
  "host": {
    "session_identity": false,
    "user_turn_identity": false,
    "stop_continuation": false
  }
}
```

設定根目錄須等於設定檔所在目錄，事件工作目錄須位於該專案內。合約及技術收據目錄須在專案內且互不包含，不使用符號連結或特殊檔案。工具從事件 `cwd` 向上找到最近設定，遇 Git 邊界或根目錄停止；也可明確傳入 `--project-config <路徑>`。未採用的專案不介入；不建立全域索引或掃描其他專案。

只有指定執行版本的真實事件與續作證據可將 `host` 資格改為 `true`：可靠 session 身分、可區分使用者回合與 hook 延續的 user-turn 身分、正常 Stop 的有界延續語意。CLI 合成 payload、設定成功或離線測試通過都不能代替真實資格；不可為了消除警告自行翻轉旗標。宿主資格不足保留缺口，不降為 hook 可選。

## 唯一合約範本

將下列外層 Markdown 範例內容保存為合約目錄內的一個 `.md` 文件。外層四個反引號只為展示；實際文件從標題開始。固定標記間必須恰有一個 JSON code block，機械欄位僅由它提供；不要在另一檔或另一狀態表重複維護。

````markdown
# 任務合約：修正空輸入解析

<!-- task-harness-contract:v1 -->
```json
{
  "schema_version": 1,
  "task_id": "parser-empty-input",
  "project_root": "/absolute/project",
  "owner_session_id": null,
  "status": "pending",
  "objective": "空輸入得到約定結果，既有有效輸入維持原行為",
  "scope": ["修正解析流程與相稱回歸驗證", "不改外部 API"],
  "requirements": [
    {
      "id": "T1",
      "outcome": "空輸入符合需求，既有有效輸入回歸通過",
      "status": "pending",
      "depends_on": [],
      "evidence": []
    }
  ],
  "authorization": {
    "user_turn_id": "replace-with-observed-user-turn-id",
    "mode": "discuss",
    "basis": "尚未填入本回合實際授權；此範本不能據以開始實作"
  },
  "recovery": {
    "next_action": "核對需求與實際授權，再由主責 agent 保存綁定",
    "blockers": [],
    "unknown_operations": [],
    "cancellation_reason": ""
  }
}
```
<!-- /task-harness-contract -->

## 約定與驗收依據

補充需求來源、具體預期行為、必要驗證與證據定位。JSON 的 outcome 與 evidence 可指向此處，不另建進度權威來源。

## 恢復與變更依據

保留重要範圍變更依據、已完成但尚待核對的操作，以及接手所需資訊。只補充解釋，不在此維護另一份狀態或授權值。
````

所有範本欄位均必填；`owner_session_id` 可為 `null` 表示未綁定，其餘識別值由 agent 取實際資料替換。不要虛構 session／user-turn 識別值。`scope`、`depends_on`、`evidence`、`blockers`、`unknown_operations` 都是字串陣列；無項目時用 `[]`。`basis`、`next_action`、`cancellation_reason` 是字串。

任務及成果狀態只有 `pending`、`in_progress`、`blocked`、`done`、`cancelled`。`authorization.mode` 為 `execute`、`discuss`、`wait` 或 `stop`，另記本回合授權依據；整體狀態不等於本回合授權。取消任務須在 `recovery.cancellation_reason` 留下依據；取消個別成果須在該項增加非空 `cancellation_reason`。取消不是驗收成功，全部取消不構成整體 `done`。

每個成果有穩定且唯一 ID。`depends_on` 僅指向存在的其他成果，不得自指或循環。小任務可只有 `T1`，驗證併入同一成果；只有具體必要的整合成果才另拆項目。`evidence` 應定位相關產物／檢查及其版本，agent 仍須判斷證據是否支持 outcome，不能只憑字串存在宣告通過。

工具拒絕重複 JSON keys、缺欄位、未知狀態等不明確資料，不猜測或補出授權。只掃描合約目錄直屬 Markdown，未帶固定標記的文件忽略；上限為 64 份、每份 512 KiB，事件輸入 1 MiB。超限明示能力缺口，不截斷後當作完整狀態。

## 保存、綁定與恢復

開始產品操作前成功保存合約；在重要狀態轉換、接手與正常收尾更新並讀回，不為每次檢查記帳。一次保存可以同時包含前置驗收與接續資訊。若保存失敗或結果不明，核對同一份文件並修復，確認成功前暫停相依操作；不另建替代合約、不盲目重做產品修改。

同一對話同時只主責一個未結束任務。切換前先保存原任務交接資訊並解除 `owner_session_id`，不複製或取消。跨對話接手先核對原執行狀態與實際產物，成功保存新的主責身分後才推進。找不到已知合約時只在確認專案內查找；多份綁定或歧義需核對，不按時間猜選。這是單一主責協議，不宣稱提供跨程序原子鎖。

續作保留仍有效成果，只重驗受影響部分。`unknown_operations` 先查原結果／實際副作用，不能當失敗直接重跑；Stop／中斷後從最近成功保存的內容核對，不假設最後保存存在。範圍改變更新同一合約並保留必要依據；新目標另建任務時不繼承舊授權。

## Hooks 的界線

| Hook | 責任 | 不做的事 |
| --- | --- | --- |
| `SessionStart` | 提供實際 session 身分與恢復提醒，讀取唯一有效綁定 | 不自動接手或啟動工作 |
| `UserPromptSubmit` | 提供實際 user-turn 身分，提醒 agent 核對最新要求並保存授權 | 不按關鍵字推定授權，不更新合約或重置補救次數 |
| `Stop` | 在資格、綁定、授權與未完成條件都成立時，提醒一次有界收尾補救 | 不阻止使用者 Stop，不背景重啟，不保證完成 |

補救最多每個 session 的同一使用者回合一次；切換任務也不重置。`stop_hook_active=true` 不再次延續；討論／等待／停止／取消／受阻時不自動實作。待查證操作只允許核對結果，不能直接重送。hook 不寫產品或合約，不取代主責 agent 的驗收判斷。

技術收據只去重補救嘗試，並非第二份任務狀態。收據已存在即不重送，即使先前輸出遺失；保存失敗只明示缺口，不以阻擋延續方式掩蓋錯誤，也不刪收據爭取重試。宿主不支援或 hook 執行失敗時可能無法強制攔截，因此不得把提醒或離線測試宣稱為完成保證。

## 驗收限制

離線檢查可驗證格式、分支、去重與封裝內容；實際執行環境的載入／信任、事件與補救鏈，以及真實 agent 對任務合約與成果的遵循，需各自取得直接證據。原生回合結束不等於整體任務完成，未驗證就明示未合格。

保存執行版本、候選指紋、模型／推理設定、實際載入來源與相關設定；只有核心版本、協定及相關設定等效有依據時才重用證據，差異按影響補驗，不為不同 UI 重做全套或宣稱未測環境已通過。不要求使用者計時、人工觀察或維護報表。評測、grader、OS 隔離與 watchdog 不屬於日常任務路徑。
