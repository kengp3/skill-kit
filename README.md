# skill-kit

個人維護的 Skills（AI 技能）集合。每個技能可獨立安裝、使用；透過 `npx skills add` 選擇需要的技能，也可一次安裝全部。

## 技能清單

| 技能 | 用途 | 額外需求 |
| --- | --- | --- |
| [define-task](skills/define-task/SKILL.md) | 釐清模糊或高返工成本的任務，整理目標、背景、材料、邊界與完成條件 | 無額外執行依賴或初始化步驟 |
| [project-setting](skills/project-setting/SKILL.md) | 管理專案文件位置與命名，支援 PRD、spec、plan、ADR、research 及自訂類型 | 無 Python／Git 執行依賴；文字規範＋系統命令提醒；Codex Hook 需逐專案初始化與信任 |

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

**移除 `project-setting` 技能不會自動清除專案 Hook 或規範。** 若要停用提醒，請要求 AI 使用技能的 [停用流程](skills/project-setting/references/configuration.md#停用)，只移除本技能的提醒註冊，保留其他 Hook；文件規範保留，除非你也要求移除。實際文件不會自動刪除。

## 使用 define-task

安裝後可請求：

> 使用 $define-task，幫我把這個需求整理成可以交給 AI 或同事執行的任務摘要。

技能會先判斷目前是思考、探索、決策或執行階段，再決定是否需要完整摘要；單純文字潤飾不會自動擴充為任務定義。它可獨立使用，不依賴 project-setting，也不會安裝 Hook。

## 使用 project-setting

安裝後在 Codex 請求：

> 使用 $project-setting 初始化這個專案的文件規範，採用預設類型，並設定 Codex Hook。

技能會在專案根目錄建立獨立 `project-setting.md`，不建立或修改 `AGENTS.md`／`CLAUDE.md`，並合併 SessionStart／SubagentStart 提示型 Hook。Hook 直接提醒 AI 讀取 `project-setting.md`，不自動阻擋或改寫文件路徑，使用者仍需在 Codex 的 `/hooks` 審查並信任定義。**安裝技能不等於已啟用 Hook；安裝全部技能也不會自動替所有專案寫入設定。** 根目錄不明或規範缺失／空白／衝突時，由 AI 暫停相關文件寫入並回報；Hook 本身不偵測或硬性阻擋。詳見 [設定說明](skills/project-setting/references/configuration.md)。

Codex／Claude 模型端及原生 Windows 尚未完成驗收；命令回放結果與未驗證項目見 [驗證紀錄](tasks/plan.md#驗證紀錄)。

## 新增技能

- 每個技能放在 `skills/<name>/`，`SKILL.md` 的 frontmatter（檔頭中繼資料）包含同名 `name` 與明確的 `description`。
- 只有實際需要時才增加 `scripts/`、`references/` 或 `assets/`；執行所需資源留在技能內，不依賴儲存庫根目錄或其他未安裝技能。
- 在技能中寫清楚執行需求與額外初始化步驟，並更新上方清單。
- `docs/` 保存開發規格、計畫與研究；`tests/` 保存維護者測試。使用者執行技能不應依賴這兩個目錄。

## 開發驗證

```bash
python3 -B -m unittest discover -s tests -v
```

以上 Python 僅供維護者執行測試，不是技能或 Hook 的執行依賴。發布前另以乾淨專案驗證清單、指定與全部安裝，以及安裝後的實際功能。設計與驗證見 [計畫](tasks/plan.md)。
