# G09：證據對帳、獨立審查與入口更新

**What to build:** 證據對帳、獨立審查與入口更新；交付完整外部行為及可核對證據。

**Blocked by:** G00, G01, G02, G03, G04, G05, G06, G07 have explicit verdicts

**Status:** in_progress

依據：[補驗規格](../specs/harness-validation-gap-closure.spec.md)、[核准工作圖](harness-validation-gap-closure.plan.md)、[可行性研究](../research/unified-project-settings-gap-fixtures-feasibility.research.md)。使用者已核准拆分與驗收邊界；G08另經明確排除。

## 驗收條件

- [ ] Standards／Spec獨立審查完成且required findings已修正。
- [ ] 中央報告、實作票及摘要與直接證據一致，必要受阻時整體仍未完成。
- [ ] 補上README當前證據入口及最小開發端檢查；日常安裝入口與全域狀態單獨回報。

## 本次彙整進度

2026-10-26（Asia/Taipei）：已更新既有[中央細分表](../research/unified-project-settings-acceptance.research.md#g00g09-補驗唯一細分狀態表)及 [README 當前入口](../../README.md#當前驗收證據)。G01 正常接入／clean readback、G02 workflow checkpoint 中斷恢復及 G04 三分支按已交付報告對帳；G03 人工精確核准尚未收到，G07 仍受 UI allowlist 阻擋，Windows cancelled。

G06 正式證據已交付：真 startup／resume／compact 的同合約、一次成果與唯一 child 行為通過；raw stdin source 未知及同事件 native redelivery 仍受阻，shell replay 本輪未跑，單次 bypass 不計 G03 通過。

G05 正式證據已交付：同 server 新 client／同 state 新 server 原 completed 歷史查回，以及新主責普通合約恢復與 unknown 不重派通過；跨 root 原生 child 查回／真正 spawn 結果遺失仍受阻，network deny 僅命中 routing 預連線失敗，未關閉 provider sampling 目標。原約 T1 一直 in_progress，未曾 done。

README 已加入最小來源審查清單（metadata／guide／copied-skill／plugin／assets 與已觀測能力一致），沿用既有 tests；CI 只列本地配置／靜態／targeted 證據，未宣稱 hosted CI 綠燈。demo 0.3.0 copied-skill 接入與日常 marketplace 0.2.1 分開，未自動切換日常入口。

本輪獨立 Standards／Spec 審查與 required findings 對帳尚未完成。G09 不標 done；必要分支仍受阻時整體補驗維持未完成。此文件整理只做讀回、local links 與 diff check，不重跑模型試驗或 full suite。

## 證據要求

保存候選／宿主／任務身分、expected → observed → raw → verdict及無關內容保留證據。控制器exit 0、模型自述、fixture或checker不單獨證明通過。未驗證與受阻保留，不以實作完成取代行為驗收。
