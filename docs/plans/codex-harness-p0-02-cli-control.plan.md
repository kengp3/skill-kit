# 02: CLI 主回合歸屬與安全續作

**What to build:** CLI 主回合歸屬與安全續作，以直接證據支援 Desktop 日常入口與 CLI 開發評測分工。

**Blocked by:** None for recorded-event regression; 01 gates any new child process execution.

**Status:** ready-for-agent

- [ ] 透過可重用的公開控制介面回放已保存 CLI RPC，僅接受指定主 thread／turn 的完成事件，保留早到事件，拒絕子回合與無效事件。
- [ ] 結果不明先核對；writer 未確認停止不允許續作；保留原 deadline 與已消耗時間，不自動整次重跑。
- [ ] 取消、失聯與超時的控制測試只操作自有程序；負向 worker 不受影響；不啟動模型回合。
- [ ] 最小回歸與必要控制邏輯即可，不依賴通用 evaluate 工具；不改 runtime skill／hook。

依據：[設計規格](../specs/codex-coding-harness.spec.md)、[試行計畫 N01–N03](codex-coding-harness-pilot.plan.md#202-具體待改檔案接入及完成條件)。本輪僅實作 P0；P1、Desktop 模型試用、其他宿主與第二專案不在本票。
