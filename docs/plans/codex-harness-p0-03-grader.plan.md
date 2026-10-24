# 03: Grader 資格與固定產物重評

**What to build:** Grader 資格與固定產物重評，以直接證據支援 Desktop 日常入口與 CLI 開發評測分工。

**Blocked by:** 01 for process execution; qualification selection can be developed independently.

**Status:** done

- [x] 需求、grader／fixture、相關依賴或環境變更可選出需重驗項目；未受影響證據可沿用；缺失／過期證據保留未驗證。
- [x] Bug／功能／重構資格分開；重構允許修改前後均通過，不強迫歷史缺陷與 reference commit。
- [x] checker 升版選出全部受影響固定產物，保留原始結果與產物；無論產品成敗都能取回驗收結果，不啟動或重跑 agent。
- [x] 沿用公開 lifecycle fixture 及保存產物／來源指紋，透過測試邊界驗證最小重評路徑；不修改原 trial 或 demo-002。

依據：[設計規格](../specs/codex-coding-harness.spec.md)、[試行計畫 N01–N03](codex-coding-harness-pilot.plan.md#202-具體待改檔案接入及完成條件)。本輪僅實作 P0；P1、Desktop 模型試用、其他宿主與第二專案不在本票。

實作證據：`python3 -B -m unittest discover -s tests -p test_harness_grader.py -v`，7 項通過、0 skipped。公開 seam 為案例輸入／資格狀態、受影響固定產物選取，以及隔離 checker 執行與新收據；TDD 曾先確認缺模組／缺 API 為紅，並以缺 observations 的 qualified 聲明建立紅→綠回歸。

原生 sandbox canary 已核對固定產物寫入遭拒、正常與 assertion 失敗可區分、缺 XML／零測試／數量不符／略過／exit 不一致／超時都不冒稱產品驗收結果；收據不可覆寫。實際執行依賴已整合的 ticket 01，沒有呼叫模型、app-server 或修改 Desktop 設定。公開 lifecycle fixture 與既有固定產品的整合驗收已由整合分支完成，見下方證據。

整合驗收：合併後 56 項 unittest、55 通過／1 Windows 略過；固定產物原生隔離重評五次，parent lifecycle 失敗、A lifecycle 通過、factory-close A／C 通過而 B 失敗，與已知結果一致。取消程序證據與 native readback／原期限續作已有組合測試；證據見 [P0 報告](../research/codex-harness-p0-20261024.research.md)。

最終修正後驗收：60項unittest（59通過／1 Windows略過）、五次固定Java產物重評完成；新增監測失效收尾、threaded launcher、malformed receipt及報告集合／數量回歸。初次結果保留為歷史，最終證據見P0報告。
