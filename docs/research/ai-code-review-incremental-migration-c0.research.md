# C0：增量移轉 batch 2 獨立審查

## 1. 基本說明

- **結論：建議通過 batch 2（Approve）。** 指定九個案例的完整回傳與狀態一致，來源審查未發現未核准的退款差異或訂單回歸；已確認阻擋 0、必要缺口 0。
- 審查開始：2026-09-28 17:56 +08:00（Asia/Taipei）。範圍是 `/Users/kengp3/Workspaces/mine/simple-skills/docs/research/ai-code-review-incremental-migration-validation-evidence/C0/reader` 的唯讀封存；沒有遠端 PR。
- **整體移轉尚未完成**：loyalty 屬後續獨立批次，不在本次放行範圍。

## 2. 範圍說明

[契約](/Users/kengp3/Workspaces/mine/simple-skills/docs/research/ai-code-review-incremental-migration-validation-evidence/C0/reader/CONTRACT.md)要求 batch 2 移轉退款並確認受影響的 batch 1 訂單行為，沒有核准行為變更。舊版固定於 `60492ed70cfb13ff86a9d46c5e0f1bb90efb268e`；新版由 `main` 的 `2ca09e3eaabf3c984ad3ca79f8dafd9422adf3dd` 比較到 `codex/refund-batch` 的 `3bcb55f1e85e4df8ebf99192da0cf6771e06e817`。[提交差異](/Users/kengp3/Workspaces/mine/simple-skills/docs/research/ai-code-review-incremental-migration-validation-evidence/C0/reader/target.patch)只有新增 `RefundService.java` 與 `Warehouse.java`；`OrderService.java`、`Policy.java`、`State.java` 在 base/head 的封存雜湊相同。

兩個 Git bundle 均通過 `git bundle verify`，且 [manifest](/Users/kengp3/Workspaces/mine/simple-skills/docs/research/ai-code-review-incremental-migration-validation-evidence/C0/reader/manifest.json)列出的 20 個檔案 SHA-256 全部吻合。本審查只讀 C0/reader，不檢視其他案例、oracle 或產生器。

## 3. 關聯與流程

用一條操作流程即可說明本次跨批次影響：舊版 [LegacySystem](/Users/kengp3/Workspaces/mine/simple-skills/docs/research/ai-code-review-incremental-migration-validation-evidence/C0/reader/legacy/LegacySystem.java:7) 在同一物件內執行訂單和退款；新版 [OrderService](/Users/kengp3/Workspaces/mine/simple-skills/docs/research/ai-code-review-incremental-migration-validation-evidence/C0/reader/target-head/OrderService.java:4) 與 [RefundService](/Users/kengp3/Workspaces/mine/simple-skills/docs/research/ai-code-review-incremental-migration-validation-evidence/C0/reader/target-head/RefundService.java:7) 使用同一個 `State`。訂單經 `Policy.shipping` 累加金額及 `O` 事件；退款先查 receipt、再查有效日齡和 gateway decline，成功後透過 [Warehouse.restock](/Users/kengp3/Workspaces/mine/simple-skills/docs/research/ai-code-review-incremental-migration-validation-evidence/C0/reader/target-head/Warehouse.java:2) 回補一次，累加退款並追加 `R`。這些 guard 與副作用順序和舊版對應。指定 sequence 以同一狀態先下單 8000 分，再於第 30 天退款，兩側結果皆為 `REFUND:1|8000:1:1:1:OR`。

## 4. 審查結果與證據邊界

**未確認缺陷。** [舊版 Probe](/Users/kengp3/Workspaces/mine/simple-skills/docs/research/ai-code-review-incremental-migration-validation-evidence/C0/reader/legacy-Probe.java:5)與[新版 Probe](/Users/kengp3/Workspaces/mine/simple-skills/docs/research/ai-code-review-incremental-migration-validation-evidence/C0/reader/target-Probe.java:5)對九案例使用對應輸入，並輸出回傳值及完整狀態。[舊版執行紀錄](/Users/kengp3/Workspaces/mine/simple-skills/docs/research/ai-code-review-incremental-migration-validation-evidence/C0/reader/legacy-execution.json)與[新版執行紀錄](/Users/kengp3/Workspaces/mine/simple-skills/docs/research/ai-code-review-incremental-migration-validation-evidence/C0/reader/target-execution.json)均記錄編譯 exit 0；`order7999`、`order8000`、`order8001`、`invalid`、`age30`、`age31`、`decline`、`replay`、`sequence` 的各次執行 exit 0、stdout 逐項相同。邊界輸出包括 7999 分訂單的 `ORDER:8499|8499:0:0:0:O`、8000 分訂單的 `ORDER:8000|8000:0:0:0:O`、第 31 天退款的 `EXPIRED|0:0:0:0:`、decline 的 `DECLINED|0:0:0:1:`，以及成功後 replay 的 `REFUND:1|0:1:1:1:R`。

本次是唯讀審查，沒有重新編譯或執行；執行結論以封存紀錄、Probe 和來源交叉核對。契約明定這是記憶體內循序演練，證據不證明資料庫交易、外部付款、訊息傳遞、部署或未列出的執行環境行為；九案例相同亦不構成所有可能輸入的形式證明。

## 5. 結論

對此固定版本及契約指定的 batch 2 範圍，業務一致性判為 **PASS**，審查建議 **Approve**。這是審查建議，並非已提交平台 review 或已完成實際合併。全專案移轉狀態仍是**未完成**：舊版 `loyaltyStatus()` 位於 [LegacySystem.java:25](/Users/kengp3/Workspaces/mine/simple-skills/docs/research/ai-code-review-incremental-migration-validation-evidence/C0/reader/legacy/LegacySystem.java:25)，契約指定於後續批次處理，不應列為本批次缺陷，也不能隨本批次放行而宣稱已移轉。

本次差異檔案已全部對帳：新增的 [RefundService.java](/Users/kengp3/Workspaces/mine/simple-skills/docs/research/ai-code-review-incremental-migration-validation-evidence/C0/reader/target-head/RefundService.java)承接退款 guard、gateway、receipt 與事件；新增的 [Warehouse.java](/Users/kengp3/Workspaces/mine/simple-skills/docs/research/ai-code-review-incremental-migration-validation-evidence/C0/reader/target-head/Warehouse.java)承接回補。關聯但未變更的 `OrderService.java`、`Policy.java`、`State.java` 已核對來源與雜湊，並以指定訂單及 sequence 案例檢查可觀察行為。
