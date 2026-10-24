# 03: Grader 資格與固定產物重評

**What to build:** Grader 資格與固定產物重評，以直接證據支援 Desktop 日常入口與 CLI 開發評測分工。

**Blocked by:** 01 for process execution; qualification selection can be developed independently.

**Status:** ready-for-agent

- [ ] 需求、grader／fixture、相關依賴或環境變更可選出需重驗項目；未受影響證據可沿用；缺失／過期證據保留未驗證。
- [ ] Bug／功能／重構資格分開；重構允許修改前後均通過，不強迫歷史缺陷與 reference commit。
- [ ] checker 升版選出全部受影響固定產物，保留原始結果與產物；無論產品成敗都能取回驗收結果，不啟動或重跑 agent。
- [ ] 沿用公開 lifecycle fixture 及保存產物／來源指紋，透過測試邊界驗證最小重評路徑；不修改原 trial 或 demo-002。

依據：[設計規格](../specs/codex-coding-harness.spec.md)、[試行計畫 N01–N03](codex-coding-harness-pilot.plan.md#202-具體待改檔案接入及完成條件)。本輪僅實作 P0；P1、Desktop 模型試用、其他宿主與第二專案不在本票。
