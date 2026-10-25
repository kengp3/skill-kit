# Personal Harness

透過 skill、hook 與少量工具，讓 AI agent 在原授權內完成嚴謹的多步驟開發，避免把局部成果當成整體完成。主責 agent 維護唯一任務合約，遇到真正阻礙或停止時保留可恢復狀態，跨對話續作先核對現況。使用者不必手動維護 tracker、計時或觀察。

首版以 Codex 的實際 agent 執行行為為驗收目標，不限定使用介面；重用既有 CLI／原生執行機制，評測工具留在開發端。本 repo 提供來源及離線候選，不會因開發自動改動全域設定、其他專案、既有啟用版本或快取。OS 隔離與 watchdog 不屬於本輪產品範圍。

## 本輪規格與使用方式

目前以[任務合約與必要 hooks 規格](docs/specs/task-harness-lifecycle.spec.md)、[整合計畫](docs/plans/task-harness-lifecycle.plan.md)及[用語](docs/specs/task-harness-glossary.spec.md)為準。舊版研究與試行結果保留作開發參考，不作本版實際行為合格證明。

完成專案接入後，使用者只需在任務開始時明確啟用一次：

> 使用 `$task-harness` 完成這項任務：……

同一任務的後續回合與明確續作沿用合約。跨對話時可提供原合約路徑；agent 先核對原執行狀態、產物與授權，再保存接手資訊。討論、等待決定或 Stop 不會自動轉成實作授權；未完成的必要成果不能自行降為後續建議。

[接入與合約指南](skills/task-harness/references/task-contract.md)提供完整 Markdown／JSON 範本、專案設定、綁定與恢復規則。首版以單一 Markdown 文件實作，原生 tracker 須具備完整保存、恢復及等效 hook adapter 才能替代。單獨載入 skill 不代表完整 harness 已接入。

## 必要接入與能力限制

- 必要 hooks 為 `SessionStart`（恢復）、`UserPromptSubmit`（最新要求核對）、`Stop`（最多一次有界收尾補救）。hook 不寫產品或合約，不取代授權與驗收，也不抵抗使用者 Stop。
- 專案明確 opt-in，設定及任務資料只在採用專案內。保留宿主要求的信任程序；不建立全域任務索引、不自動啟用其他專案。
- Python 3 標準函式庫為 script runtime；3.10+ 是相容目標，開發環境 3.15 不代表最低版本已實測。不硬編碼 Homebrew、不自動安裝 runtime。
- 設定中的 session 身分、使用者回合身分與 Stop 延續資格預設 `false`。離線 payload 或單元測試不構成真實事件證據；能力不足明示為缺口，不宣稱 hook 可選或已完整驗收。

本輪已有來源、離線驗證與候選封裝；完成項目與直接證據見[整合驗證報告](docs/research/task-harness-lifecycle-validation.research.md)。實際 agent 與 hook 整合仍待 [H05](docs/plans/task-harness-lifecycle-05-desktop.plan.md) 驗收，不再要求 Desktop 專屬驗證。不要求人工監看或新增例行核准點；低負擔需觀察，普遍省時效果不能由少量案例推定。

合約指南與來源候選已同步為 `0.2.1`，保留凍結候選 `0.2.0` 與其歷史證據。此次來源／封裝同步的[離線驗證](docs/research/h05-package-validation.research.md)不代表 H05A 的真實接入與補救已完成；尚未執行新 trial。

## 開發端離線候選

目前來源候選版本為 `0.2.1`。以既有 Python 工具建立不存在的目的地；保留原候選，以下命令只建包及驗證，不安裝或刷新宿主：

```sh
python3 -B scripts/package_harness.py dist/candidates/personal-harness-0.2.1
python3 -B scripts/package_harness.py --verify dist/candidates/personal-harness-0.2.1
```

完整包保留相依 skills、references、scripts、必要 hooks 與內容指紋；評測程式、grader、固定答案及研究留在開發 repo。更新／回退先保留可信 release 和指紋，再依明確採用授權處理來源及宿主快取；不要手改快取，也不要把某個來源版本當作目前活躍對話的載入證據。

既有 [N04／N06 離線交付](docs/research/codex-harness-p1-offline-20261024.research.md)、[CLI 三組 smoke](docs/research/codex-coding-harness-smoke-20261024.research.md)與[歷史接入查核](docs/research/codex-coding-harness-implementation.research.md)只支持其當時版本及範圍。舊 CLI 成功不等於新 hooks 或完整任務生命週期已合格，也不證明普遍更省時。日常任務不承擔三組比較或 grader 回放。

維護測試：`python3 -B -m unittest discover -s tests -p 'test_*.py'`。此指令使用開發案例，不能替代實際 agent 行為驗收；執行 trial 需有明確授權。

## 技能清單

| Skill | 用途 | 使用說明 |
| --- | --- | --- |
| [define-task](skills/define-task/SKILL.md) | 釐清模糊需求，整理目標、範圍與完成條件 | 請 AI 使用 `$define-task` 定義任務，無須初始化 |
| [project-setting](skills/project-setting/SKILL.md) | 管理專案文件的分類、命名與存放位置 | 請 AI 使用 `$project-setting` 初始化專案規範與提醒 |
| [ai-code-review](skills/ai-code-review/SKILL.md) | 審查功能、缺陷修正、重構與移轉 | 提供需求、目前產物與原始驗證證據；依風險啟用獨立 review |
| [task-harness](skills/task-harness/SKILL.md) | 唯一任務合約、持續推進、驗收與跨對話恢復 | 任務級明確啟用；完整接入包含三個必要 hooks |

`task-harness` 依需求使用同層 `define-task`，風險觸發時使用 `ai-code-review`；完整候選保留相依目錄。遠端已發布技能可能落後於本機來源，下列既有 Skills CLI 安裝方式不等於安裝本輪完整 harness，也不是 Python 候選的 runtime 需求。

## 其他獨立 skills 的既有發布方式

先安裝 Node.js（JavaScript 執行環境）與 npm（套件管理工具），以下指令以 Codex 為目標。

在要使用技能的專案目錄執行，依需求選擇其中一種：

```bash
# 安裝指定技能；可將 project-setting 換成 define-task
npx skills add kengp3/skill-kit --skill project-setting --agent codex

# 安裝全部技能到目前專案
npx skills add kengp3/skill-kit --skill '*' --agent codex

# 全域安裝全部技能，供不同專案使用
npx skills add kengp3/skill-kit --skill '*' --agent codex --global
```

預設為專案層級；加上 `--global` 則安裝至使用者層級。完成後可查詢安裝清單：

```bash
# 查看 Codex 已安裝的技能
npx skills list --agent codex

# 僅查看全域安裝
npx skills list --agent codex --global
```

## 如何移除

移除時使用技能名稱，範圍須與安裝時一致。專案層級請在原專案目錄執行；全域安裝加上 `--global`。

```bash
# 移除目前專案的指定技能
npx skills remove project-setting --agent codex

# 移除全域安裝的指定技能
npx skills remove project-setting --agent codex --global
```

可將 `project-setting` 換成 `define-task`。若兩個層級都有安裝，需分別移除；完成後可用上方清單指令確認。

**project-setting 需另行初始化專案，並完成 Hook（事件掛鉤）的信任設定；解除安裝技能不會自動移除專案提醒。** 停用方式見 [設定說明](skills/project-setting/references/configuration.md#停用)。

更多指令與參數見 [Skills CLI（命令列工具）官方文件](https://github.com/vercel-labs/skills)。
