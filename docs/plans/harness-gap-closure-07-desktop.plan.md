# G07：V05 Desktop 停止與模型選單

**What to build:** V05 Desktop 停止與模型選單；交付完整外部行為及可核對證據。

**Blocked by:** dedicated Desktop workspace/state, allowed UI access, same-chat native evidence and model access（G01 已通過）

**Status:** blocked

2026-10-26（Asia/Taipei）：G01 正常接入與 clean readback 已通過；Desktop UI 控制仍被工具 app allowlist 拒絕，專用 Desktop state、同 chat 原生證據讀取與帳號模型資格尚未成立。沒有執行 UI 停止／選單試驗，不以 API Stop／M2 代測。詳見 [G07 資格與操作包](../research/harness-gap-closure-desktop.research.md)及[可審閱人工步驟](../research/harness-gap-closure-desktop-evidence/manual-runbook.md)。人工包就緒不等於行為驗收完成；本票維持 blocked。Windows 本輪明確排除。

依據：[補驗規格](../specs/harness-validation-gap-closure.spec.md)、[核准工作圖](harness-validation-gap-closure.plan.md)、[可行性研究](../research/unified-project-settings-gap-fixtures-feasibility.research.md)。使用者已核准拆分與驗收邊界；G08另經明確排除。

## 驗收條件

- [ ] 實際UI停止命中已開始工具，畫面與host終態、程序查核相互支持。
- [ ] UI模型切換前後的舊新worker身分與model context可查，舊worker未重啟。
- [ ] 不能分清日常state或取得宿主證據時保持受阻，不以API代測通過。

## 證據要求

保存候選／宿主／任務身分、expected → observed → raw → verdict及無關內容保留證據。控制器exit 0、模型自述、fixture或checker不單獨證明通過。未驗證與受阻保留，不以實作完成取代行為驗收。
