# 任務合約與必要 hooks：整合計畫

狀態：in_progress。整合分支 codex/task-contract-hooks；固定基線 6829db57f73d0a773fa01314aca6f1b81dd7f854。
規格：[非侵入式任務合約與必要 hooks](../specs/task-harness-lifecycle.spec.md)。本地 tracker 延續既有 docs/plans 慣例；每個 ticket 一個 plan，不發布外部 issue。to-spec/to-tickets 的確認由使用者「均採建議方案並持續開發」授權涵蓋。

## 已收斂的剩餘問題

1. 定位：專案靜態設定限定合約目錄，不建全域索引；同一對話只一個未結束任務。
2. 格式：同一 Markdown 固定標記 JSON 是機械欄位唯一來源。
3. Runtime：Python 3.10+ 標準函式庫；無自動安裝與 Homebrew 路徑硬編碼。
4. 補救額度：用原使用者回合技術收據 exclusive-create，原生 stop_hook_active 為另一拒絕重入依據；續作身份未驗證則接入未就緒。
5. 失效：不猜授權、不發續作；明示必要能力缺口，不宣稱 skill-only 完成。
6. 驗收：事件 CLI 與封裝 CLI 為本輪公共測試邊界；Desktop/模型驗收獨立保留，不啟動新 trial。

## Tickets

| ID | 成果 | 依賴 | 狀態 |
| --- | --- | --- | --- |
| H01 | 合約驅動的恢復、授權核對與一次補救 handler | 無 | done |
| H02 | 必要 hooks 完整候選封裝與套件外執行 | H01、H03 | in_progress |
| H03 | 任務生命週期 skill、合約範本與日常接入指南 | 無 | done |
| H04 | 整合驗證、兩軸 review 與證據對帳 | H01–H03 | pending |
| H05 | Desktop 真實接點與模型遵循資格 | H04、後續試行授權 | blocked |

## 保護與驗證

保留既有 .codex/config.toml 未提交還原、所有無關未追蹤內容、dist 舊候選與歷史證據。新實作 worktree 只基於整合分支；不複製未提交資料。測試用 tempfile，不操作既有 Desktop 聊天。
H01/H03 可各自實作，H02 等兩者整合後。依 skill 以獨立 worktree、TDD、固定基線 Standards/Spec 複核；只提交本輪明確檔案，無 push/PR。
完成後保存實際命令與結果到 research；測試結果不回填成 Desktop 資格。H05 未完成時整體 goal 不標 complete。

## 執行紀錄

- 2026-10-25：規格與 tickets 已保存；H01/H03 在獨立 worktree 實作，兩者僅修改明確責任檔案。
- 相關既有基線：22 項通過；外層 sandbox 的首次 3 項 grader 未驗證與原樣重跑結果均保留於 [baseline](../research/task-harness-lifecycle-evidence/baseline.json)。
- 宿主識別查核：[必要 hook 資格缺口](../research/task-harness-lifecycle-host-gap.research.md)。官方欄位不足以直接宣稱原使用者回合與自動續作鏈已驗證。

- H01/H03 已整合至 d24e2a1；主責在整合來源重跑 hook CLI 24 項通過（2.384 秒，Python 3.15）。H02 開始封裝；H04 尚待最終候選與獨立複核。
