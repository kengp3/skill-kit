---
name: project-setting
description: Create or update project document rules, reminder hooks, and explicitly requested settings from a supplied Markdown specification. Use for document conventions, unclear categories, or delegated specification-based setup; the provider owns setting semantics.
---

# 專案設定與文件規範

以專案根目錄 `project-setting.md` 為唯一文件規範來源，不依賴 AGENTS.md 或 CLAUDE.md 作為入口；平台適用指令仍須照常遵循。AI 遵循文字；Hook（事件掛鉤）只在工作階段與子代理開始時提醒讀取。不自動改寫路徑、阻擋工具或維護別名。

技能與 Hook 不需要 Python、Git 或 Node.js；使用現有檔案工具編輯，提醒用系統命令輸出固定文字。Codex 為主要平台，Claude 為選用；平台驗收狀態見 [設定說明](references/configuration.md)。

單獨使用時只管理文件規範與要求的提醒。只有使用者明確指定包含其他能力，或已啟用能力在原授權內提供設定規格時，才處理該能力的設定；按 [依提供規格設定](references/configuration.md#依提供規格設定) 操作。規格提供者定義欄位、格式、預設值、有效性及移轉規則，本技能負責設定操作。

## 初始化或更新

1. 確認使用者指定的專案目錄，讀取適用指令、已有規範與平台 Hook 設定。使用者指定或工作階段已確認的專案根目錄優先，不以 Git、AGENTS.md 或工具 cwd 判定根目錄。不明時只問目標目錄，不無界向上搜尋或套用上層專案規範；多專案任務分別確認。
2. 用 [規範範本](assets/document-rules.md) 建立根目錄 `project-setting.md`，依使用者慣例調整表格，沒有自訂需求時採五種預設；不預建空目錄。已有檔案先讀取，只改授權項目，不能以預設覆蓋；不可讀或衝突先回報，無法依提供規格與原授權唯一決定的內容先釐清。檢查目的地與符號連結不越界。新初始化不建立或修改 AGENTS.md／CLAUDE.md。
3. 用 [設定說明](references/configuration.md) 安裝使用者要求的平台提示型 Hook；一般初始化沿用已知使用平台，未能判斷時詢問，不同時安裝所有平台。若只要求調整文件規範，不順手改 Hook。保留其他指令與設定；不將範本整份覆蓋到已有平台設定。
4. 若本次包含提供的設定規格，依規格只合併其擁有的區段、分類列與明確要求的平台設定，再交回提供者檢查；沒有提供規格時不搜尋或加入其他能力設定。
5. 回讀變更，確認獨立規範可讀、無關內容與平台指令檔保留，且每個事件只有一份本技能提醒。啟用、信任與驗證按設定說明完成；分開回報「設定已寫入／讀回」與「提供者驗證／宿主已載入」。

## 分類與日常使用

- 文件操作前實際讀取已確認根目錄的 project-setting.md，以用途決定類型與目的地；規範剛被修改應重讀。根目錄不明、檔案缺失／空白／不可讀或規範衝突時，暫停相關文件寫入並回報，其他工作可繼續；不得擅自恢復預設或套用另一專案規範。這由 AI 遵循，不是 Hook 的自動偵測或阻擋。
- 類型、必要名稱或編號不明時，提出一個最合適選擇與理由，等待使用者決定。可選既有類型、新類型或本次位置；一次性位置不新增永久規則。
- 不自動搬移既有文件，不覆寫同名目的地，不越出專案邊界；一般文件與入口／平台文件分開處理。
- 建立前確認路徑，完成後讀回核對。後續工具操作與連結使用真正目的地；沒有程式替你轉換來源名稱。

停用只在使用者要求的專案內進行，依 [設定與停用說明](references/configuration.md#停用) 保留其他 Hook、規範與文件。
