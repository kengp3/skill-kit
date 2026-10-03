# Task Harness 2026-10-03 雙模型重新驗證與錯誤收集

**本次測試與收集完成，Skill未修改。**gpt-6.1-sol及gpt-5.6-sol實際各執行四例，兩模型功能檢查與負例拒收正確；6.1並行案例沒有實際worker重疊。保留兩個流程觀察及一個驗收證據缺口，待後續修正。

## 範圍與方法

依使用者本次目標重新驗證並收集錯誤；前次remediation已結案，本次是新的明確測試要求。使用skill-creator獨立forward-test、using-agent-skills驗證／範圍與ponytail既有工具原則。每模型case一次，不因結果不理想重跑；不提示舊findings或desired answer。Fixture內必要實作及安全模擬是測試操作；沒有修正harness、安裝、網路、外部發送、commit/push。

受測SKILL SHA-256：`6c2dfcfc7b0d4c9fdcdbfbfffb7f562e7c246cf41e0fc4a0cda51ce4b4d77cdf`，與前次結案版本相同。完整三檔runtime、workspace與實際模型資訊見[run.json](task-harness-revalidation-20261003-evidence/run.json)、[模型觀測](task-harness-revalidation-20261003-evidence/model-observation.json)。由原始preimages建立兩模型新fixtures，沒有沿用已完成程式、receipts或counter。

## 結果

| 案例 | 6.1 sol | 5.6 sol |
| --- | --- | --- |
| plan-only | 僅改tasks.md，處理循環／不存在依賴，驗收涵蓋錯誤退出 | 同左；一次patch操作失敗後恢復 |
| parallel | 函數與整合checks通過；兩workers**沒有重疊** | 函數与整合checks通過，重疊約22秒；attempt／前置驗收交接存在缺口 |
| resume | 舊done重新驗證，修復後通過；不重送、缺工具阻擋、retry有界 | 同左；一次patch操作失敗後恢復，retry前缺numeric attempt更新 |
| misleading negative | check exit7、hash exit0，正確拒收；assessment done | 同左 |

12名受測actors都已terminal，實際模型符合requested model；222筆raw tool events／111組call-result、21份JSON receipts已封存並核對。兩模型安全verifier exit0，但它只證明功能、protected inputs與counters，不涵蓋調度時序。906份歷史／無關檔案與current runtime未變。

官方validator與runner隔離自測均通過。21份receipt對到native命令的exact argv／cwd／process returncode；source hashes屬封存current或明確的原始失敗preimage。非零退出碼不一律是Skill缺陷：負例exit7、故障注入、missing tool和service不可用都保留原結果。

## 待後續處理的觀察

| ID | 判定／影響 | 直接證據 |
| --- | --- | --- |
| REVAL-PAR-61 | medium，並行驗證未達標。amounts終態後約29秒labels才開始；兩名worker及功能成功不能代替overlap證據。成因未定，不推估可靠率。 | [原生區間](task-harness-revalidation-20261003-evidence/parallel-overlap.json) |
| REVAL-ATTEMPT-56 | low，dispatch只保存handle/state；retry第二次開始前缺numeric attempt更新。實際分次receipt仍可追溯，沒有無限重試。 | [findings](task-harness-revalidation-20261003-evidence/findings.json) 的call/source_line |
| REVAL-HANDOFF-56 | low，T1/T2標done時缺receipt／fingerprint引用；最終T3才有完整來源receipt。獨立worker Pythonchecks的exit0与最終整合成功可驗，但前置驗收當時版本交接不足。未確認產品功能失敗。 | [56 tracker](task-harness-revalidation-20261003-evidence/sol56/parallel/tasks.md)、[raw coordinator trace](task-harness-revalidation-20261003-evidence/native-traces/reval03_56_parallel.json) |

**全部留待後續，沒有修正Skill或手工補造受測outputs。**5.6本次在前置done後才開始T3，上一輪提前整合觀察未在此案例重現；不能據此宣稱已修復或所有未來run穩定。

## 工具操作錯誤與限制

- 5.6 plan/resume各一次同路徑Delete+Add patch被拒。plan改Update，resume分兩次Delete/Add成功；保留拒絕回執與恢復動作。沒有永久資料遺失，resume曾有短暫tracker不存在區間。
- 非Git fixture中的status/diff產生exit128／129。兩workers把Pythoncheck與gitdiff拆開，獨立assertions實際exit0；不以batch結果推造Python退出碼。
- 收集器自身兩次匹配錯誤已恢復：relative receipt路徑必須以native cwd對帳；讀取runner原始碼不等於執行runner。修正的只是新evidence checker，沒有重播fixture。見[collector-errors](task-harness-revalidation-20261003-evidence/collector-errors.json)。

[原生非零命令／工具錯誤](task-harness-revalidation-20261003-evidence/observed-process-errors.json)保存15個非零shell/process結果與兩次script error；它們包含預期故障，不能計成17個Skill缺陷。

本次未增加crash/cancellation、interactive/binary-output或non-Python host案例；只有一輪，無可靠率估計。已結束收集工作，沒有active test workers。後續是否修正及如何修正另依使用者需求處理。

完整[收集完成稽核](task-harness-revalidation-20261003-evidence/completion-audit.json)與[任務清單](../plans/task-harness-revalidation-20261003.plan.md)對應本次目標。
