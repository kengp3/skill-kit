# P1 離線實作：N04、候選封裝與 N06

狀態：進行中。固定基線 `205ca091bee6bdaaea2819d44bc6b0feb9ac84f7`；依既有規格、試行計畫 §20 與本輪使用者授權，在目前分支實作，不推送。採 ask-matt → implement → tdd → code-review；沿用本地計畫作追蹤。

## 範圍與驗收

- N04：只補 task-harness／ai-code-review 的併發、生命週期風險與自動證據原則，重用既有獨立 review 模式；不增加固定角色、hook 或人工觀察。
- 候選封裝依賴 N04：以新版本與獨立目錄建包，驗證內容、相依、指紋及套件外執行；既有 dist、marketplace、Desktop 設定、啟用版本與快取保持原樣。不安裝或刷新宿主。
- N06：schema 升版明示缺值，重用已存 RPC／固定結果，依 thread／turn／item 歸屬去重，保留原始參照、衍生統計與判讀。不從失敗命令或對話字詞猜求助／重試／修復，不以 wall time 推算人工投入。
- N06 可獨立於 N04 實作；舊資料回放不啟動 agent，不改原 smoke 結果。Desktop 接入、Stop、新模型行為與 N07 不在本輪。

## 已同意的測試邊界

1. 既有 package CLI：新目錄建包／驗包、完整 runtime 及獨立命令，不測宿主安裝。
2. 保存事件 → 摘要：主子回合歸屬、跨 turn 接續、重複／衝突／缺失事件及未知值。以真實 A／B／C 記錄和小型負向素材驗證，不依賴活躍 Desktop。

## 執行順序

1. [x] 讀取現況、保護基線、封裝基線測試。
2. [x] N04 精簡修改及內容／引用核對。
3. [x] N06 一個行為切片一次 red → green，舊資料產生新的衍生摘要。
4. [x] 新版本候選離線封裝、既有 package 檢查及必要補強。
5. [ ] 全部適用 unittest、來源／保護內容核對、Standards／Spec 獨立複核。
6. [ ] 同步規格／計畫狀態與交付證據；檢查 staged diff 後提交本輪內容。

完成證據寫入 `docs/research/codex-harness-p1-offline-20261024.research.md` 與同名 evidence 目錄；候選包使用 `dist/candidates/` 下新目的地，不納入日常來源。人工投入保持 unavailable。尚未執行的驗收均保留限制，不宣稱 N05 完成。
