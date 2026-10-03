# Task Harness follow-up 修正結果

2026-10-03（Asia/Taipei）。結論：**第二候選通過本輪四個固定 forward cases 與全部適用 G1–G5；本輪三類修正完成。** 第一候選的失敗證據保留，沒有第三候選或抽樣求綠燈。

## 修改與邊界

- Tracker 範本顯示 task attempt、check attempt 與 acceptance receipt；task restart 與 check retry 分開。未知歷史保留 unknown，安全續作使用具名 resume epoch 的局部計數。
- Worker ownership 包含獨立 evidence 路徑；缺少 worker verification 時，由 coordinator 對當前版本產生自己的 receipt。
- 前置任務自己的 receipt 經接受並成功保存 done 後，才保存相依任務的起始 checkpoint，接著修改產品。
- Runtime 保持 `SKILL.md`、`agents/openai.yaml`、`scripts/run_check.py` 三檔；本輪只修改 Skill 指令與同步 spec，runner／metadata 未變。未安裝、commit、push 或發布。

完整差異：[SKILL.final.diff](task-harness-followup-execution2-20261003-evidence/SKILL.final.diff)、[spec.final.diff](task-harness-followup-execution2-20261003-evidence/spec.final.diff)。最終 SKILL.md SHA-256：`99114ea67a51c28339a595ed846b3942a5b7d3125327592e7d4f4f57fdbdaf0d`；三檔 hashes 與隔離位置見 [run.json](task-harness-followup-execution2-20261003-evidence/run.json)。

## 結果與直接證據

| Case | Actual model | 流程 gates | 功能／恢復結果 |
| --- | --- | --- | --- |
| C61-R | gpt-6.1-sol | G1、G5 pass | 歷史 unknown、具名 epoch；修復 math；T4 75→0、T5 75→75；未知 send 不重播；deployctl 缺失維持 blocked。 |
| C56-R | gpt-5.6-sol | G1、G5 pass | 同上；T1 使用 R1-1，沒有再推定累計 attempt 2；T2 historical unknown。 |
| C61-P | gpt-6.1-sol | G1–G4 pass | 恰兩名 workers；各自 receipt 後接受 prerequisites；T3 checkpoint 後整合；check.py exit 0。 |
| C56-P | gpt-5.6-sol | G1–G4 pass | 同上；全部派工與逐次 checkpoint 後才主動 wait；T3 於兩個 done 成功後開始。 |

固定 gates 的逐項 raw trace 行號與判讀見 [fixed-gate-audit.json](task-harness-followup-execution2-20261003-evidence/fixed-gate-audit.json)。行號是 JSON 中的 `source_line`，指向原始 session，而不是匯出 JSON 的文字行號。

- [static-validation.json](task-harness-followup-execution2-20261003-evidence/static-validation.json)：官方 validator exit 0；兩模型隔離副本與現行 runtime hashes 一致。
- [model-observation.json](task-harness-followup-execution2-20261003-evidence/model-observation.json)、[trace-verification.json](task-harness-followup-execution2-20261003-evidence/trace-verification.json)：8 個原生 actors（4 coordinators、4 workers），actual model contexts 相符；170 個 tool events 的 raw hashes 核對，全部有 native terminal evidence。
- [receipt-integrity.json](task-harness-followup-execution2-20261003-evidence/receipt-integrity.json)：17 份 receipts 可對應實際 argv、cwd、process returncode 與穩定來源版本。
- [artifact-checks.json](task-harness-followup-execution2-20261003-evidence/artifact-checks.json)：封存後四項直接功能 checks 皆 exit 0。根 coordinator 沒有重播 send／probe／unavailable。
- [preservation-check.json](task-harness-followup-execution2-20261003-evidence/preservation-check.json)：2,243 個非授權變更範圍的既有檔案未變；collector 另驗證 fixture protected inputs 與兩項 simulation counters 各為 2。

5.6 parallel coordinator 在接受前讀取 source 與 receipt；本次 audit 由完整 writer traces、receipt 前後 hashes 及封存來源重建接受當時的版本一致性。沒有宣稱它執行了額外的 coordinator hash-comparison command，也沒有用後來 T3 的整合檢查替代 T1/T2 當時驗收。

## Finding disposition 與保留錯誤

[finding-dispositions.json](task-harness-followup-execution2-20261003-evidence/finding-dispositions.json)：`REVAL-ATTEMPT-56`／alias `F5-DISPATCH` 由 G1 關閉；`REVAL-HANDOFF-56` 由 G2 關閉；`F5-READY` 由 G3 關閉。只更新本輪 disposition，原始 findings 不覆寫。

[第一候選 verdict](task-harness-followup-execution-20261003-evidence/candidate1-verdict.json) 仍為 fail：C56-R 推定未知歷史計數。第二候選是唯一一次有直接根因證據的追加修訂。

[observed-process-errors.json](task-harness-followup-execution2-20261003-evidence/observed-process-errors.json) 保留 9 個非零 process 結果與 1 個 patch script error。其中 transient failures、missing-tool availability 是預期負例；讀取尚不存在的 evidence 目錄、非 Git fixture 上的 Git 操作及同路徑 Delete+Add patch 屬操作錯誤，後續流程未用它們冒充驗收成功。

[follow-up-backlog.json](task-harness-followup-execution2-20261003-evidence/follow-up-backlog.json) 保留三項低風險改善。5.6 workers 沒另寫獨立的 pre-check metadata，但保有 checks receipts；原定 G1 限定 dispatch、coordinator 執行與 safe retry 的 checkpoint，本次不事後擴充成所有 worker checks 的新格式 gate。

## 完成與限制

本輪依[修正計畫](../plans/task-harness-followup-remediation-20261003.plan.md)完成 P1–P4。Resume fixture 的 T2/T3/T5 保持 blocked 是正確測試結果，不是待修 Harness 功能，也不授權真的發送訊息或安裝工具。

每個最終案例只有一次 forward run；本結果證明固定案例下的修正與流程，不代表統計可靠率、所有 host 或所有未來任務均無缺陷。實際 worker overlap 仍屬觀測；crash／cancellation／interactive/binary output／其他 host 等未測邊界不列入本輪 closure。沒有額外 reviewer 階層或新增 runtime 機制。
