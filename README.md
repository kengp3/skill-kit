# Personal Harness

個人 AI coding harness 的來源與整合 repo。首版以 Codex 處理既有專案的 bug、功能與重構，目標是在維持交付品質下減少人工投入與返工。個別 skill 依其相依內容使用；完整配置另包含發佈內容、專案啟用與驗證機制。

## 本機 Codex runtime（開發中）

唯一來源仍是 `skills/`。使用 Python 3 標準函式庫建立獨立套件，不需要 npm：

```sh
python3 -B scripts/package_harness.py dist/personal-harness
python3 -B scripts/package_harness.py --verify dist/personal-harness
```

目的地必須不存在，腳本不覆寫舊版。套件含四個技能、其 references／assets／scripts 及內容指紋，排除 repo 文件、研究、grader 與答案。`--verify` 檢查缺檔、變更及額外檔案並輸出 manifest SHA-256；更新／回退應與先前保存的可信指紋比對，manifest 自身不是簽章。

`.agents/plugins/marketplace.json` 提供 `personal-harness-local` 來源，指向上述生成物。先以原生命令註冊共用來源（不執行 `plugin add`）：

```sh
codex plugin marketplace add /Users/kengp3/Workspaces/mine/simple-skills
```

採用專案須受宿主信任，在 `.codex/config.toml` 明確設定：

```toml
[plugins."personal-harness@personal-harness-local"]
enabled = true
```

保留使用者層級無候選 plugin 啟用項目，只有採用專案明確啟用。先檢查既有設定，合併指定區塊，不覆寫整份 config。原生 app-server 也會為明確設定 `enabled = false` 的專案準備快取，可用於先準備而不載入。新 session 核對實際快取包、manifest 指紋與技能入口；停用改為 `false` 並驗證不再載入。其他已安裝的同名 skill 副本不會隨 repo 自動更新，應核對實際選用路徑。

已用 Desktop 內附 `0.163.0-alpha.11.2` app-server 驗證快取準備、專案啟停、更新及回退；正式來源註冊後無命令列覆寫也可運作。原生技能清單顯示本 repo 啟用時載入 4 個候選技能，未採用的 demo-002 為 0；停用後本 repo 也為 0。目前本 repo 明確啟用 `0.1.0` 作開發使用。這些是原生引擎證據，尚未宣稱 Desktop 主視窗的活躍對話已使用新版完成任務。參見[實作查核紀錄](docs/research/codex-coding-harness-implementation.research.md)。

更新先保留舊 release 與可信 manifest 指紋，再用新的不存在目錄建包、驗證，讓 marketplace source 指向新 release 並由宿主刷新。回退將 source 指回舊 release，再核對快取與技能路徑。這次實測快取目錄使用 `0.1.0`／`0.1.1`；不要假設固定叫 `local`，也不要只靠版本目錄名稱驗收。宿主可能移除已不用的舊快取，因此可信 release 要另外保留。不要直接刪除目前套件來更新，也不要手改快取。

本版沒有新增強制 hook：repo `.codex/hooks.json` 仍只是文件規則提醒。必要權限與副作用控制重用宿主及專案關卡，必須依實際工具路徑驗證；控制不足時停止相依操作。本機首版已以內附 CLI 完成 A／B／C 各一次流程 smoke：凍結版外部驗收均通過，另有 B 交付後死鎖診斷與 C controller 故障續作，完整保留於[交付報告](docs/research/codex-coding-harness-smoke-20261024.research.md)。目前 0.164 亦已重驗啟停、更新及回退。Desktop 主視窗 Stop、人工效益、公平能力比較與其他宿主仍未合格；本輪結果不代表新版普遍更好或更省時。

專案資料沿用其 AGENTS、建置設定與既有命令；[試行計畫](docs/plans/codex-coding-harness-pilot.plan.md)列出 demo-002 候選入口及限制，不把未執行命令寫成已通過。維護測試：`python3 -B -m unittest discover -s tests -p 'test_*.py'`。

平台依據：[Codex plugin 封裝與接入](https://developers.openai.com/plugins/build/plugins)、[hooks 的信任及覆蓋限制](https://learn.chatgpt.com/docs/hooks)。

## 技能清單

| Skill | 用途 | 使用說明 |
| --- | --- | --- |
| [define-task](skills/define-task/SKILL.md) | 釐清模糊需求，整理目標、範圍與完成條件 | 請 AI 使用 `$define-task` 定義任務，無須初始化 |
| [project-setting](skills/project-setting/SKILL.md) | 管理專案文件的分類、命名與存放位置 | 請 AI 使用 `$project-setting` 初始化專案規範與提醒 |
| [ai-code-review](skills/ai-code-review/SKILL.md) | 審查功能、缺陷修正、重構與移轉，提供問題、修改方向及驗收證據 | 提供 repo、審查版本與需求；移轉時另提供兩側 repo/ref |
| [task-harness](skills/task-harness/SKILL.md) | 以風險驗證與直接證據完成開發、協調及續作 | 小任務直接交付；依接續需要才建立清單與持久紀錄 |

本機的 ai-code-review（由 migration-code-review 擴充並更名）尚未推送；可直接指定本機 SKILL.md 使用。下列遠端安裝指令只取得遠端已發布內容。

`task-harness` 本機新版可直接指定 `skills/task-harness/SKILL.md`，尚未發布至遠端。缺少需求時會按需使用同層 `define-task`，風險觸發獨立 review 時使用同層 `ai-code-review`；單獨攜帶此 skill 時須一併保留這兩個完整相依目錄。上述完整 plugin 已包含它們。

## 如何安裝

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
