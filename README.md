# Kengp3 Harness

四個 AI agent skills，協助定義任務、管理專案規範、推進工作與審查程式碼。

## 技能介紹

| Skill | 用途 |
| --- | --- |
| [define-task](skills/define-task/SKILL.md) | 釐清目標、範圍、材料與完成條件，產出可執行的任務摘要 |
| [project-setting](skills/project-setting/SKILL.md) | 管理文件位置與命名規範，依提供的規格初始化或更新專案設定 |
| [task-harness](skills/task-harness/SKILL.md) | 透過唯一任務合約追蹤進度、協調工作、核對成果並支援續作 |
| [ai-code-review](skills/ai-code-review/SKILL.md) | 審查變更、需求覆蓋與驗證證據，提出具體問題及修正建議 |

## 安裝

以下以 Codex 的專案本地安裝為例：

1. 下載或 clone 本 repository。
2. 將 `skills/` 下所需的完整技能目錄複製到目標專案的 `.agents/skills/`，保留目錄內的附屬資源。
3. 確認技能出現在 Codex 的可用清單；未出現時重新啟動 Codex 後再檢查。

只需文件規範時，可單獨安裝 `project-setting`；使用完整 harness 時，請一起安裝四個技能：

```text
你的專案/
└── .agents/
    └── skills/
        ├── define-task/
        ├── project-setting/
        ├── task-harness/
        └── ai-code-review/
```

每個技能目錄內都應有 `SKILL.md`。已有同名技能時，先核對版本並保留自訂內容，再更新。

此安裝方式不需要先建包或安裝 Python／Node.js；實際開發與驗證所需工具依任務而定。其他載入位置見 [OpenAI 官方 Skills 說明](https://learn.chatgpt.com/docs/build-skills#where-codex-loads-local-skills)。

## 使用方式

先初始化專案文件規範：

> 使用 `$project-setting` 初始化這個專案的文件規範；保留既有自訂設定。

若要使用完整 harness，改用：

> 使用 `$project-setting`，包含 `$task-harness`，依 task-harness 提供的設定規格初始化這個專案；保留既有自訂設定。

接著依需要指定技能：

- **釐清需求**：使用 `$define-task`，整理這項工作的目標、範圍與完成條件。
- **執行任務**：使用 `$task-harness` 完成這項任務：……
- **審查變更**：使用 `$ai-code-review` 審查目前尚未提交的變更。

專案規範保存在根目錄的 `project-setting.md`。安裝技能不會自動啟動任務；續作時沿用原任務合約，跨對話可提供原合約路徑。

詳細設定與操作見[安裝與操作手冊](docs/specs/codex-coding-harness-guide.html)，下載後可離線閱讀。
