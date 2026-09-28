# C3：增量移轉 batch 2 獨立審查

## 1. 基本說明

- 執行時間：2026-09-28 17:56:37 UTC+08:00。
- 審查對象：[C3/reader](/Users/kengp3/Workspaces/mine/simple-skills/docs/research/ai-code-review-incremental-migration-validation-evidence/C3/reader) 的舊系統訂單／退款與新架構 batch 2；依 [契約](/Users/kengp3/Workspaces/mine/simple-skills/docs/research/ai-code-review-incremental-migration-validation-evidence/C3/reader/CONTRACT.md)，本批也驗證受影響的 batch-1 訂單。
- 結果：**業務一致性 FAIL；batch 2 建議 Request changes**。已確認阻擋 1 項；應先恢復 8000 分免運門檻，再重驗九個指定案例。
- 本次只讀取封存材料，沒有修改被審程式、重跑 Java、提交平台審查或操作 remote PR；材料也註明無 remote PR。

## 2. 範圍說明

舊系統固定版為 `60492ed70cfb13ff86a9d46c5e0f1bb90efb268e`；目標 base 為 `920ada7be31ee156b951dee451a671b5c0edaaed`（`main`），head 為 `8aeffaf209f694b4c50cc3e6f23304de9f6c0ba9`（`codex/refund-batch`）。兩套系統以契約及來源對照；目標的 [patch](/Users/kengp3/Workspaces/mine/simple-skills/docs/research/ai-code-review-incremental-migration-validation-evidence/C3/reader/target.patch) 是 base→head，涉及 `Policy.java` 修改、`RefundService.java` 與 `Warehouse.java` 新增。`OrderService.java`、`State.java` 未改，但在共同狀態與呼叫路徑內。loyalty 為後續獨立批次，超出本批驗收。

[manifest](/Users/kengp3/Workspaces/mine/simple-skills/docs/research/ai-code-review-incremental-migration-validation-evidence/C3/reader/manifest.json) 所列 20 個檔案的 SHA-256 全部吻合；兩個 bundle 列出的 refs 符合上述固定 commit。沒有從 bundle 抽取物件或獨立重跑 Probe。提供的編譯及九個案例紀錄均記錄 exit code 0，但其編譯路徑在 reader 外，故不能把紀錄表述為本次重跑或獨立驗證過的執行環境。

## 3. 關聯與流程

舊側 [LegacySystem](/Users/kengp3/Workspaces/mine/simple-skills/docs/research/ai-code-review-incremental-migration-validation-evidence/C3/reader/legacy/LegacySystem.java:7) 的 `order` 在 `net >= 8000` 時免運，`refund` 先查已完成收據、再判斷 0–30 天，成功後增加 gateway、退款與補貨次數並附加 `R`。新側 [OrderService](/Users/kengp3/Workspaces/mine/simple-skills/docs/research/ai-code-review-incremental-migration-validation-evidence/C3/reader/target-head/OrderService.java:4) 透過 `Policy.shipping()` 更新共享 `State`；[RefundService](/Users/kengp3/Workspaces/mine/simple-skills/docs/research/ai-code-review-incremental-migration-validation-evidence/C3/reader/target-head/RefundService.java:7) 以相同優先序處理收據、期限、gateway 與退款，並由 `Warehouse.restock()` 增加補貨。`sequence` 先下 8000 分訂單再退款，所以訂單運費差異會保留在退款後的完整狀態。此直接呼叫鏈已足以解釋差異，無需額外關係圖。

## 4. 審查結果與問題

**F-001（阻擋，batch 2 新增回歸）：8000 分訂單多收 500 分。**[legacy `LegacySystem.java:9`](/Users/kengp3/Workspaces/mine/simple-skills/docs/research/ai-code-review-incremental-migration-validation-evidence/C3/reader/legacy/LegacySystem.java:9) 與 [target-base `Policy.java:2`](/Users/kengp3/Workspaces/mine/simple-skills/docs/research/ai-code-review-incremental-migration-validation-evidence/C3/reader/target-base/Policy.java:2) 均使用 `net >= 8000`；[target-head `Policy.java:2`](/Users/kengp3/Workspaces/mine/simple-skills/docs/research/ai-code-review-incremental-migration-validation-evidence/C3/reader/target-head/Policy.java:2) 改為 `net > 8000`。`OrderService` 沒有其他門檻防護。這違反明定「8000 或以上免運」且沒有核准的行為變更。

| 指定案例 | 舊側完整輸出／狀態 | 新側完整輸出／狀態 |
| --- | --- | --- |
| `order8000` | `ORDER:8000\|8000:0:0:0:O` | `ORDER:8500\|8500:0:0:0:O` |
| `sequence` | `REFUND:1\|8000:1:1:1:OR` | `REFUND:1\|8500:1:1:1:OR` |

上述值見 [legacy 執行紀錄](/Users/kengp3/Workspaces/mine/simple-skills/docs/research/ai-code-review-incremental-migration-validation-evidence/C3/reader/legacy-execution.json) 與 [target 執行紀錄](/Users/kengp3/Workspaces/mine/simple-skills/docs/research/ai-code-review-incremental-migration-validation-evidence/C3/reader/target-execution.json)，亦可由來源直接推得。其餘七個指定案例的紀錄完整輸出一致；退款單獨案例 `age30`、`age31`、`decline`、`replay` 未顯示差異。最小修正是恢復 `net >= 8000`，再以相同初始狀態重跑全部九例，逐例比對回傳值與完整狀態。未觀測資料庫交易、實際付款、訊息系統或部署行為；契約明確將這些排除於本次記憶體、循序演練之外。

## 5. 結論

**batch 2：Request changes；約定範圍的業務等價性 FAIL。**F-001 修正並重驗前不能建議通過。**整體移轉：尚未完成**，因本批仍有阻擋，且 loyalty 尚待後續批次；本結論不推稱整個專案的運行品質。

檔案對帳（本節最後）：變更目標為 `target-base/Policy.java` → `target-head/Policy.java`（F-001）、新增 `target-head/RefundService.java`、新增 `target-head/Warehouse.java`；關聯未改來源為 `target-base/OrderService.java`、`target-head/OrderService.java`、`target-base/State.java`、`target-head/State.java`；舊側來源為 `legacy/LegacySystem.java`。規則及案例材料為 `CONTRACT.md`、`legacy/CONTRACT.md`、`target-base/CONTRACT.md`、`target-head/CONTRACT.md`、`legacy-Probe.java`、`target-Probe.java`、`legacy-execution.json`、`target-execution.json`；固定版與差異材料為 `legacy.bundle`、`target.bundle`、`target.patch`、`manifest.json`。上述路徑均相對於 [C3/reader](/Users/kengp3/Workspaces/mine/simple-skills/docs/research/ai-code-review-incremental-migration-validation-evidence/C3/reader)。
