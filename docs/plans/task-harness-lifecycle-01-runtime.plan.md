# H01：合約驅動的必要 hook 行為

Status: implemented-offline
Blocked by: None
Spec: [任務合約與必要 hooks](../specs/task-harness-lifecycle.spec.md)

What to build：從宿主事件讀取同一專案的權威合約，提供恢復/最新要求指示，並在資格與授權吻合時最多一次要求收尾補救。

- [x] 結構與狀態驗證、限定查找、歸屬/依賴衝突與不受信任路徑拒絕。
- [x] 三事件 CLI、Stop 模式/回合/資格檢查、unknown 不盲重播。
- [x] 原子技術收據，重複與並行/輸出遺失不重置額度，不修改合約。
- [x] 逐 slice red→green 的公共 CLI 測試，輸入上限與失敗為可見缺口。

離線證據：[H01 runtime evidence](../research/task-harness-hooks-runtime-evidence/runtime.research.md)。公共 subprocess CLI 測試已通過；只代表合成事件與臨時檔案的確定性行為，不代表 Desktop 載入、user-turn 身分或真實模型遵循。宿主資格仍預設未驗證；H05 保留獨立缺口。
