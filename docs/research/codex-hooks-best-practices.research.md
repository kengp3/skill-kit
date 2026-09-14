# Codex Hooks 實作與包裝研究

查證日期：2026-09-15。範圍：官方文件與目前程式的唯讀比對；未修改產品、安裝插件或重新執行整合測試。

## 結論

**目前採用 Skills 集合分發：透過 `npx skills add` 選擇或全部安裝，project-setting 是其中一個獨立技能。** 安裝技能後，再由該技能在目標專案初始化設定與 Hook。依據 [Skills CLI 官方說明](https://github.com/vercel-labs/skills)，不需要自製選單或 npm 套件。

以下 Plugin（可安裝套件）方案保留為替代研究，不是目前實作計畫；原先針對跨專案重用的推薦，已由使用者的 Skills 集合分發需求取代。

`hooks/` 有意義的前提是它位於可被發現的 Plugin 內。單純把 `scripts/hooks.py` 移到名為 `hooks` 的資料夾，不會解決發現、信任與啟用問題。

## 官方規格摘要

- 專案可用 `.codex/hooks.json` 或 `config.toml` 內的 `[hooks]`；同層擇一。各來源會合併，匹配的命令 Hook 並行執行。專案層須受信任，Hook 定義也須經 `/hooks` 審查。[Hooks：來源與信任](https://learn.chatgpt.com/docs/hooks#where-codex-looks-for-hooks)
- 路由使用同步 `PreToolUse`；`updatedInput` 搭配 `permissionDecision: "allow"`。`apply_patch` 使用字串 `command`。`ask` 尚不支援，會報錯並繼續工具；背景 Hook 無法改寫，`PostToolUse` 無法撤銷已發生的寫入。[Hooks：輸入改寫](https://learn.chatgpt.com/docs/hooks#pretooluse)、[背景執行](https://learn.chatgpt.com/docs/hooks#run-hooks-in-the-background)
- Hook 不是完整強制邊界；`write_stdin` 不重新觸發前置檢查。[工具涵蓋範圍](https://learn.chatgpt.com/docs/hooks#tool-coverage)
- 新套件指南採根目錄 `plugin.json`，Hook 宣告位於 `extensions.com.openai.hooks`；預設尋找 `hooks/hooks.json`。`.codex-plugin/plugin.json` 是仍支援的相容形式。顯式 Hook 宣告會取代預設發現；宣告路徑須以 `./` 起始並留在套件內。[Plugin 封裝指南](https://developers.openai.com/plugins/build/plugins)
- Plugin Hook 有 `PLUGIN_ROOT`（安裝程式位置）與 `PLUGIN_DATA`（可寫資料位置）；安裝並不自動信任 Hook，執行環境也必須已有腳本。[Plugin bundled hooks](https://developers.openai.com/plugins/build/plugins#hooks)

## 替代 Plugin 方案的最小結構

以下僅為未採用的 Plugin 提案，並非本專案目前目錄：

```text
project-setting/
├── plugin.json
├── hooks/
│   └── hooks.json
├── scripts/
│   ├── conventions.py
│   └── hooks.py
└── skills/
    └── project-setting/
        ├── SKILL.md
        └── references/configuration.md
```

`hooks/hooks.json` 負責事件宣告，Python 程式仍可留在 `scripts/`。命令建議為 `python3 "${PLUGIN_ROOT}/scripts/hooks.py" hook --platform codex`；腳本從事件 `cwd` 找目標專案，不能把 Plugin 安裝目錄當成使用者專案。保留根目錄 `project-setting.json` 作專案真實規範，避免將它移入全域 Plugin 資料區。

新格式示意：

```json
{
  "$schema": "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json",
  "name": "project-setting",
  "version": "0.1.0",
  "description": "專案文件位置與命名規範",
  "extensions": {
    "com.openai": {
      "hooks": "./hooks/hooks.json"
    }
  }
}
```

這是封裝提案，尚未以本機 Codex 版本驗收。若目標版本不支援新格式，可使用官方仍支援的相容 manifest；不要未經驗證同時維護兩份宣告。

## 對現有實作的判斷

目前 `skills/project-setting/scripts/hooks.py` 的 `install()` 會複製 runtime 到每個目標專案、合併 `.codex/hooks.json`，並補入專案指令。這是有效的專案本地安裝策略；缺點是每個專案各有一份程式，更新、移除及避免重複註冊都由自製安裝器負責。

採 Plugin 後建議保留核心解析器，讓平台負責分發程式；初始化 Skill 只管理專案設定與啟用狀態。遷移時僅移除本套件原先加入的註冊，保留其他 Hook。避免舊專案 Hook 與 Plugin Hook 同時處理同一寫入。

現有 `PreToolUse` 已採 `allow + updatedInput` 並附實際路徑，與本用途相符。仍應以完整工具參數為輸入，只改必要路徑，不改文件正文或擴大寫入範圍；路徑越界、同名覆寫、多檔案衝突在改寫前驗證。回傳改寫不等於寫入已成功。

## 專案啟用與未知分類

Plugin 可能在多個專案被載入，不能把「沒有設定」一律當成略過，也不能在每個無關專案都要求初始化。建議分清兩個狀態：

1. **未啟用規範的專案**：不改寫、不提示初始化；由使用者明確啟用。
2. **已啟用的專案**：缺設定、無匹配或多重匹配時，停止該次受管文件寫入，回報候選類型，讓 Agent 詢問使用者，再接續原工作。

啟用狀態需獨立於設定檔存在與否，例如專案本地的啟用標記；具體儲存方式待遷移設計確定。使用者已授權初始化該專案時，即可進入第二種狀態。一次性位置仍只能影響該文件，不可自動變成永久匹配規則。

## 實作建議與驗收重點

- **事件保持最少**：SessionStart／SubagentStart 提供短指引；同步 PreToolUse 做精確路由。沒有實際事後工作時，不加 PostToolUse、Stop 或背景程序。
- **縮小匹配範圍**：先支援已驗收的 `apply_patch`；Bash 只在需要時給指引，不靠字串取代偽裝成任意 shell 輸出路由。
- **不依賴 Hook 順序**：只設一個路由處理者；共享狀態採鎖及原子更新。檢查器不應因自己沒有改寫就將其他檢查視為已通過。
- **診斷要有用**：設定有限 timeout，輸出只含需要的分類、路徑及錯誤；避免每次 Bash 重複整份規範，也不要輸出憑證或完整聊天紀錄。
- **保持權限流程**：不用 PermissionRequest 自動批准路由；不把 trust bypass 放進正常安裝流程。
- **實測重點**：乾淨專案安装、正常信任、子目錄與 worktree、未啟用略過、已啟用缺設定詢問、第三方 Skill 建立後讀寫、碰撞、更新與卸載、舊註冊共存偵測。

## 尚未確定的部分

官方 Hook 頁的 Plugin 段仍使用相容 manifest，新封裝指南則推薦根目錄 manifest；本研究以後者決定新套件方向，但不宣稱目前本機版本已支援。另未從本次資料確認多個同步 Hook 同時回傳不同 `updatedInput` 的合併規則，因此設計上避免依賴它。這些須在正式轉換前以指定 Codex 版本做小型驗收。
