# Kengp3 Harness

以模型能力推進已明確啟用的任務：主責 agent 維護唯一合約，拆解、派工、核對證據並完成原授權內的必要成果。設定集中於專案根目錄的 `project-setting.md`；核心不依賴 Python、Node.js、外部 CLI、MCP 服務或 runtime script。

本版來源為 `0.3.0`。以[統一設定與模型流程規格](docs/specs/unified-project-settings.spec.md)、[設定整合 ADR](docs/adr/0001-unified-project-settings.adr.md)及[用語](docs/specs/task-harness-glossary.spec.md)為準。[安裝與操作手冊](docs/specs/codex-coding-harness-guide.html)可離線閱讀。舊版候選與研究保留原狀，不能當成本版已完成實際行為驗收的證據。

## 在專案本地使用

不需要先執行建包腳本或 Skills CLI。取得本版來源或完整候選後，可用檔案管理員把所需 skill 目錄複製到專案的 `.agents/skills/`：

- 只使用文件規範：複製 `project-setting`。
- 使用完整 harness：一起複製 `task-harness`、`project-setting`、`define-task`、`ai-code-review`，保留各自 references 與 assets；task-harness 內含標準 hooks 範本與接入規格。scripts 是選配輔助；缺少時仍能使用核心流程。

已有同名技能先核對來源與版本，保留既有版本後再依授權升級，不把整個範本覆蓋到既有設定。重開專案工作階段並核對技能實際載入；只複製檔案不等於已驗證載入或行為。

單獨設定文件規範：

> 使用 `$project-setting` 初始化這個專案的文件規範。

指定包含 task-harness：

> 使用 `$project-setting`，包含 `$task-harness`，依 task-harness 提供的 Markdown 設定規格初始化這個專案；保留其他設定。

啟動任務：

> 使用 `$task-harness` 完成這項任務：……

安裝或初始化不會啟用所有任務。同一任務後續回合與明確續作沿用原合約；跨對話可提供原合約路徑。新任務不繼承舊授權或本次模型覆寫。

## 設定分工與升級

- project-setting 可獨立使用，只依指定規格執行設定。task-harness 隨技能提供[設定規格](skills/task-harness/references/project-settings.md)，自行定義欄位、預設值、有效性、移轉與修復。
- 專案長期設定只有 `project-setting.md`。文件分類表的 `task-contract` 與 `hook-receipt` 兩列是唯一路徑來源，移轉沿用既有位置。
- 發現舊 `harness-project.json` 時，先提示並依[移轉流程](skills/task-harness/references/settings-migration.md)操作。新值對帳、格式／內容驗證及目標版本正常讀回三項全過後，刪除舊檔、不留備份；失敗或衝突保留原檔並回報。
- 舊環境資格只留歷史資料；新流程依實際診斷判定。設定移轉與宿主信任／環境資格分別回報，不增加刪除舊設定的門檻。
- 原授權內主動診斷與修復；需要人工操作、內容決策或超出授權才回報相依缺口。唯讀、討論限定與使用者 Stop 仍有效。

## Hooks 與模型接手

[標準 hooks](skills/task-harness/assets/codex-hooks.json)隨 skill 提供，plugin 由同一份資源建包。它只用系統 shell 內建 `echo` 輸出固定內容，不解析事件、不讀寫設定或合約，也不執行外部 helper：

| 事件 | 本版行為 |
| --- | --- |
| SessionStart | 提醒已明確啟用的任務讀取專案設定、恢復同一合約並核對現況 |
| UserPromptSubmit | 提醒核對最新要求，以及派工／階段前、agent 回報後、收尾前的共同檢查 |
| Stop | 回傳合法的空 JSON 物件 `{}`；為被動回應，不提供條件式阻擋或一次性補救 |

