# project-setting 最終方案整理任務

狀態：精簡與本機驗證已完成。範圍與設計見 [plan.md](plan.md)。

## 1. 精簡技能操作流程

依賴：無。規模：中型，4 檔。

檔案：skills/project-setting/SKILL.md、references/configuration.md、references/migration.md、assets/document-rules.md。

- [x] 移除 migration.md 及技能中的遷移觸發、舊設定處理與歷史路徑說明；description 不再宣稱提供遷移。
- [x] configuration.md 保留完整初始化、更新、驗證及停用流程；停用只移除本技能提醒，保留其他設定與文件。
- [x] 規範範本只移除歷史來源說明，保留全部有效分類、安全規則與自身排除。

驗證：逐項走讀初始化→更新→停用；檢查重複初始化、自訂規範、混合 Hook、自訂提醒歸屬不明的處理；檢查技能內引用無斷鏈。此走讀不宣稱為模型實測。

## 2. 統一交付說明

依賴：1。規模：中型，5 檔。

檔案：README.md、docs/specs/project-setting.spec.md、docs/plans/project-setting.plan.md、docs/plans/project-setting-text-hooks.plan.md、docs/research/codex-hooks-best-practices.research.md。

- [x] README 與規格僅描述最終方案，移除遷移範例與相容性敘述；停用連結改指 configuration.md。
- [x] 刪除兩份被 tasks/plan.md 取代的專屬舊計畫；研究文件收斂為與最終方案相關的來源與結論，移除棄用設計及舊驗收敘述。不新增歷史副本。
- [x] 修正所有指向刪除檔案的引用，保留實際驗證限制；不得把規劃／命令回放標成平台驗收。

驗證：搜尋相關引用與舊方案用語，逐項判斷，不盲目刪除 Python、Git 或 JSON 等仍有正當用途的字詞。

### 檢查點

- [x] 技能包、README 與規格對初始化、更新、停用的描述一致，沒有遷移分支或無效連結。

## 3. 驗證與收尾

依賴：1、2。規模：小型，僅更新 tasks/plan.md、tasks/todo.md 的結果。

- [x] 重跑現有命令測試與差異檢查，記錄通過、跳過與無法執行項目。
- [x] 比對兩平台 Hook 範本與現有測試未被改動；確認規範安全行為保留、無新執行依賴。
- [x] 審閱最終差異，只包含本次整理；不安裝、提交或推送。

驗證命令：`python3 -B -m unittest discover -s tests -v`、`git diff --check`。另檢查所有修改文件的內部連結。

## 保留的待平台驗證項目

以下不是本次文字整理的完成條件，且不得標示已通過：

- [ ] 原生 Windows cmd 輸出與環境相容性。
- [ ] Codex／Claude 實際信任、Hook 注入與模型讀取獨立規範。
- [ ] 模型初始化、文件建立／修改、缺失／衝突／巢狀根目錄、重複初始化與停用案例；驗證保留自訂規範、其他設定與既有文件。
