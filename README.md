# skill-kit

個人維護的 Skills（AI 技能）集合，每個技能皆可獨立安裝與使用。

## 技能清單

| Skill | 用途 | 使用說明 |
| --- | --- | --- |
| [define-task](skills/define-task/SKILL.md) | 釐清模糊需求，整理目標、範圍與完成條件 | 請 AI 使用 `$define-task` 定義任務，無須初始化 |
| [project-setting](skills/project-setting/SKILL.md) | 管理專案文件的分類、命名與存放位置 | 請 AI 使用 `$project-setting` 初始化專案規範與提醒 |

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
