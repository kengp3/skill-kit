# Task Harness 修正與雙模型驗證

日期：2026-10-02。結論：**已套用最小修改並完成兩輪 fresh 測試；部分修復，尚未滿足全部修正 DoD。**

規劃交接、受測版本及原 resume 的退出碼問題在最終案例通過；派工與整合狀態有所改善，但狀態同步仍有殘留，且在 helper 路徑發現同類退出碼證據缺口。沒有將失敗產物手工改成成功，也沒有以功能 checker 通過代稱完整行為驗收。

## 修改與版本

- 唯一修改的 Skill 檔案：[SKILL.md](../../skills/task-harness/SKILL.md)。[完整差異](task-harness-sol61-sol56-remediation-202610-evidence/final-source.diff)；`agents/openai.yaml` 不變，沒有新增 runtime 檔案、套件或 scheduler。
- 修改前 SHA-256：`948713f0c0720334b7c4ab355a78c11c162a4a14a19b683289a37e14abeec5be`。
- 候選一：`207d2881574786802feda83dea09cfd99cf7e3874ff9234caed57993b656656b`。模板補 current coordinator／tools；命令要求個別 exit；驗收綁定版本；prerequisite done 先於 dependent 實作；checkpoint 刷新 worker liveness。
- 最終候選二：`20387010c2d448d08e08e51b5985ab80696b75b1d65a1bdffefc4a4486ce4c04`。因候選一 helpers 仍從 pending 直接 done，進一步明定每次成功 dispatch 後立即保存 owner／attempt／handle／running；產物已可驗收則記 verifying。保留 coordinator 接受證據後才能 done 的通用規則。
- 兩候選均通過官方 `quick_validate.py`；此檢查只證明 Skill 格式有效，沒有取代行為驗證。

## 方法與範圍

依 [修正計畫](../plans/task-harness-sol61-sol56-remediation.plan.md) 使用 skill-creator 的 fresh forward-testing、using-agent-skills／incremental-implementation 的分段驗證，以及 ponytail 的最小修改方式。

每輪均由 `gpt-6.1-sol`、`gpt-5.6-sol` 各測 plan-only、parallel、resume，合計兩輪十二案例、二十名受測 actors。每個 parallel 案例恰好兩名原生 helpers；其他案例不委派。受測者只有 Skill、真實任務與原始 inputs，沒有收到 findings 或預期答案。

沿用原始 fixture preimages、checker、verifier 和 prefix-only 調整的 exporter；生成產物位於隔離 temporary workspace，完成後封存。候選二修正了候選一測試 envelope 誤寫的 `source/check.py` 路徑，兩模型一致改為實際 `check.py`；因此不將前後差異當作單一指令變更的因果實驗。

- 候選一：[run](task-harness-sol61-sol56-remediation-202610-evidence/run.json)、[獨立審核](task-harness-sol61-sol56-remediation-202610-evidence/review-final.md)。十名 actors、162 筆 tool call/result events。
- 候選二：[run](task-harness-sol61-sol56-remediation-202610-evidence/attempt2/run.json)、[原生模型核對](task-harness-sol61-sol56-remediation-202610-evidence/attempt2/model-observation.json)、[trace 完整性](task-harness-sol61-sol56-remediation-202610-evidence/attempt2/trace-verification.json)。十名 actors、144 筆 tool call/result events；另保存原生 command／terminal lifecycle events。
- 最終兩模型 verifier 均 exit 0、`failures: []`：[6.1 sol](task-harness-sol61-sol56-remediation-202610-evidence/attempt2/sol61/verification.json)、[5.6 sol](task-harness-sol61-sol56-remediation-202610-evidence/attempt2/sol56/verification.json)。這是功能／保護檔案／retry counter 檢查，並非狀態時序或語意通過證明。

## 原四項觀察的結果

| ID | 最終案例結果 | 判定範圍 |
| --- | --- | --- |
| REC-56-01 | 兩模型 plan-only 均有 current coordinator、workspace／baseline、tools／permissions；future owner 另列 unassigned，未實作或派工 | 本輪通過 |
| EVID-56-01 | 四 helper 與兩組 integration evidence 有來源 fingerprint，coordinator 有版本核對 | 本輪通過；命令描述及 exit 真實性另列缺口 |
| EVID-61-01 | 兩 resume 的 probe／unavailable retry 具有可區分結果；unknown send 不重播、缺工具 blocked、bounded retry 保留 | 原 resume 路徑通過；不能推論所有 helper 路徑都遵守個別 exit 規則 |
| STATE-01 | 每名 helper 成功派工後有 running／handle／attempt；兩模型先記 helper done 和 receipt running 再實作；final active 狀態正確 | **部分改善，保持 open**；5.6 額外驗證任務仍同批結案，resume 修改前 running 的持久化亦未獨立證實 |

