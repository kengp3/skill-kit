# Task Harness follow-up 修正研究

## 最新補充：candidate 1 失敗與 candidate 2 待驗證

2026-10-03 本次重新讀取 current worktree 與封存 evidence；本節更新現況，下方早期研究保留為歷史。此次未修改 runtime、未重跑案例。

| 分類 | 本次核對結果 | 影響 |
| --- | --- | --- |
| 已確認 blocker | [C56-R native trace](task-harness-followup-execution-20261003-evidence/native-traces/followup_56_resume.json) source_line 38 把 T1 寫成 task attempt 2、T2 寫成 1；[原始輸入](task-harness-followup-execution-20261003-evidence/sol56/original-inputs.json) 沒有歷史次數。 | G1 fail；不能把計數推論當成歷史事實。 |
| 已有功能／receipt 證據 | [artifact-checks](task-harness-followup-execution-20261003-evidence/artifact-checks.json) 四項 exit 0；[receipt-integrity](task-harness-followup-execution-20261003-evidence/receipt-integrity.json) 含 17 份可歸屬 receipts；[candidate1-verdict](task-harness-followup-execution-20261003-evidence/candidate1-verdict.json) 記錄其他 gates 已檢視。 | 這些屬 candidate 1，不能證明目前 candidate 2 通過。此次未完整重做所有時序 audit。 |
| 已恢復的驗證工具錯誤 | checker 曾把 shell wrapper 的 `; fi` 當 argv，及把 `git diff && runner` 中未啟動的 runner 誤配為 receipt 來源；verdict 留有修正紀錄。 | 屬 evidence checker 問題，與 Skill 的 attempt 缺陷分列；後續核對實際 command 是否啟動。 |
| 現有修訂，尚未驗證 | 現行 SKILL hash `99114ea67a51c28339a595ed846b3942a5b7d3125327592e7d4f4f57fdbdaf0d`，對 candidate 1 只改一段 Start 規則；runner 與 metadata 未變，execution2 evidence 目錄尚不存在。 | 下一步是驗證現有修訂，不是再次擴寫 Skill。 |

**根因界限**：直接可證明的是 coordinator 從不完整歷史推算數字。candidate 1 已寫「不得虛構未知次數」，卻沒有提供 reconcile 後仍未知時的明確記錄方式；這可能留下執行歧義，但不能證明是唯一因果。candidate 2 用「未知歷史＋具名 resume epoch＋局部計數」補上可執行方式，效果仍待測。

**方案取捨**：推薦保留現有窄修並驗證；重做 runner 無法直接解決語意推論。新增機械式 tracker 可以限制欄位，卻要承擔格式遷移與額外 runtime 成本，只有 candidate 2 明確失敗後才值得另案評估，不能此時自動加入。

