# skill-kit

個人維護的 Skills（AI 技能）集合。每個技能可獨立安裝、使用；透過 `npx skills add` 選擇需要的技能，也可一次安裝全部。

## 技能清單

| 技能 | 用途 | 額外需求 |
| --- | --- | --- |
| [define-task](skills/define-task/SKILL.md) | 釐清模糊或高返工成本的任務，整理目標、背景、材料、邊界與完成條件 | 無額外執行依賴或初始化步驟 |
| [project-setting](skills/project-setting/SKILL.md) | 管理專案文件位置與命名，支援 PRD、spec、plan、ADR、research 及自訂類型 | Python 3.9+、Git、macOS/Linux；Codex Hook 需逐專案初始化與信任 |

## 如何安裝

需要 Node.js 與 npm。儲存庫：[kengp3/skill-kit](https://github.com/kengp3/skill-kit)。

在要使用技能的專案內執行：

```bash
# 互動安裝；多個技能時可選擇清單
npx skills add kengp3/skill-kit --agent codex

# 僅列出可用技能
npx skills add kengp3/skill-kit --list

# 安裝指定技能
npx skills add kengp3/skill-kit --skill project-setting --agent codex

# 安裝全部技能到 Codex
npx skills add kengp3/skill-kit --skill '*' --agent codex
```

預設安裝到目前專案；要安裝到使用者層級可加 `--global`。互動安裝時可選擇需要的技能，也可透過 `--skill define-task` 僅安裝任務定義技能。參數詳見 [Skills CLI 官方文件](https://github.com/vercel-labs/skills)。

```bash
# 全域安裝全部技能，供不同專案使用
npx skills add kengp3/skill-kit --skill '*' --agent codex --global

# 安裝後確認 Codex 的已安裝技能與位置
npx skills list --agent codex

# 僅查看全域安裝
npx skills list --agent codex --global
```

本機開發時，可在另一個暫存專案用儲存庫的實際路徑驗證：

```bash
npx skills add /absolute/path/to/skill-kit --list
npx skills add /absolute/path/to/skill-kit --skill project-setting --agent codex
```

## 如何移除

專案層級的技能，請在當初安裝的專案目錄執行；全域安裝則加上 `--global`。移除時使用技能名稱，而非儲存庫名稱。

```bash
# 移除指定技能
npx skills remove project-setting --agent codex

# 移除本集合的兩個技能
npx skills remove define-task project-setting --agent codex

# 移除全域安裝的兩個技能
npx skills remove define-task project-setting --agent codex --global

# 移除後確認剩餘技能與安裝位置
npx skills list --agent codex
```

以上為不同移除範例，依安裝範圍選擇執行；若專案與全域都有安裝，需分別移除。參數詳見 [Skills CLI 移除文件](https://github.com/vercel-labs/skills#skills-remove)。

**移除 `project-setting` 技能不會自動清除已初始化的專案 Hook。** 安裝器已將執行腳本複製到各專案的 `.project-setting/runtime/`，並寫入 Hook 註冊與專案指令。若也要停用文件路由，需逐專案移除 `.codex/hooks.json` 中指向 `.project-setting/runtime/hooks.py` 的 Hook，以及 `AGENTS.md` 中本技能加入的指引；保留其他 Hook 與指令。曾整合 Claude Code 的專案，則檢查 `.claude/settings.json` 與 `CLAUDE.md`。

目前沒有自動清理整套專案設定的移除指令。`project-setting.json`、`.project-setting/` 中的路由狀態與既有文件不會由上述技能移除指令刪除；停用整合後應開啟新工作階段確認不再載入。詳細設定見 [project-setting 設定說明](skills/project-setting/references/configuration.md)。

## 使用 define-task

安裝後可請求：

> 使用 $define-task，幫我把這個需求整理成可以交給 AI 或同事執行的任務摘要。

技能會先判斷目前是思考、探索、決策或執行階段，再決定是否需要完整摘要；單純文字潤飾不會自動擴充為任務定義。它可獨立使用，不依賴 project-setting，也不會安裝 Hook。

## 使用 project-setting

安裝後在 Codex 請求：

> 使用 $project-setting 初始化這個專案的文件規範，採用預設類型，並設定 Codex Hook。

技能會建立根目錄 `project-setting.json`，並將 Hook（事件掛鉤）整合到該專案。使用者仍需在 Codex 的 `/hooks` 審查並信任定義。**安裝技能不等於已啟用 Hook；安裝全部技能也不會自動替所有專案寫入設定。** 詳細流程與限制見技能內的 [設定說明](skills/project-setting/references/configuration.md)。

`project-setting` 原名 `project-conventions`。新版本使用 `project-setting.json` 與 `.project-setting/`，沒有自動遷移舊專案設定或 Hook。曾使用舊版的專案，應先保留原設定與路由狀態，完成專案層級遷移後再啟用新版，避免兩套路由器並存。

## 新增技能

- 每個技能放在 `skills/<name>/`，`SKILL.md` 的 frontmatter（檔頭中繼資料）包含同名 `name` 與明確的 `description`。
- 只有實際需要時才增加 `scripts/`、`references/` 或 `assets/`；執行所需資源留在技能內，不依賴儲存庫根目錄或其他未安裝技能。
- 在技能中寫清楚執行需求與額外初始化步驟，並更新上方清單。
- `docs/` 保存開發規格、計畫與研究；`tests/` 保存維護者測試。使用者執行技能不應依賴這兩個目錄。

## 開發驗證

```bash
python3 -m unittest discover -s tests -q
```

發布前另以乾淨專案驗證清單、指定與全部安裝，以及安裝後的實際功能。技能更新不會自動更新已複製到其他專案的 Hook runtime（執行腳本）；目前尚未提供完整的專案 Hook 移除與舊版遷移流程。
