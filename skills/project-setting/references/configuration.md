# 設定與驗證

## 文件規範

規範只維護在已確認專案根目錄的 `project-setting.md`，初始化採用 `assets/document-rules.md`。不存在時才建立，已存在時先讀取並保留自訂內容。新初始化不建立或修改 AGENTS.md／CLAUDE.md；平台適用指令仍須遵循，若與文件規範衝突，按指令優先序處理並說明。
使用現有檔案工具編輯，不要求版本檢查或安裝 Python、Git、Node.js。不要為了合併幾段設定引入新的安裝程式。

從子目錄工作時，AI 依使用者指定或工作階段已確認的專案根目錄讀取 project-setting.md，不以工具 cwd、Git 或 AGENTS.md 猜根目錄。根目錄不明時先詢問，不無界向上搜尋；巢狀與多專案各自確認，不套用其他專案規範。檔案缺失、空白、不可讀或規則衝突時，暫停相關文件寫入並回報；修改後重讀。Hook 本身不查檔、不定位根目錄，也不保證 AI 遵循。

## Codex（預設主要平台）

1. 讀取專案 `.codex/hooks.json` 與 `.codex/config.toml`。如果已有內嵌 `[hooks]`，沿用 TOML 儲存位置，將範本同等欄位併入；同一層不要同時新增 JSON 與內嵌 Hook。兩者已並存時先釐清有效來源，不覆蓋任何一份。
2. 把 [Codex 範本](../assets/codex-hooks.json) 的 `SessionStart`、`SubagentStart` 群組合併到既有 hooks 陣列。新事件可直接新增，已有事件保留其他 handlers。完整相同的本技能 handler 已存在就不追加。
3. 保留其他設定。依初始化的啟用意圖設定 `[features]` 下 `hooks = true`，不建立第二個重複區段；若原值為 false，明確回報此變更。使用者明確要求維持停用時不得覆蓋。
4. 到 `/hooks` 審查並信任新增定義，重開工作階段確認載入。若需要使用者在介面完成信任，交付具體檔案與操作位置，將「設定已寫入」與「信任／載入已確認」分開回報。

範本不設 matcher，讓 SessionStart 涵蓋開始、恢復與 compact（上下文壓縮）等來源；不新增 PreToolUse。兩個事件皆可直接輸出文字，無須解析輸入或生成動態 JSON。

macOS/Linux 使用 shell 內建 `echo`；Windows 以 `commandWindows` 指定 `cmd /d /c echo`，只需系統 cmd.exe。提醒使用 ASCII，避開中文命令編碼問題。不得在命令中插入使用者路徑、文件內容或其他可執行字串；實際規範由 AI 讀取。

## Claude（使用者要求時才安裝）

1. 直接使用同根 `project-setting.md`，不建立或修改 CLAUDE.md，也不需要 AGENTS.md 引用。
2. 將 [Claude 範本](../assets/claude-hooks.json) 合併至 `.claude/settings.json`，保留 env、permissions 與其他 Hook，不安裝 Codex 設定。
3. 範本使用 shell 的 `echo` 輸出靜態 JSON；SubagentStart 需透過 `additionalContext` 注入上下文，不能直接套用 Codex 的純文字輸出。依 Claude 宿主提供的 shell 執行，未聲稱 Windows 可直接使用 cmd 執行此範本。
4. 重新載入／開始工作階段並查核設定是否生效。此平台仍屬選用且未完成模型端實測。

## 停用

1. 確認使用者指定的專案，讀取平台設定，修改前備份到不覆蓋既有資料且不越界的位置。
2. 只移除與本技能 assets 範本完整相同的提醒 handler（事件處理項目）；自訂過的命令先確認歸屬。混合群組保留其他 handler，只刪除因此變空的群組，不清空整個 hooks，也不關閉全域 Hook 功能。
3. 預設保留 project-setting.md 與所有實際文件；只有使用者明確要求同時移除規範時，才備份並移除該檔。其他平台指令與設定保持不變。
4. 回讀差異，重新開始工作階段確認提醒已停用；未完成平台檢查時明確回報。解除安裝技能與停用專案提醒是兩個獨立動作。

## 驗證與完成回報

- 回讀 project-setting.md、平台設定，確認規範完整可讀、沒有重複提醒，其他內容未變。
- 在命令執行環境回放兩個事件的 handler，檢查成功輸出規範提醒且未改寫任何檔案。這只證明命令可用，不等於 AI 已收到或遵循。
- 在新工作階段確認 Hook 載入與輸出；若未授權或無法執行子代理，不為驗證額外建立子代理，明確列為未驗證。
- 在隔離測試目錄提供相同規範，要求建立一份 plan、讀取並修改；確認實際檔名與連結正確、原文保留。再提供用途不明或已有同名文件的案例，檢查是否先釐清／讀取，而非覆寫。
- 平台實測要使用真正模型與工具操作；人工或腳本回放不能充當 AI 行為驗收。沒有完成時列為未驗證。

## 支援邊界與證據

本技能僅提供規範與提示，不強制阻擋、修改工具參數或保證外部腳本／所有檔案寫入皆符合規範。缺少 project-setting.md 時提醒仍會輸出；AI 必須回報規範缺失，不能宣稱 Hook 已載入規範全文。

維護者測試使用 Python 標準函式庫，僅驗證發行資源與原生命令，不構成技能使用者的 Python 依賴。實際驗證結果記錄於儲存庫 `tasks/plan.md`；安裝此技能不需要該文件。原生 Windows、Codex 模型端及 Claude 模型端須分開驗證。

官方文件查證於 2026-09-15：
- [Codex Hooks](https://learn.chatgpt.com/docs/hooks)：SessionStart／SubagentStart 純文字上下文、commandWindows、信任、設定來源。
- [Claude Hooks](https://code.claude.com/docs/en/hooks)：SessionStart 與 SubagentStart 的輸出格式及設定。
