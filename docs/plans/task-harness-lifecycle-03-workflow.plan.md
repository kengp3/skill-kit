# H03：低負擔的任務生命週期

Status: ready-for-agent
Blocked by: None
Spec: [任務合約與必要 hooks](../specs/task-harness-lifecycle.spec.md)

What to build：使用者啟用後由主責 agent 維護唯一合約，推進、驗收、取消、接手、恢復及範圍調整都有明確且精簡規則。

- [ ] 恢復舊 skill 任務閉環，保留新版風險/修復原則與已確認簡化。
- [ ] 合約與專案設定範本跟 runtime schema 一致，host 資格預設未驗證。
- [ ] Hook 必要、Python 依賴、專案 opt-in/信任/驗收指引、未知能力不假通過。
- [ ] README 回到非侵入式任務管理，舊評測僅保留開發參考。