本次重開查核官方 [Evaluation best practices](https://developers.openai.com/api/docs/guides/evaluation-best-practices) 與 [Trace grading](https://developers.openai.com/api/docs/guides/trace-grading)：前者支持先固定任務評估目標與判準，後者支持依工具呼叫等 trace 分析流程遵循。本專案據此分離功能結果、tracker 時序與 receipt 歸屬；這是本地落地選擇，官方文件並未規定四案例或兩候選上限，也不取代本地通過證據。

**不重新列為 blocker**：worker 無實際 overlap 不等於 coordinator 主動序列化。沿用 dispatch protocol；不恢復「全部 dispatch 早於 first completion」這個受 worker 速度影響的條件。crash／cancellation／其他 host 等未測邊界保留，不擴張本輪。

後續採先 resume、再同 hash parallel、最後固定 gate audit，詳見[修正計畫最新重規劃](../plans/task-harness-followup-remediation-20261003.plan.md#最新重規劃candidate-2-驗證與結案)。

---

日期：2026-10-03（Asia/Taipei）。本次僅研究與規劃；未修改 Skill、未啟動模型測試。研究以 current worktree、兩輪 raw traces 及一手工程文件為依據，不把單次模型行為推廣為能力結論。

## 現況與證據

現行 runtime 為 SKILL.md、agents/openai.yaml、scripts/run_check.py 三檔。SKILL.md SHA-256：`3635695f1cf027aa5c362b8379fe10ed4726d85ac7789243daab7028f742b732`。八案例受測的是先前 `6c2dfc…` 版本；新版僅有官方 validator 通過及舊 trace 重新判讀，沒有新的雙模型行為證據。

| 工作項 | 已確認事實 | 證據與定位 | 根因判斷 |
| --- | --- | --- | --- |
| REVAL-ATTEMPT-56／F5-DISPATCH | 派工 checkpoint 缺 numeric attempt；resume 第二次 check 前未保存 attempt 2。receipt 仍能區別兩次檢查。 | [重新驗證 trace](task-harness-revalidation-20261003-evidence/native-traces/reval03_56_parallel.json) source_line 36、56、69；[resume trace](task-harness-revalidation-20261003-evidence/native-traces/reval03_56_resume.json) 113、147。 | 已定位到 tracker 寫入內容；現行範本把 attempt 放在自由文字，table 沒有欄位。這是可改善的提示介面，尚未證明是模型漏寫的唯一原因。 |
| REVAL-HANDOFF-56 | T1/T2 標 done 時無可交接的版本 receipt；最終整合 receipt 才包含完整來源。 | 同一 parallel trace 36 的 worker scope 為 amounts.py／labels.py only；100、122 接受前置任務；[最終 tracker](task-harness-revalidation-20261003-evidence/sol56/parallel/tasks.md)。 | 派工契約缺 evidence 寫入範圍，計畫又將前置 verification 部分延至 T3。worker 不能自行擴權保存 receipt；coordinator 本可先重驗卻沒有做。scope 與 acceptance 必須一起修。 |
| F5-READY | 歷史 5.6 在 T1/T2 running 時啟動 T3 並修改 receipt.py，後來才接受 prerequisites。本次未重現，仍未針對性修復。 | [第五候選 trace](task-harness-sol61-sol56-remediation-202610-evidence/attempt5/native-traces/remfix5_56_parallel.json) 59、70；T1/T2 done 在 103、122。 | 模型將「可先實作、稍後驗證」套用至已宣告依賴的任務。既有規則已禁止，需在 coordinator 起始動作旁具體化前置條件；不能重寫依賴來讓歷史違規消失。 |
| REVAL-PAR-61 | 無實際 overlap；A checkpoint 回覆到 B dispatch 約 58.428 秒，兩次派工間沒有主動 wait／驗收。 | [並行修訂判讀](task-harness-parallel-gate-20261003.research.md)。 | 現行 dispatch protocol 下順序通過；延遲成因未確定。列觀測項，不加入此次修復 blocker，也不要求 worker 人工等待。 |

上述行號是匯出事件的 `source_line`。歷史 [findings](task-harness-revalidation-20261003-evidence/findings.json) 與 [follow-up backlog](task-harness-sol61-sol56-remediation-202610-evidence/attempt5/follow-up-backlog.json) 保留原樣；相同問題建立 alias，不重複計為兩項待修缺陷。

## 一手來源與可用結論

1. OpenAI 的 [Evaluation best practices](https://developers.openai.com/api/docs/guides/evaluation-best-practices) 建議先定義評估目標、資料與判準，採用任務專用測試；多 agent 的工具選擇與交接是額外的不確定性來源。因此本次驗收分別檢查 checkpoint、接受版本、相依任務啟動與功能成果。這是本專案的落地推論，文件未規定我們的欄位格式。
2. OpenAI 的 [Trace grading](https://developers.openai.com/api/docs/guides/trace-grading) 將 trace 用於判斷工作流程的正確性與遵循程度。據此以真實工具呼叫、回覆及當時的 tracker patch 檢查先後關係，不能只讀最終 done 表格。未導入雲端 grader；現有 native traces 足夠。
3. Anthropic 的 [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents) 說明 orchestrator-workers、獨立子任務並行及簡單可組合設計，也強調環境回饋與停止條件。此文章原發表於 2024-12-19，頁面提醒工具生態已有變動；本次只採用穩定的工作流程原則，不用它判斷目前 host API 或模型能力。

來源於 2026-10-03 開啟查核。上述來源支持評估方法，不能代替本機修復成功證據，也沒有證明 6.1 延遲的原因。

## 方案比較與推薦

| 方案 | 優點 | 代價／限制 | 決定 |
| --- | --- | --- | --- |
| 修整既有範本與 transition 契約 | 沿用三檔 runtime；直接處理觀測缺口，diff 小。 | Skill 仍是指令，無法提供程序式強制保證，必須 forward-test。 | 推薦第一階段。 |
| 新增 tracker parser／狀態寫入器 | 可對機器格式做欄位及 transition 驗證。 | 限縮既有 tracker 相容性、新增 runtime 與失敗模式；目前沒有證據需要這些成本。 | 此次不做；只有窄修失敗且定位到可機械驗證的原因時另提方案。 |
| 擴寫每次事後審核 | 能找到漏項。 | 修復太晚，可能已啟動相依工作；新增 reviewer 不能替代起始條件。 | 保留一次固定 gate audit，不疊 reviewer 層級。 |

最小修改位置為 [SKILL.md](../../skills/task-harness/SKILL.md) 的 tracker 範本、worker contract、Start one task、Accept/Persist 與 retry 條目。同步 [規格](../specs/task-harness.spec.md)，不新增 runtime helper 或修改 runner。

具體方向：attempt 可見且在每次執行前保存；worker 的程式 ownership 同時包含獨立 evidence 路徑；依賴接受與 done 保存成功後，coordinator 才保存 successor 的起始 checkpoint 並修改產品。缺 worker receipt 時由 coordinator 對目前 artifacts 做獨立檢查，不能事後回填成 worker 當時證據。

## 範圍與未驗證

這次規劃三個問題類別；並行 dispatch 新規則納入受影響 regression。工具 patch／非 Git fixture／collector matcher 錯誤已恢復，另保留改善項；crash、cancellation、interactive/binary output、non-Python host 仍未測，不擴張本輪。

現有 runner 已保存真實 argv、cwd、process returncode 與來源前後 hash，existing receipt 不覆寫／重播。此次問題位於調度和證據交接，沒有直接證據要求更換 runner 或引入資料庫／鎖服務。

完整任務、測試與結束條件見[修正計畫](../plans/task-harness-followup-remediation-20261003.plan.md)。本研究完成不表示任何 finding 已修復。
