# Task Harness 2026-10-03 重新驗證與錯誤收集

Authority：本檔。Coordinator：/root。狀態：測試與錯誤收集完成；修正留待後續。

## Objective / Background

依當前明確目標，以 gpt-6.1-sol、gpt-5.6-sol 重新驗證目前 Task Harness，收集錯誤待之後修正。前次 remediation 已依固定 closure contract 結案；本次是另行要求的新測試，不是自動 attempt6。

## Materials / Boundaries

確認專案：/Users/kengp3/Workspaces/mine/simple-skills；文件遵循 project-setting.md。使用 skill-creator 的獨立 forward-test 原則、using-agent-skills 的驗證與範圍規則、ponytail 的既有工具與最小檢查。

目前三檔 runtime 與前次結案版本相同，精確 hashes、隔離根目錄见 ../research/task-harness-revalidation-20261003-evidence/run.json。從原始 preimages 重建兩模型同版 fixtures，不複製已完成成果／receipt／counter。歷史證據、Skill／metadata、README 全部唯讀；只新增本計畫、新 evidence 與 research 報告。Fixture 實作僅為测试；不修正 harness、不安裝、不連網、不發送外部通知、不 commit/push。

## 任務清單

| ID | 成果 | Depends on | Owner / handle | Attempt | State |
| --- | --- | --- | --- | --- | --- |
| A1 | 6.1 plan-only | none | /root/reval03_61_plan | 1 | done |
| A2 | 6.1 parallel | none | /root/reval03_61_parallel | 1 | done |
| A3 | 6.1 resume | none | /root/reval03_61_resume | 1 | done |
| A4 | 6.1 misleading negative | none | /root/reval03_61_misleading | 1 | done |
| B1 | 5.6 plan-only | none | /root/reval03_56_plan | 1 | done |
| B2 | 5.6 parallel | none | /root/reval03_56_parallel | 1 | done |
| B3 | 5.6 resume | none | /root/reval03_56_resume | 1 | done |
| B4 | 5.6 misleading negative | none | /root/reval03_56_misleading | 1 | done |
| C1 | 封存、核對模型／結果與收集錯誤 | A1–B4 | /root | 1 | done |

## Acceptance / Definition of Done

各模型每案例一次，不向受測代理透露預期答案、舊 findings 或修正方式；parallel 各用兩名原生 workers，其他不再委派。保存實際模型、tool call/result、終態、tracker、程式與 receipts。模型不可用則保留錯誤，不暗換模型。

檢查 plan-only／依賴／owner／scope、dispatch checkpoints／ready work／single writer／overlap、個別驗收退出碼與source版本、stale done／未知 send 不重播／缺工具阻擋／bounded retry、PASS字樣但exit7的歸屬。官方validator與runner自測在本次環境取得直接結果。

C1只安全重跑 check.py，不重播 send/probe/unavailable；protected inputs、runtime與歷史／無關檔案hash不變。保存 findings，區分預期故障注入、工具操作錯誤、功能失敗、流程偏差與未驗證；不因發現錯誤進入修正或新增案例。收集完成可有失敗結果；本目標的done表示測試與錯誤交付完整，並非Skill零缺陷。

## Checkpoint

八案例／十二actors皆terminal；實際gpt-6.1-sol、gpt-5.6-sol已核對。222 tool events／111 call-result pairs、21 receipts與完整fixtures已封存；兩verifier、officialvalidator與runner自測exit0。906份歷史／無關檔案及三檔runtime不變。

C1 done代表測試與錯誤交付完整；6.1 worker overlap未達標，5.6 attempt與驗收handoff缺口保留待後續。預期故障注入及已恢復的工具操作錯誤另列，不擴張為產品failure。

[報告](../research/task-harness-revalidation-20261003.research.md)、[findings](../research/task-harness-revalidation-20261003-evidence/findings.json)。沒有active test workers、沒有Skill修正，沒有重跑同case抽樣或自動後續工作。
