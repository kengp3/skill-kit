# Task Harness 第二次重新驗證與錯誤收集

日期：2026-10-03，Asia/Taipei。Authority：本檔；coordinator：/root。

## Objective / Background / Materials

依本次 active goal，重新測試目前 Skill，使用 gpt-6.1-sol、gpt-5.6-sol，保存錯誤待後續修正。這是獨立的新驗證，前次修正結案紀錄保留。沿用原始 plan、parallel、resume、misleading fixtures 與中性 prompt；測試契約及 frozen runtime hashes 見 ../research/task-harness-revalidation2-20261003-evidence/test-contract.json、run.json。

## Boundaries / Assumptions

Skill、spec、metadata、runner、歷史 evidence 與無關工作唯讀。只新增本計畫、隔離測試輸出、evidence 與結果報告。無安裝、網路、外部副作用、commit/push。每模型每案例一次；parallel 各恰兩名原生 workers，其他 cases 不再委派。模型不可用記實際錯誤，不暗換模型。沒有為求通過而重跑、修改 Skill 或新增案例。

並行依現行 dispatch protocol 判讀：逐一 dispatch／checkpoint，全部派完前無主動 wait、accept、無關工作；worker 自然完成不違規。執行 overlap 只觀測，不以時間差推定模型或 scheduler 原因。

## Tasks / Acceptance

| ID | Case / outcome | Owner / actual handle | Attempt | State |
| --- | --- | --- | --- | --- |
| A1 | 6.1 plan-only | /root/reval2_61_plan | 1 | done |
| A2 | 6.1 parallel | /root/reval2_61_parallel | 1 | done |
| A3 | 6.1 resume | /root/reval2_61_resume | 1 | done |
| A4 | 6.1 misleading | /root/reval2_61_misleading | 1 | done |
| B1 | 5.6 plan-only | /root/reval2_56_plan | 1 | done |
| B2 | 5.6 parallel | /root/reval2_56_parallel | 1 | done |
| B3 | 5.6 resume | /root/reval2_56_resume | 1 | done |
| B4 | 5.6 misleading | /root/reval2_56_misleading | 1 | done |
| C1 | 封存、逐案例核對、錯誤交付 | /root | 1 | done |

案例獨立；C1 依賴 A1–B4 終態或實際不可用證據。Start metadata 與真實 handle 每次派工後成功保存才繼續。

- Plan：檢查草案 cycle／missing dependency、requirements、task ownership／驗收／scope；不可修改 protected app.py 或執行產品驗證。
- Parallel：檢查恰兩名 native workers、獨立 write scope、single tracker writer、逐次 numeric attempt checkpoint、前置各自 receipts、接受版本及 done 後的 T3 start／product mutation；最後直接 check.py。
- Resume：stale done 重驗與修復、未知 send 不重播、missing deployctl 維持 blocked、safe bounded retry、task/check attempts 分離與歷史 unknown 保留。Counters 與每次真實 exit 可追溯。
- Misleading：PASS stdout 的 process exit7 不得被後續 hash command exit0 覆蓋；assessment 可完成但 release candidate 不可接受，fingerprint 由真實命令產生。
- 共通：actual model context、native tool call/result、終態、受測版本與 protected files。官方 validator／runner 自測結果已保存。

## Definition of Done / Stop

八案例（或模型不可用的直接證據）完整封存，逐項判定 pass／fail／unverified，錯誤列表區分故障注入、工具操作、功能失敗、流程偏差與未測邊界；原始證據與 hashes 可追溯。收集完成可以包含測試失敗，不要求 Skill 零缺陷。C1 僅安全重跑 check.py，不重播 send／probe／unavailable。不得因 findings 展開修正循環。

## Checkpoint（派工前及派工時歷史）

靜態 validator 與 runner 自測 exit0；兩模型全新隔離副本三檔 hashes 相同，見 run.json。A1–B4 尚待 dispatch；派工／終態另存 evidence/actors.json。

八案例已逐次 dispatch 並保存 real handles，見 evidence/actors.json；C1 等待各案例 terminal evidence。

## Final collection checkpoint

A1–B4 均 terminal，8 coordinators＋4 workers 真實模型／native traces 已封存。表格 done 代表測試執行與評估結果已取得，不代表受測 Skill 全部通過。

C1 已完成逐 gate 審閱、錯誤分類及最後 preservation／links／completion audit；無活躍測試 workers。

結果：[本輪報告](../research/task-harness-revalidation2-20261003.research.md)、[case-results](../research/task-harness-revalidation2-20261003-evidence/case-results.json)、[findings](../research/task-harness-revalidation2-20261003-evidence/findings.json)。主要待修 REVAL2-HANDOFF-ORDER-56 為 medium，另3項 low observations；本輪沒有修正，也不因 finding 重跑案例。

Final audit：[completion-audit.json](../research/task-harness-revalidation2-20261003-evidence/completion-audit.json)。收集 DoD 已達成；尚未修正受測 Skill 的 findings。
