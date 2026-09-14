# 設定與整合

本次已驗收 Codex。Claude Code 依使用者要求跳過；其轉接程式僅通過本地回放，尚未完成實際平台驗證，預設不安裝。

## 執行條件

Python 3.9+、Git；macOS/Linux shell。Windows hook 命令尚未適配。整個技能目錄可獨立複製，沒有套件依賴。安裝器把兩支腳本複製到專案 `.project-setting/runtime/`，後續不依賴開發儲存庫。路由別名 `.project-setting/routes.json` 不提交；runtime、JSON、專案指令與 hook 設定可版本控制。

## JSON

```json
{
  "version": 1,
  "documents": {
    "plan": {
      "description": "實作步驟與驗證安排",
      "path": "docs/plans/{slug}.plan.md",
      "match": ["*.plan.md", "*-plan.md", "plan.md"]
    }
  }
}
```

- version 是設定格式版本，不是產品版本。
- documents 的 key 是使用者可新增的小寫類型識別碼；path 是 root 相對路徑。
- 支援 {slug}、{id} 各出現一次；固定檔名也可。slug 可含 Unicode 字母、數字、底線與連字號；不接受斜線。
- match 使用區分大小寫的檔名 glob。既有目的路徑也會識別；多類型匹配時詢問，不以順序強行決定。
- login.plan.md 自動取得 slug=login；plan.md 無名稱需詢問；0001-database.adr.md 提供 id 與 slug。
- description 給 AI 建議用途。內容語意分類由 AI 解讀，核心不呼叫模型猜分類。

## 使用者選擇

`choose` 保存來源→目的地的文件別名，讓同一來源後續讀寫一致；不修改全專案匹配規則。
本次位置也保存同一文件的別名，便於後續修改；不代表永久新增一種類型。
缺設定時可初始化使用者提供的 JSON，或確認一次性位置。設定改動只影響新文件，已選定文件保留原目的地。

## 工具整合

Codex：`.codex/hooks.json`，PreToolUse 改寫補丁的檔案標頭，保留內容。Claude：`.claude/settings.json`，改寫完整 input 物件中的 file_path，保留其他參數且不自動回傳 allow。
兩平台 SessionStart/SubagentStart 提供規範；Bash 只提供指引。正常路由回傳目的地，資訊不足才 deny 並要求 AI 詢問，不把錯誤分類寫進檔案。
Codex updatedInput 必須搭配 allow，仍須遵守宿主的沙箱與權限；不是新增操作授權。Claude 只回傳 updatedInput，保留原權限流程。

初始化只追加一次標記的指令，合併 hook 陣列。不要同時安裝多個重複的路由器。Claude 需從 root 啟動，Codex 專案與 hook 需要信任。新 session 驗證載入。

## 明確限制

- 不能改寫任意 Bash/PowerShell/外部編輯器的逐檔寫入，不能保證第三方固定路徑腳本或文件相對連結自動修復。
- 只改寫受支援途徑；其他程式先解析目的地再執行。來源不存在且不明的 Markdown 會詢問；慣用入口／技能內部目錄不會。
- 路由別名是本地運行狀態，不是跨機器共享索引；後續工作應使用真正目的地。
- 寫入前會保留來源與目的地對應，避免不同來源搶用同一位置；記錄存在不代表工具已成功寫入。工具失敗時保留對應，讓相同來源可重試。人工清理前須確認沒有進行中的工具呼叫，且不再需要該文件的別名；勿直接刪除整份狀態來解除衝突。
- 受管文件的補丁重新命名尚未支援，因為還需要同步更新別名及參照；無關程式碼的重新命名不受此限制。
- 無效設定、目的地衝突或路徑越界停止該操作並明確回報；不自動遷移歷史文件。
- 尚未支援文件內容章節與範本驗證，也不宣稱 hook 是完整檔案系統隔離邊界。

## 查證來源

- [Codex hooks](https://learn.chatgpt.com/docs/hooks)：PreToolUse updatedInput、additionalContext、信任與工具覆蓋。
- [Claude hooks](https://code.claude.com/docs/en/hooks)：完整 input 替換、權限與上下文回傳。
- [Claude settings](https://code.claude.com/docs/en/settings)：專案設定範圍。

官方來源查核於 2026-09-15；實際平台驗證證據記錄在開發儲存庫 docs/plans/project-setting.plan.md。