提醒只傳遞要求，不能宣稱已機械驗證合約或保證完成。主責模型一直負責[四個檢查時點](skills/task-harness/SKILL.md#check-the-same-contract-at-workflow-boundaries)。hooks 無法使用時先診斷並嘗試修復，仍不可用則自動以同一合約主動檢查並繼續；恢復後銜接目前進度，不重做操作或重複派工。未知結果先查明，條件改變才重驗。

本地 skill 安裝可請 project-setting 依[隨附接入規格](skills/task-harness/references/project-settings.md#codex-標準-hooks-接入)把對應 hooks 合併到專案設定，保留其他 handlers 並避免重複來源；已由 plugin 提供相同事件與 handler 時沿用，不建立副本。Codex 的啟用與信任依宿主正常流程處理；「已寫入、已載入、已信任、已執行」分別回報。測試 automation 的單次信任略過不等於正常信任驗收。

## 模型分工

[模型選擇與回退規則](skills/task-harness/references/model-selection.md)支援規劃、執行、驗證、審查與自訂階段；不要求任務走完全部階段，也不預綁模型。設定值例如 `[模型A;high, 模型B;medium]`，由左至右嘗試；省略強度時使用宿主對該模型的預設。

優先序為本次明確指定、任務、agent 角色、階段、專案預設；皆未設定才沿用主責。候選耗盡自動回退專案預設，沒有專案預設才沿用主責，無需填 default；同模型不重複嘗試。強度不支援時優先保留模型並用宿主預設，明確禁止變更時遵守限制。

主責維持對話選定模型，不因階段自行切換。手動切換對話模型只影響後續真正繼承主責的派工，已啟動 agent 維持原設定。單次指定只記錄於該任務合約；只有明確要求設為專案預設才更新長期設定。

無法建立子 agent 時先診斷，仍不可用由主責循序接手並記錄實際執行者與模型。明確要求獨立審查的條件不能用自我檢查完成，須保留未完成並回報，其他工作繼續。請求模型、宿主解析值與實際可觀測結果分開記錄，未知值不編造。

## 開發端封裝與驗證

下列 Python 命令僅供維護者建包及查核，不是使用者安裝或日常使用前提。使用不存在的目的地，不覆寫既有候選：

```sh
python3 -B scripts/package_harness.py dist/candidates/kengp3-harness-0.3.0
python3 -B scripts/package_harness.py --verify dist/candidates/kengp3-harness-0.3.0
python3 -B -m unittest discover -s tests -p 'test_*.py'
```

新包包含四個 skills、其 references／assets、選配 helpers、標準 hooks 與內容指紋。舊 Python hook handler 不再是封裝輸入或日常入口；其來源與舊測試僅留作歷史開發對照。單元測試與建包通過不取代 A–G 的真實 agent 行為驗收。

既有本機 marketplace 指向 `dist/kengp3-harness`，可能仍是舊候選；建包不會更新它、註冊 marketplace、修改宿主快取或全域安裝。需要 native plugin 安裝時，先明確選擇候選與安裝範圍，再依宿主支援的 marketplace 流程操作並核對實際載入版本；不要手改快取。隔離驗收使用獨立 state、catalog 與 project。

## 停止、停用與移除

使用者 Stop 結束執行，明確續作後才恢復；不能為補寫合約而抵抗停止。取消保留依據與既有成果，不等於驗收成功。

停用／升級只處理指定專案與可辨識來源。請 agent 保留任務合約、設定、證據與其他 handlers；移除本地 skill 目錄和停用專案 hooks 是不同動作。其他安裝方式與完整檢查見[手冊](docs/specs/codex-coding-harness-guide.html)。

## 技能清單

| Skill | 用途 |
| --- | --- |
| [define-task](skills/define-task/SKILL.md) | 定義目標、範圍與完成條件 |
| [project-setting](skills/project-setting/SKILL.md) | 文件規範與依提供規格執行設定 |
| [task-harness](skills/task-harness/SKILL.md) | 唯一任務合約、持續推進、模型分工與恢復 |
| [ai-code-review](skills/ai-code-review/SKILL.md) | 依需求、產物與直接證據審查品質與風險 |

遠端已發布版本可能落後於本地來源。既有 `npx skills add`／`list`／`remove` 是選用的第三方安裝方式，需要其自身 Node.js 環境；它不是本版核心的必要依賴，也不證明已安裝本輪完整候選。