## 尚未關閉的問題

1. **STATE-01／STATE-02：驗證任務仍落後。**5.6 parallel 額外建立 T4「執行整合 checker 並保存證據」，依賴 T3。即使第一次 checker 視為 T3 自驗，第二次 checker 執行時 T3 仍 running、T4 pending，最後才同批改 done。見 `remfix2_56_parallel.json` 的 `call_Kr6aThD9WwDR1LIbl5WT1XGQ`（source 120）、`call_RFQQbl9t3KDJb24gcfWO7Wt0`（134）、`call_3sVHJL4glJEo9czU08MtdxW6`（141）。無法將每次 checker invocation 確定歸屬 T3 或 T4；可確認的是 T4 從 pending 直接 done，沒有啟動或調整任務定義的紀錄。另以 **STATE-03** 記錄：5.6 resume 在同一 patch 更新來源與 running 狀態，沒有來源修改前已保存 running 的獨立證據。不以 patch 文字順序冒充 OS 寫入鑑識。
2. **EVID-56-02：helper 的個別 exit 來源不足。**5.6 label worker 合併 Python assertions 與 `sha256sum`，唯一 process exit 0 屬整批，卻在 evidence 分別列各命令 exit 0。見 `remfix2_56_parallel--labels_worker.json` 的 `call_jQB1UmMaE5te5Wm3mClddlCH`（source 39/42）、`call_9F3wUN1YrRerHsDxk9EOyq7x`（48）。PASS 輸出與整合檢查支持功能正確，但不足以補出未單獨觀測的退出碼。這是原退出碼問題的同類新路徑。
3. **EVID-61-02：命令記錄不精確。**6.1 label worker 實際在 Python heredoc 中執行 assertions，evidence 卻寫等價的 `python -c`。測試確實執行、hash 正確，命令欄位不是實際 invocation。見 `remfix2_61_parallel--labels.json` 的 `call_fqKma2I3dDBDyEcvEQh9x3gx`（source 26）。

最終 [獨立證據審核](task-harness-sol61-sol56-remediation-202610-evidence/attempt2/review-final.md) 確認上述部分修復結論。詳見 [結構化 findings](task-harness-sol61-sol56-remediation-202610-evidence/findings.json)。以上皆未觀察到錯誤產品輸出、互相覆寫或外部副作用；問題在中途狀態與交接證據的可信度，不能因此略過。

## 工具錯誤、觀測限制與保存

兩輪都出現同路徑 Delete＋Add patch 拒絕，已改用 Update 恢復；兩輪各有一次 zsh 保留變數 `status` 造成 wrapper 失敗，均保留失敗與後續驗證。這些沒有被改寫成 Skill 已消除的錯誤。non-Git、尚未建立的 tracker、缺少 deployctl 及 seeded service exit 75 分別列為環境／故障輸入。

「第二次 spawn 後立即 list_agents」是明示測試觀測控制，兩模型皆因此在第二個 helper tracker 更新前先做一次唯讀觀測；不把此控制造成的順序當作通用指令 failure。候選二兩組皆有原生 lifecycle overlap 證據；只代表 worker 生命週期重疊，不代表硬體同時計算或效能提升。

plan-only 的輸出格式、至少一筆金額及純空白姓名仍有明示假設差異，原契約未完全指定，未升格為功能 bug。每個模型／情境／版本只有一次 fresh run，結果不能推估穩定通過率。

[保存核對](task-harness-sol61-sol56-remediation-202610-evidence/preservation.json) 確認 290 份原有相關文件及 metadata／README 指紋未變。最終 Skill 是上述候選二；候選一失敗、兩輪產物及原始歷史 evidence 保留。沒有安裝、commit、push、發布或外部發送；收集器只重驗安全 checker，沒有重播 send／probe／unavailable。

## 後續處理

本輪實作、雙模型重測與錯誤記錄已完成，**全部修正 DoD 尚未達成**。依計畫停止堆疊同義規則。下一步應先重新診斷「驗證被拆成依賴任務」及「worker 把可推論結果寫成實測 receipt」的形成原因，評估收斂任務與證據交接格式，再用針對性 fresh 案例驗證；不要直接新增 scheduler 或平台專用語法。
