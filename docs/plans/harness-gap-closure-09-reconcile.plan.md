# G09：證據對帳、獨立審查與入口更新

**2026-10-26 範圍修訂（使用者已核准）：** 本次依三項改版、demo 日常端到端及必要失敗處理收尾；完成判定見中央 R1–R8。G05／G06 宿主剩餘分支及 G07 改列選配未驗證，下方先前「整體未完成」敘述是舊範圍快照，不再作為完成門檻。 依據：[最新規格 S1](../specs/harness-validation-gap-closure.spec.md#s1-唯一驗收邊界與狀態)。

**What to build:** 證據對帳、獨立審查與入口更新；交付完整外部行為及可核對證據。

**Blocked by:** G00, G01, G02, G03, G04, G05, G06, G07 have explicit verdicts

**Status:** done — 限本輪證據對帳、審查與入口收尾；整體補驗未完成

依據：[補驗規格](../specs/harness-validation-gap-closure.spec.md)、[核准工作圖](harness-validation-gap-closure.plan.md)、[可行性研究](../research/unified-project-settings-gap-fixtures-feasibility.research.md)。使用者已核准拆分與驗收邊界；G08另經明確排除。

## 驗收條件

- [x] Standards／Spec獨立審查完成且required findings已修正。
- [x] 中央報告、實作票及摘要與直接證據一致，必要受阻時整體仍未完成。
- [x] 補上README當前證據入口及最小開發端檢查；日常安裝入口與全域狀態單獨回報。

## 本次彙整進度

2026-10-26（Asia/Taipei）：已更新既有[中央細分表](../research/unified-project-settings-acceptance.research.md#g00g09-補驗唯一細分狀態表)及 [README 當前入口](../../README.md#當前驗收證據)。G01 正常接入／clean readback、G02 workflow checkpoint 中斷恢復及 G04 三分支按已交付報告對帳；G03 已完成核准後續作，G07 仍受 UI allowlist 阻擋，Windows cancelled。

G03 續作證據已對帳：[正常持久信任報告](../research/harness-gap-closure-persisted-trust.research.md)記錄使用者核准五項精確定義後，正常 TUI t 信任；同專用 state 兩個新 invocation 各 completed／server exit 0、精確 20 bytes、各任務唯一 done 合約、三則 developer 提醒及正常 Stop。auth 清除後五項仍 trusted、global 指紋不變；限 CLI 0.164.0／該五定義／本 state，不外推 SubagentStart 執行、Windows／Desktop、demo 或全域信任。demo G01 的五個 hooks 仍 untrusted，日常 marketplace 0.2.1 未升級。

G06 正式證據已交付：真 startup／resume／compact 的同合約、一次成果與唯一 child 行為通過；raw stdin source 未知及同事件 native redelivery 仍受阻，shell replay 本輪未跑，單次 bypass 不計 G03 通過。

G05 正式證據已交付：同 server 新 client／同 state 新 server 原 completed 歷史查回，以及新主責普通合約恢復與 unknown 不重派通過；跨 root 原生 child 查回／真正 spawn 結果遺失仍受阻，network deny 僅命中 routing 預連線失敗，未關閉 provider sampling 目標。原約 T1 一直 in_progress，未曾 done。

README 已加入最小來源審查清單（metadata／guide／copied-skill／plugin／assets 與已觀測能力一致），沿用既有 tests；CI 只列本地配置／靜態／targeted 證據，未宣稱 hosted CI 綠燈。demo 0.3.0 copied-skill 接入與日常 marketplace 0.2.1 分開，未自動切換日常入口。

本輪[獨立 Standards／Spec 審查](../research/harness-gap-closure-review.research.md)已完成，固定 base `f15338e`、受查 head `0ec9812`，兩軸各 0 actionable findings，無尚待修正的 required findings；[審查身分與結果](../research/harness-gap-closure-review-evidence/review-results.json)可核對。README 已補上本輪真實入口，中央表、個案票與摘要的結果／阻礙已對帳，G09 的三項收尾條件完成。G03 的新增限案證據不回寫原審查受查 head，受查 target `0f29d11` 的[G03 增量兩軸審查](../research/harness-gap-closure-review.research.md#g03-核准後增量審查)已完成，各 0 actionable findings，限定通過範圍不變；G05／G06／G07 的必要缺口仍保留原判定，整體補驗未完成。此次三文件收尾只做讀回、local links、狀態與 diff check，不重跑模型試驗或 full suite。

## 證據要求

G07 後續只完成[可攜輸入材料](../research/harness-gap-closure-desktop-evidence/manual-kit-20261026-4a9d7f20/operator.md)與[準備範圍審查](../research/harness-gap-closure-review.research.md#g07-人工輸入材料審查)：Stop／Model ZIP 為 27／26 檔，來源與維護自檢通過，父層發現的暫存模板路徑依賴已修正並複查。中央表仍維持 G07 UI 未執行、環境資格未成立，不因材料就緒關閉驗收缺口；G09 done 仍僅限對帳與審查收尾。

保存候選／宿主／任務身分、expected → observed → raw → verdict及無關內容保留證據。控制器exit 0、模型自述、fixture或checker不單獨證明通過。未驗證與受阻保留，不以實作完成取代行為驗收。
