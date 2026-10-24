# 02: CLI 主回合歸屬與安全續作

**What to build:** CLI 主回合歸屬與安全續作，以直接證據支援 Desktop 日常入口與 CLI 開發評測分工。

**Blocked by:** None for recorded-event regression; 01 gates any new child process execution.

**Status:** done

- [x] 透過可重用的公開控制介面回放已保存 CLI RPC，僅接受指定主 thread／turn 的完成事件，保留早到事件，拒絕子回合與無效事件。
- [x] 結果不明先核對；writer 未確認停止不允許續作；保留原 deadline 與已消耗時間，不自動整次重跑。
- [x] 取消、失聯與超時的控制測試只操作自有程序；負向 worker 不受影響；不啟動模型回合。
- [x] 最小回歸與必要控制邏輯即可，不依賴通用 evaluate 工具；不改 runtime skill／hook。

依據：[設計規格](../specs/codex-coding-harness.spec.md)、[試行計畫 N01–N03](codex-coding-harness-pilot.plan.md#202-具體待改檔案接入及完成條件)。本輪僅實作 P0；P1、Desktop 模型試用、其他宿主與第二專案不在本票。

實作證據：純控制介面回放首輪 C 兩段原生 RPC，9 項回歸通過；包含 interrupted readback、早到 terminal、錯誤歸屬、結果不明、取消續作授權、writer liveness 分離及原 deadline。TDD 已觀察缺模組、缺驗證、缺續作 API 與衝突事件等失敗後逐項轉綠。實作當時真實父子程序收尾及負向 worker 尚待 ticket 01 整合（現已完成，見下方整合驗收），本票不自行重複程序掃描；未啟動 app-server 或模型。

整合驗收：合併後 56 項 unittest、55 通過／1 Windows 略過；固定產物原生隔離重評五次，parent lifecycle 失敗、A lifecycle 通過、factory-close A／C 通過而 B 失敗，與已知結果一致。取消程序證據與 native readback／原期限續作已有組合測試；證據見 [P0 報告](../research/codex-harness-p0-20261024.research.md)。
