# project-setting 提示型 Hook 設計依據

## 結論

project-setting 以技能包分發，使用專案根目錄 project-setting.md 保存文件規範。AI 使用現有檔案工具初始化及更新設定，SessionStart／SubagentStart 只提醒讀取規範；不需要額外安裝程式或執行期腳本。

## 採用的官方規格

以下 Hook 格式已於 2026-09-16 文件審查時核對；平台實際載入與模型行為仍待驗證。

- Codex 可由專案 `.codex/hooks.json` 或 config.toml 的 `[hooks]` 提供定義，同層擇一；使用者須完成信任流程。[Codex Hooks](https://learn.chatgpt.com/docs/hooks)
- Codex 的 SessionStart／SubagentStart 可將標準輸出的純文字加入模型上下文；Windows 可用 commandWindows 指定系統命令。[事件與命令設定](https://learn.chatgpt.com/docs/hooks)
- Claude 使用含 hookEventName 與 additionalContext 的靜態 JSON 注入提醒。[Claude Hooks](https://code.claude.com/docs/en/hooks)

## 實作選擇與限制

- 提醒採固定 ASCII 文字，不嵌入使用者路徑或文件內容。根目錄辨識與規範讀取由 AI 完成。
- 保留使用者的既有規範與其他 Hook；完整相同的提醒不重複新增。停用只移除已確認的本技能項目。
- 提醒不會阻擋或改寫工具操作，也不會檢查規範是否存在；AI 必須處理缺失、衝突與實際文件位置。
- 原生命令回放只能驗證輸出及唯讀性，不能取代原生 Windows、平台信任／事件載入或模型行為測試。結果見 [驗證紀錄](../../tasks/plan.md#驗證紀錄)。
