# 任務合約與必要 hooks：整合計畫

狀態：in_progress。整合分支 codex/task-contract-hooks；固定基線 6829db57f73d0a773fa01314aca6f1b81dd7f854。
規格：[非侵入式任務合約與必要 hooks](../specs/task-harness-lifecycle.spec.md)。本地 tracker 延續既有 docs/plans 慣例；每個 ticket 一個 plan，不發布外部 issue。to-spec/to-tickets 的確認由使用者「均採建議方案並持續開發」授權涵蓋。

## 已收斂的剩餘問題

1. 定位：專案靜態設定限定合約目錄，不建全域索引；同一對話只一個未結束任務。
2. 格式：同一 Markdown 固定標記 JSON 是機械欄位唯一來源。
3. Runtime：Python 3.10+ 標準函式庫；無自動安裝與 Homebrew 路徑硬編碼。
4. 補救額度：用原使用者回合技術收據 exclusive-create，原生 stop_hook_active 為另一拒絕重入依據；續作身份未驗證則接入未就緒。
5. 失效：不猜授權、不發續作；明示必要能力缺口，不宣稱 skill-only 完成。
6. 驗收：事件 CLI 與封裝 CLI 為離線公共測試邊界；H05 改驗實際 agent 與必要 hooks，不再要求 Desktop。相同核心／相關設定的證據可重用，實質差異才補驗。
7. 文件與工作單已完成；使用者更新目標後進入實作與離線驗證。新模型 trial 不自行擴張歷史額度，需符合明確核定範圍。

## Tickets

| ID | 成果 | 依賴 | 狀態 |
| --- | --- | --- | --- |
| H01 | 合約驅動的恢復、授權核對與一次補救 handler | 無 | done |
| H02 | 必要 hooks 完整候選封裝與套件外執行 | H01、H03 | done |
| H03 | 任務生命週期 skill、合約範本與日常接入指南 | 無 | done |
| H04 | 整合驗證、兩軸 review 與證據對帳 | H01–H03 | done |
| [H05](task-harness-lifecycle-05-desktop.plan.md) | 實際 agent 執行與 hook 整合驗收 | H05A、H05B、H05C | in_progress（只剩 V3） |
| [H05A](task-harness-lifecycle-05a-admission.plan.md) | 原生接入與有界補救（C0） | H04（已完成）；執行授權及接入條件 | done（完整接入與 C0 通過） |
| [H05B](task-harness-lifecycle-05b-behavior.plan.md) | 完整交付與授權遵循（C1、V1、V2、V5） | H05A | done |
| [H05C](task-harness-lifecycle-05c-recovery.plan.md) | 中斷恢復與結果不明（V3、V4） | H05A | in_progress（V4 通過，V3 未驗證） |

H05 舊檔名只保留引用相容性。預設 H05A → H05B → H05C 串行執行；H05C 不需等待 H05B 的產品結果，圖上的依賴只有 H05A。本地 tracker 沿用 docs/plans，不新增外部 issue；工作拆分與測試接口依使用者接受建議方案完成。

## 保護與驗證

保留既有 .codex/config.toml 未提交還原、所有無關未追蹤內容、dist 舊候選與歷史證據。新實作 worktree 只基於整合分支；不複製未提交資料。測試用 tempfile，不操作既有 Desktop 聊天。
H01/H03 可各自實作，H02 等兩者整合後。依 skill 以獨立 worktree、TDD、固定基線 Standards/Spec 複核；只提交本輪明確檔案，無 push/PR。
完成後保存實際命令與結果到 research；離線結果不回填成實際 agent 資格。H05 未完成時整體產品不標 complete。Desktop 不再是獨立待辦；歷史原始證據不改寫。

## 執行紀錄

以下為時間序紀錄；其中舊 Desktop 門檻與當時授權狀態已由本次修訂取代，不作現行執行指示。

- 2026-10-25：規格與 tickets 已保存；H01/H03 在獨立 worktree 實作，兩者僅修改明確責任檔案。
- 相關既有基線：22 項通過；外層 sandbox 的首次 3 項 grader 未驗證與原樣重跑結果均保留於 [baseline](../research/task-harness-lifecycle-evidence/baseline.json)。
- 宿主識別查核：[必要 hook 資格缺口](../research/task-harness-lifecycle-host-gap.research.md)。官方欄位不足以直接宣稱原使用者回合與自動續作鏈已驗證。

- H01/H03 已整合至 d24e2a1；主責在整合來源重跑 hook CLI 24 項通過（2.384 秒，Python 3.15）。H02 開始封裝；H04 尚待最終候選與獨立複核。

- H01–H04 已完成並整合至產品來源 81497d5：最終 101 通過、1 個 Windows 原生測試跳過；兩軸 review 的三個獨立問題修正後均已複核。候選 0.2.0 已建包驗證但未安裝。詳見[整合驗證](../research/task-harness-lifecycle-validation.research.md)。H05 維持 blocked，整體未完成。

- 清理限制：原生 archive_worktree 拒絕移除 workflow（目前主要 checkout）及 runtime（仍有其他 active task 使用）。保留兩份已提交工作樹，不以 shell 強制刪除。已詢問是否開放最多一個 Desktop 接點測試對話／一個使用者回合；未收到授權前 H05 不執行。

- 2026-10-25：使用者已授權一次有界 Desktop 接點驗證。接入預檢因未能建立符合限制的信任路徑而停止，未建立對話或啟動模型；目前阻礙是接入能力，不是重複等待授權。見[預檢結果](../research/task-harness-desktop-admission.research.md)。

- 2026-10-25：依最新決策，移除 Desktop 專屬完成門檻；設計改以實際 agent 行為、原生 hook 協定與固定產物驗收。H05 收斂為五個產品情境及兩個控制案例，拆為三個相依工作單。H01–H04 及歷史 101 通過／1 跳過結果保留，不把文件修訂算成新驗收。程式、候選與新 trial 本輪未動。


## 收斂後剩餘清單（2026-10-25）

1. **done：完整候選接入與停用。** 0.2.1 四個 skills／三個 hooks 已由原生宿主載入、正常信任、停用及移除讀回；限測試專用 state，見[接入證據](../research/h05-native-admission.research.md)。
2. **done：C0 真實事件與一次補救。** 探針及產品 handler 各一次，三事件與原 user-turn 可對帳。
3. **done：C1、V1、V2、V5 任務執行。** 完整成果、最新授權與小任務低負擔通過直接檢查及獨立審查。
4. **in_progress：只剩 V3 中斷與恢復。** V4 已通過，文件與證據對帳完成；V3 固定輸出事件未觸發，沒有真正中斷，故未開恢復 session。開發端觸發修正與離線回放已完成；只待另核定一次 V3 實際補驗後才可完成。

只修上述驗收暴露的必要缺陷；不增加 Desktop、其他宿主、OS/watchdog 或新評測框架。H01–H04 已完成內容不重做；沒有足夠直接證據的項目不標完成。

本輪 6 案通過／1 案未驗證、12 次輸入且無整案補跑。完整證據：[H05 行為驗收](../research/h05-agent-behavior-validation.research.md)。不因更換模型重跑全套，不擴張待辦。
