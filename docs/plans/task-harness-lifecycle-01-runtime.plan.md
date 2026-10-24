# H01：合約驅動的必要 hook 行為

Status: ready-for-agent
Blocked by: None
Spec: [任務合約與必要 hooks](../specs/task-harness-lifecycle.spec.md)

What to build：從宿主事件讀取同一專案的權威合約，提供恢復/最新要求指示，並在資格與授權吻合時最多一次要求收尾補救。

- [ ] 結構與狀態驗證、限定查找、歸屬/依賴衝突與不受信任路徑拒絕。
- [ ] 三事件 CLI、Stop 模式/回合/資格檢查、unknown 不盲重播。
- [ ] 原子技術收據，重複與並行/輸出遺失不重置額度，不修改合約。
- [ ] 逐 slice red→green 的公共 CLI 測試，輸入上限與失敗為可見缺口。
