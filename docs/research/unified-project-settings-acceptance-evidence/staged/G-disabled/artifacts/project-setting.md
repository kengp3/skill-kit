# 專案文件規範

路徑相對於已確認的本專案根目錄；本檔是文件位置唯一規範來源。

| 類型 | 文件用途 | 目的地與檔名 |
| --- | --- | --- |
| prd | 產品目標、使用者問題、成功指標 | docs/prds/{slug}.prd.md |
| spec | 系統行為、需求與驗收 | docs/specs/{slug}.spec.md |
| plan | 實作步驟與驗證安排 | docs/plans/{slug}.plan.md |
| adr | 架構決策、理由與影響 | docs/adr/{id}-{slug}.adr.md |
| research | 研究證據、比較與調查 | docs/research/{slug}.research.md |
| task-contract | 任務合約與可恢復狀態 | docs/plans/{slug}.task-contract.md |
| hook-receipt | 實際 hook 事件的技術收據 | docs/research/{slug}.hook-receipt.md |

文件操作前讀取本規範及適用指令；變更後重讀。依用途分類，不要求產生每種類型。slug 使用簡短字母、數字、底線或連字號；id 沿用既有編號，資訊不足先釐清。分類或根目錄不明、規範缺失或衝突時暫停相關文件寫入並回報。僅經授權修改規範。建立前確認目的地與父目錄不經符號連結越出專案，不將一般文件放入內部或第三方目錄。同名檔先讀取，不直接覆寫；保留既有文件位置。完成後讀回，後續連結使用實際路徑。入口與平台設定不屬一般文件分類。規範由模型遵循，提醒不構成機械攔截。

## Task Harness

| 設定項目 | 值 |
| --- | --- |
| schema_version | 1 |
