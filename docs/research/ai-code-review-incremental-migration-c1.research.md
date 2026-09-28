# C1：增量移轉 Batch 2 獨立審查

## 1. 基本說明

**結論：Request changes；Batch 2 業務一致性 FAIL。** 已確認一項阻擋問題：新退款服務錯誤拒絕第 30 天退款。先修正年齡邊界，再重跑九個必要案例並比較完整輸出與狀態。

- 審查開始：2026-09-28 17:56:26 UTC+08:00（Asia/Taipei）。
- 審查材料：[C1 reader](/Users/kengp3/Workspaces/mine/simple-skills/docs/research/ai-code-review-incremental-migration-validation-evidence/C1/reader)；報告封存於本次指定路徑。
- 執行狀態：已完成指定快照的來源、合約與既有執行紀錄核對；本輪唯讀，未重新編譯或執行。沒有遠端 PR，也沒有提交平台審查。

## 2. 範圍說明

舊側 `main` 為 `60492ed70cfb13ff86a9d46c5e0f1bb90efb268e`；新側 Batch 1 base `main` 為 `834fcd68b8c98b0ea6431f477646b0ceb80c0491`，Batch 2 head `codex/refund-batch` 為 `a7c2d4caa3d54397943de5509f453ba4cb70d91b`。Git bundle 所列 refs 與 [manifest](/Users/kengp3/Workspaces/mine/simple-skills/docs/research/ai-code-review-incremental-migration-validation-evidence/C1/reader/manifest.json) 相符；manifest 所列 20 個檔案的 SHA-256 均相符。新側以 base→head 直接快照及 [patch](/Users/kengp3/Workspaces/mine/simple-skills/docs/research/ai-code-review-incremental-migration-validation-evidence/C1/reader/target.patch) 比較，變更為新增 `RefundService.java`、`Warehouse.java` 兩檔。

[契約](/Users/kengp3/Workspaces/mine/simple-skills/docs/research/ai-code-review-incremental-migration-validation-evidence/C1/reader/CONTRACT.md:3) 要求 Batch 2 移轉退款、保留既有行為，並檢查受影響的 Batch 1 訂單。納入舊側 [LegacySystem](/Users/kengp3/Workspaces/mine/simple-skills/docs/research/ai-code-review-incremental-migration-validation-evidence/C1/reader/legacy/LegacySystem.java:7)、新側 base/head 的 `OrderService`、`Policy`、`State`，以及兩側 `Probe`、執行紀錄與九個指定案例。loyalty 是後續獨立批次，不屬本批驗收。

## 3. 關聯與流程

單一流程鏈足以說明本次兩個入口及共用狀態：`Probe → OrderService.order → Policy.shipping → State(orderTotal, events)`；`Probe → RefundService.refund → receipts／age guard → gatewayCalls → Warehouse.restock → State(refunds, restocked, events)`。舊側兩條路徑都在 `LegacySystem` 中；新側服務共用同一個 `State`。退款的 receipt 重播須先於年齡與 gateway 檢查；成功後才各增加一次退款、補貨與 `R` 事件。

Batch 1 的 `OrderService`、`Policy`、`State` 在 base/head 未變。提供的 `order7999`、`order8000`、`order8001`、`invalid` 完整輸出與狀態均與舊側一致；`sequence` 的下單階段也留下相同的 `8000` 與 `O`，其後退款因第 30 天邊界失敗。

## 4. 審查結果與問題

**F1｜阻擋｜第 30 天退款遭拒。** [新側 `RefundService.java:9`](/Users/kengp3/Workspaces/mine/simple-skills/docs/research/ai-code-review-incremental-migration-validation-evidence/C1/reader/target-head/RefundService.java:9) 使用 `ageDays >= 30`；[舊側 `LegacySystem.java:15`](/Users/kengp3/Workspaces/mine/simple-skills/docs/research/ai-code-review-incremental-migration-validation-evidence/C1/reader/legacy/LegacySystem.java:15) 使用 `ageDays > 30`，且[契約](/Users/kengp3/Workspaces/mine/simple-skills/docs/research/ai-code-review-incremental-migration-validation-evidence/C1/reader/CONTRACT.md:5) 明定 0 至 30 天均可退款。`Probe` 可直接以 30 天觸發，沒有上游 guard 排除此案例。建議將新側條件改為 `ageDays < 0 || ageDays > 30`，並保留 receipt 重播優先序。

| 案例 | 舊側輸出與狀態 | 新側輸出與狀態 |
|---|---|---|
| `age30` | <code>REFUND:1&#124;0:1:1:1:R</code> | <code>EXPIRED&#124;0:0:0:0:</code> |
| `sequence` | <code>REFUND:1&#124;8000:1:1:1:OR</code> | <code>EXPIRED&#124;8000:0:0:0:O</code> |

[舊側紀錄](/Users/kengp3/Workspaces/mine/simple-skills/docs/research/ai-code-review-incremental-migration-validation-evidence/C1/reader/legacy-execution.json)與[新側紀錄](/Users/kengp3/Workspaces/mine/simple-skills/docs/research/ai-code-review-incremental-migration-validation-evidence/C1/reader/target-execution.json)均包含九個指定案例，編譯及各案例 exit code 均為 0；除表列兩例外，完整 stdout 相同。`age31`、`decline`、`replay` 在提供紀錄中一致，且來源中的 gateway、補貨、事件與 receipt 路徑相符。一般品質審查未發現另一項可確認的本批缺陷；此次材料只涵蓋循序、記憶體內行為，不證明資料庫交易、外部支付、訊息或部署行為。執行紀錄是提供的既有證據，本輪未重跑；bundle refs 與檔案雜湊核對亦不等同於重新從 bundle 建置。

## 5. 結論

**Batch 2：Request changes，業務一致性 FAIL。** F1 是未核准的可觀察行為差異；修正後以相同初始狀態重跑 `order7999`、`order8000`、`order8001`、`invalid`、`age30`、`age31`、`decline`、`replay`、`sequence`，逐例比較回傳值及完整狀態，尤其核對 `sequence` 的 `OR` 順序。**整體移轉仍未完成**：loyalty 明定留待後續批次，不能由 Batch 2 結果推定 whole migration 通過。

本次採用 [AI 程式碼審查技能](/Users/kengp3/Workspaces/mine/simple-skills/skills/ai-code-review/SKILL.md)、其 `migration.md`、`deep-review.md`、`report.md` 參考與專案 `project-setting.md`；對應 SHA-256 依序為 `38aee866…`、`e1de157c…`、`5b57525a…`、`3ae87fb8…`、`cd6c155c…`。以下為本次完整變更檔案清單；其餘閱讀材料已在範圍與證據段落標明。

| base → head | 責任與差異 | 審查結果 |
|---|---|---|
| 無 → [`RefundService.java`](/Users/kengp3/Workspaces/mine/simple-skills/docs/research/ai-code-review-incremental-migration-validation-evidence/C1/reader/target-head/RefundService.java:1) | 新增退款 guard、gateway、receipt、狀態與事件流程 | F1：30 天邊界錯誤；其餘指定路徑依提供紀錄一致 |
| 無 → [`Warehouse.java`](/Users/kengp3/Workspaces/mine/simple-skills/docs/research/ai-code-review-incremental-migration-validation-evidence/C1/reader/target-head/Warehouse.java:1) | 新增補貨計數；由成功退款呼叫 | 已查，指定成功／拒絕／重播案例未見獨立差異 |
