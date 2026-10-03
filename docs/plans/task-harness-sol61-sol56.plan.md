# Task Harness 6.1 sol / 5.6 sol 重測任務

日期：2026-10-02。狀態：**六案例與錯誤收集完成；修正留待後續。**Authority：本檔；coordinator：`/root`。

## Objective

用 `gpt-6.1-sol`、`gpt-5.6-sol` 分別重新執行 plan-only、parallel execution、resume 三種情境，保存 current skill 指紋、真實模型與工具事件、最終 artifacts、錯誤清單，供之後修正。

## Materials / baseline

確認專案根目錄：`/Users/kengp3/Workspaces/mine/simple-skills`。現行 SKILL SHA-256：`948713f0c0720334b7c4ab355a78c11c162a4a14a19b683289a37e14abeec5be`。

沿用先前的原始 fixture preimages、保護檔案與 verifier，重新建立未完成的 inputs；不使用既有生成成果充當 fresh test。各模型 workspace：`/private/tmp/task-harness-solmatrix-mc_zeld9/sol61`、`/private/tmp/task-harness-solmatrix-mc_zeld9/sol56`。

## Boundaries / tools / permissions

本輪 skill、metadata、歷史報告唯讀；只新增本計畫、新 research 報告及 evidence。模型只修改所分配 temporary fixture。計畫測試只寫 tasks.md/evidence；執行測試可完成 fixture 程式；續作測試可修復 seeded math fault 並執行既有安全 local simulations。這些 fixture 操作是驗證範圍，不是修正 harness。

使用原生 subagents、list_agents、檔案工具、Python stdlib 與既有 validator/verifier。Parallel 各派兩名互斥寫入 worker，由 coordinator 整合；其餘不再派工。沒有網路、安裝、外部發送、commit、push 或發布。未指定成本／token 預算。

## 任務清單

| ID | 成果 | Depends on | Owner / handle | State |
| --- | --- | --- | --- | --- |
| A1 | 6.1 sol plan-only | none | /root/solmatrix_61_plan | done |
| A2 | 6.1 sol parallel execution | none | /root/solmatrix_61_parallel | done |
| A3 | 6.1 sol resume | none | /root/solmatrix_61_resume | done |
| B1 | 5.6 sol plan-only | none | /root/solmatrix_56_plan | done |
| B2 | 5.6 sol parallel execution | none | /root/solmatrix_56_parallel | done |
| B3 | 5.6 sol resume | none | /root/solmatrix_56_resume | done |
| C1 | 封存／驗證六案例，收集錯誤與限制 | A1,A2,A3,B1,B2,B3 | /root | done |

## Acceptance / verification

- Plan-only：保留來源與權限資訊，處理 A↔B 與 C→X 草案；每項 CLI acceptance 有可執行的驗證方式，空姓名的錯誤退出有檢查；不實作或派工。
- Parallel：實際成功啟動兩名原生 worker、寫入 scope 互斥、唯一 coordinator 寫 tracker；以原生事件核對 overlap 與 readiness；原始 check.py 通過。沒有同時 running 證據時記 gap，不由完成訊息推論。
- Resume：重新檢查舊 done、unknown send 不重播、缺工具 blocked、安全暫時錯誤 retry 一次、持續故障有界停止、未假報整體全部完成。
- C1：核對 requested model 與 native session 的實際 model 記錄；保存全部受測 actor tool calls/results、原始行指紋、protected inputs 與 final skill fingerprints。跑 verifier 只重播 check.py，禁止再次執行 send/probe/unavailable。
- 測試失敗不阻止收集工作完成。不得修改 skill 或手工修補生成產物，使失敗變成成功；須保留 failure、影響、證據、待修正狀態。

## Definition of Done / checkpoint

兩個指定模型都已實際嘗試，六案例有終態及可審查 evidence；模型不可用也須保留原生錯誤，不能換模型後冒稱完成。新 report 與 findings 保存於 `docs/research/task-harness-sol61-sol56-202610.research.md`、`docs/research/task-harness-sol61-sol56-202610-evidence/`。Current source 與歷史檔案保持原指紋。

已完成：六個 fresh 案例、十名 actor 實際模型核對、142 筆原生工具事件封存、兩模型安全 verifier、192 份既有檔案保存核對。所有受測 agents 都已 terminal，未重派。兩模型功能 assertions 通過，四項紀錄／證據觀察與四次已恢復 patch 錯誤保留待處理；測試完成不代表品質觀察已修正。

結果與完整限制見 [重測報告](../research/task-harness-sol61-sol56-202610.research.md)，結構化 errors 見 [findings.json](../research/task-harness-sol61-sol56-202610-evidence/findings.json)。本輪沒有修改 skill、metadata 或歷史證據，沒有未完成的收集任務。
