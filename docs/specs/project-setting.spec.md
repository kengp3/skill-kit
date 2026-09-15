# 專案文件規範技能

## 目標

以文字規範與提示型 Hook 管理 AI 產生文件的位置。技能與 Hook 不依賴 Python 或 Git。規範唯一來源為已確認專案根目錄的 project-setting.md；兩平台 Hook 直接指向它，新初始化不建立或修改 AGENTS.md／CLAUDE.md，平台適用指令仍須遵循。

## 行為

- 五類預設 prd、spec、plan、adr、research，支援自訂用途與路徑。一般任務不要求產生所有文件類型。
- 文件操作前實際讀取獨立規範，修改後重讀。根目錄不明、規範缺失／空白／不可讀／衝突時由 AI 暫停相關寫入並回報，不無界向上搜尋或套用另一專案規範；Hook 不自動查檔。
- project-setting.md 本身不套用一般分類，不能被搬入 docs。
- AI 依用途分類；分類、名稱或編號不明先問一個關鍵問題，一次性位置不改寫永久規範。
- 寫入前核對根目錄、目的地、衝突與符號連結；既有文件不自動搬移或覆寫。完成後讀回，連結與後續工具操作使用實際位置。
- 規範與平台設定由 AI 使用現有檔案工具維護，保留已有內容，重複初始化不覆蓋自訂規則或重複註冊。
- 只有 SessionStart、SubagentStart 提示型 Hook；無路由解析、PreToolUse、allow/deny/updatedInput、別名與鎖定管理。
- Hook 命令只輸出固定 ASCII 提醒。Codex 使用 echo 與 Windows cmd；Claude 使用 shell echo 輸出靜態事件 JSON，為未實測的選用平台。
- Hook 不直接讀規範、不搜尋根目錄、不管制工具，需由 AI 讀取並遵循文字；不能把命令成功當成模型遵循的證明。

## 更新與停用

已有規範先讀取，僅修改授權項目，保留自訂分類與內容。重複初始化不覆蓋規範或重複註冊提醒。

停用按技能 references/configuration.md：修改前備份，只移除能確認屬於本技能的提醒；混合群組保留其他 handler。自訂過的命令先確認歸屬，不整組刪除或關閉全域 Hook。預設保留 project-setting.md 與實際文件；明確要求移除規範時才備份並刪除。技能解除安裝與專案提醒停用分開驗證。

## 交付與驗證

技能包含 SKILL.md、規範與 Hook assets、設定 references，不含執行腳本。維護者以既有 Python unittest 驗證靜態 JSON 的命令輸出及唯讀性，使用者不需安裝測試依賴。

需區分靜態檢查、無 Python/Git 環境的命令回放，以及平台載入／模型操作與原生 Windows。驗證結果與未完成項目見 tasks/plan.md；命令成功不代表平台驗收完成。
