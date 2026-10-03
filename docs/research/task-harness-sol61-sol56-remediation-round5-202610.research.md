# Task Harness 第五候選結案

2026-10-03。**依使用者調整後的固定 closure contract，本次 remediation 已完成；保留兩項未修復、非阻塞 follow-up。**不宣稱所有調度規則零回歸，不自動建立 attempt6。

使用者引用「規劃 Harness 修正方案」（conversationId `6abfd1c1-dfe8-83e8-879a-bec56f92a8f6`）要求停止 DoD 持續擴張。已將固定七項與 safety／evidence gates 寫入[修正計畫](../plans/task-harness-sol61-sol56-remediation.plan.md)，取代原先所有新回歸都必須修復的結案要求；歷史結果保持原樣。

## 修正與結果

- 第五候選將 task completion 與 assessment subject pass criteria 分開；評估可以完成負面判定，修復任務仍須真正驗證通過。
- 新增 Python 3 stdlib `scripts/run_check.py`，每個 command 保存 actual argv、cwd、process returncode、stdout/stderr 與 source fingerprints；tracker 引用 receipt，避免手抄退出碼與指紋。既有 receipt 不覆寫、不自動 replay。
- 原四項 STATE-02／STATE-03／EVID-56-02／EVID-61-02，以及 F-NEG-STATE／F-EXIT-56／F-HASH-56，均在最終候選適用案例取得直接通過證據。
- gpt-6.1-sol 與 gpt-5.6-sol 各完成 plan-only、parallel、resume、misleading，共八例。12 actors、192 native tool events／96 call-result pairs、22 JSON receipts 已核對；两模型 verifier exit 0。負例保留 checker exit7 與後續 hash exit0，正確拒收。
- 三檔 runtime 與兩個隔離副本／封存副本一致；官方 Skill validator、runner 最小隔離自測通過；454 份歷史與無關檔案、fixture 保護輸入保持不變。沒有安裝、commit、push、發布或未授權外部動作。

最終 SKILL.md SHA-256：`6c2dfcfc7b0d4c9fdcdbfbfffb7f562e7c246cf41e0fc4a0cda51ce4b4d77cdf`；全部 runtime fingerprints 見 [run.json](task-harness-sol61-sol56-remediation-202610-evidence/attempt5/run.json)。引用對話的 `2c0b96…` 是第四候選，不作為第五候選證據。

## 未修復的 follow-up

| 項目 | Severity | 本次處置 |
| --- | --- | --- |
| F5-DISPATCH | low | 5.6 dispatch 缺 attempt，resume retry tracker 亦有舊 attempt；實際執行與逐次 receipts 仍可歸屬。保留後續改善。 |
| F5-READY | medium | 5.6 在 prerequisites accepted 前開始 T3 實作，違反 readiness；最終 integration check 與 done 均在前置有效驗收之後，未直接造成固定 correctness gate failure。保留後續改善。 |

[Follow-up backlog](task-harness-sol61-sol56-remediation-202610-evidence/attempt5/follow-up-backlog.json) 保留證據、影響及建議，不自動執行。依本次固定結案契約，這些問題非 blocker；它們仍是真實 open findings，不能稱為已修復。

## 證據與限制

[獨立審核](task-harness-sol61-sol56-remediation-202610-evidence/attempt5/review-final.md) 逐項列出 gate、raw call_id／source_line 與判定；[完成稽核](task-harness-sol61-sol56-remediation-202610-evidence/attempt5/completion-audit.json) 對應本次固定要求。

runner 僅驗證 Python 3、小型非互動命令；crash/cancellation、interactive/binary output、non-Python hosts 未測，不阻塞此固定範圍。一次雙模型案例不推估可靠率，也不證明所有未來任務必然遵守每條指令。Resume fixture 的 T2/T3/T5 保留 blocked 是預期安全判定，不代表本 remediation 未完成。
