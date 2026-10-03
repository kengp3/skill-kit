# 普通資料夾功能驗收：固定範圍

使用者認為強隔離成本過高，建議普通測試資料夾／專案；其後 active goal 要求繼續執行。沿用已建立的四個 fixture 目錄，將測試定位改為功能 smoke test。使用標準 workspace-write，不再設計自訂 read-deny profile。共享宿主不保證盲測或不可存取其他案例；指示限制工作範圍，稽核實際工具操作，不作安全隔離或模型優劣／改善因果宣稱。

## Objective / Boundaries

驗證同一 native-first 候選的實際執行與恢復，成功後才評估正式採用。候選 SKILL.md SHA-256 固定為 970a338e499945b21d8ac045f1ed34fdda25e8d6c431735a3fb5d71a3c89d182。正式 runtime、hooks 與無關工作不變；不安裝、不改全域設定、不 commit/push。研究端收集 script 不納入 Core。

## Materials / Assumptions

沿用 portability-hooks 計畫 C1–C8、原 matrix 的四個 workspace 和兩模型。隔離診斷已保存原 session plan-only 結果。本輪只取消強隔離作為功能測試的前置條件，所有功能／安全／證據正確性条件保留。資料夾已是可用測試專案，不需要額外建立 Git repo、Codex sidebar project 或新使用者 chat。

## Tasks / Definition of Done

1. gpt-6.1-sol native-execution：resume 原 session 01a101fd-fb50-7c41-9bda-7d64a282e847，兩 worker 再 coordinator integration；先前 plan-only artifact 已有證據。
2. gpt-6.1-sol resume-negative：一次建立 PASS/exit7 原生 receipt 及合成 unknown checkpoint，終止後改 fixture 來源，再真正 resume；不可重跑舊 check 或重播 unknown。
3. gpt-5.6-sol native-execution：plan-only，終止後 resume 執行。
4. gpt-5.6-sol resume-negative：同第 2 項。
5. 逐項核對 C1–C8 的直接 evidence；選配 helper 的既有行為另做小型直接相容性檢查。review 固定 gates，不加入新 correctness 無關 blocker。

每案例至多一次，最多四個 coordinator sessions（第一個沿用既有），共至多四 workers。不因結果不理想改 candidate 或補樣。必要能力不足／實際固定 gate failure 則按既有停止規則記錄 No-Go 或 Inconclusive。完成研究不等於 portable Core 發布；Go 才最小套用 evidence 路由與 spec，保留 helper 內容。

四個案例的 workspace／evidence 各自獨立，沒有結果依賴；按上述次序啟動，可在等待既有案例時執行下一案例。每一案例自己的 plan/execute 或 checkpoint/resume 仍嚴格分回合，不把同時執行或速度當成功條件。確認 blocking failure 後不再啟動後續案例，已啟動者保留其結果。
