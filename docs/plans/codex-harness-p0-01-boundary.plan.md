# 01: 開發測試的寫入與程序邊界

**What to build:** 開發測試的寫入與程序邊界，以直接證據支援 Desktop 日常入口與 CLI 開發評測分工。

**Blocked by:** None (can start immediately).

**Status:** ready-for-agent

- [ ] 測試子程序只能寫入專屬工作目錄；設定、plugin cache、宿主持久狀態與其他日常資料不因測試被覆寫；未知／symlink 逃逸路徑拒絕。
- [ ] 以可執行方式限制 wall time、CPU／記憶體與並行程序；本輪模型／網路額度為零，不能呼叫模型或連線；限制無法成立則停止相依程序。
- [ ] 正常、錯誤、取消與失聯均收尾自有父子程序；無關檔案與負向 worker 不變；不要求人工監看。
- [ ] 以真實隔離 canary 及負向對照驗證，不修改 Desktop、全域配置、快取、記憶或原 demo-002。

依據：[設計規格](../specs/codex-coding-harness.spec.md)、[試行計畫 N01–N03](codex-coding-harness-pilot.plan.md#202-具體待改檔案接入及完成條件)。本輪僅實作 P0；P1、Desktop 模型試用、其他宿主與第二專案不在本票。
