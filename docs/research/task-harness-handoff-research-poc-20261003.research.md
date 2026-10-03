# Task Harness 交接研究與 PoC 決策

日期：2026-10-03。執行依據：[固定計畫](../plans/task-harness-handoff-research-poc-20261003.plan.md)。狀態：**R1–R4完成；Inconclusive，不採用B1。R5未觸發；正式 Skill 未改，原finding未關閉。**

## R1：結論與證據

選擇 A 路線的同契約最小指令調整作為唯一候選；先完成離線 oracle 校準才進模型比較。現行兩段保存仍是本輪 strict gate，不因本次未見產品損壞而改判歷史案例。

| 問題 | 判定 | 直接依據與限制 |
| --- | --- | --- |
| H1：分散指令造成交接合併 | unknown，合理但未證明 | 現行 Start、Accept、Persist 已有規則，5.6仍合併。只能證明未遵守，無法推知內部原因。R3只改呈現方式，其他條件固定。 |
| H2：兩次保存具有普遍安全必要性 | 未證明；本專案契約必要性 supported | 兩次操作讓「前置已完成、後繼尚未啟動」成為可觀察恢復點；第二次寫入失敗時可明確保留已接受結果。等價原子提交可能也安全，但目前沒有相應契約與實作證據。 |
| H3：patch成功即可證明原子性／持久化 | 不支持；本地實作保證 unknown | API文件明確把atomicity交給實作者選擇；不能把工具成功回覆推論成所有寫入的交易或斷電保證。 |
| H4：evaluator誤判曾導致返工 | supported | 歷史 audit-checker-errors.json 記錄 identity projection比較錯誤；R2 O8固定以retained fields與raw hash驗證。 |

### 實際事件對照

來源為 [6.1 trace](task-harness-revalidation2-20261003-evidence/native-traces/reval2_61_parallel.json) 與 [5.6 trace](task-harness-revalidation2-20261003-evidence/native-traces/reval2_56_parallel.json)。source_line為原始JSONL行號；R2另保存所用原始行hash及normalized slice。

| actor | acceptance | predecessor done | successor start | first product action | 判讀 |
| --- | --- | --- | --- | --- | --- |
| 6.1 parallel | source82讀取receipt、核對result及current fingerprints | source82第一個awaited command保存，成功結果見86及個別native事件 | source82第二個awaited command另存，成功結果見86 | source88 | 兩個依序成功的實際寫入；只有一個外層exec不構成違反。 |
| 5.6 parallel | source98讀取T2 source/receipt | source105同一patch | source105同一patch，108成功 | source114，117成功 | strict fail；沒有觀察到產品動作早於checkpoint成功。一次patch的atomicity unknown。 |

兩段保存具體保護的情境：前置done寫入失敗時不得啟動後繼；前置done成功而後繼start失敗時，恢復後可辨別已接受的前置與未執行的後繼。兩段保存本身不能保證斷電持久化、對抗其他writer改來源，或證明所有single-commit設計不安全。因既有契約明確且本輪目標為遵循改善，保留契約的成本是額外一次寫入；改為等價單次提交則需要新的primitive／freshness／recovery證據，不在本輪實作。

### 一手來源（查證於2026-10-03）

- [OpenAI Evaluation best practices](https://developers.openai.com/api/docs/guides/evaluation-best-practices)：輸出有變異，先固定任務目標、資料和評分，並校準自動評分與人工判讀。本輪採預登記對照，不引入雲端eval平台，也不以此文件證明本地根因。
- [OpenAI Apply Patch](https://developers.openai.com/api/docs/guides/tools-apply-patch)：operation執行後回報completed/failed；atomicity由實作者決定。這是API工具指南，不是本機Codex工具實作認證，因此只支持不能由success推論transaction的邊界。
- [Python os.replace](https://docs.python.org/3/library/os.html#os.replace)：成功rename的原子語意只適用該primitive；不能外推到apply_patch、整段workflow或crash durability。

## R2 oracle contract

沿用計畫O1–O8：strict遵循、產品安全觀察、證據有效性分開。缺必要結果為unverified；不能當pass或模型failure。fake writer只注入並記錄，不替模型強制流程。合成分支明確標記，不列為模型測試。R1已完成手工判讀；允許R2開始。

## 後续 checkpoint

R2完成且oracle可解釋才凍結唯一B1、8筆矩陣及holdout。R4必須給出Go／No-Go／Inconclusive；本報告不把研究完成等同修復完成。

## R2結果

[offline-result.json](task-harness-handoff-research-poc-20261003-evidence/offline-result.json)：21/21分支符合預期。O1 strict pass；O2 strict fail、early product=false；O3–O6正確停止無marker，非法繼續實際寫marker並被拒；O7缺證unverified；O8投影完整性檢查正確。獨立agent建立oracle，coordinator核對script、fixtures與結果hash。唯一修補將O7缺native判定從dispatcher移到passive judge，保留red/green/修補後實際程序輸出於[offline-executions.json](task-harness-handoff-research-poc-20261003-evidence/offline-executions.json)。這是驗收器校準，不是Skill修復證據。

候選只改Persist步驟，見[candidate.diff](task-harness-handoff-research-poc-20261003-evidence/candidate.diff)。B1官方validator已通過；正式Skill仍為B0。8筆中性prompt、B0/B1 hashes、同模型high reasoning、B0/B1/B1/B0順序及holdout已在[matrix.json](task-harness-handoff-research-poc-20261003-evidence/matrix.json)預先凍結。

## R3：固定雙模型對照結果

全部8筆完成，實際24個actors（8 coordinators、16 workers），模型均為預定的gpt-6.1-sol或gpt-5.6-sol且reasoning為high。每模型執行順序B0、B1、B1、B0，沒有補樣。502個tool events＝251對call/result，原始工具／identity／lifecycle行hash及retained-field projection已核對；未封存內部reasoning。

| Run | Model | Version | Handoff時序 | 功能整合 | 對照有效性 |
| --- | --- | --- | --- | --- | --- |
| hpoc_61_1 | 6.1 | B0 | pass | pass | clean |
| hpoc_61_2 | 6.1 | B1 | pass | pass | clean |
| hpoc_61_3 | 6.1 | B1 | pass | pass | clean |
| hpoc_61_4 | 6.1 | B0 | pass | pass | clean |
| hpoc_56_1 | 5.6 | B0 | pass | pass | clean |
| hpoc_56_2 | 5.6 | B1 | pass | pass | **confounded** |
| hpoc_56_3 | 5.6 | B1 | pass | pass | clean |
| hpoc_56_4 | 5.6 | B0 | pass | pass | clean |

- [逐案例結果](task-harness-handoff-research-poc-20261003-evidence/case-results.json)、[交接原生證據](task-harness-handoff-research-poc-20261003-evidence/handoff-evidence.json)：逐一人工判讀acceptance/done/start/product語意，並自動綁call ID、結果行及raw hashes；不是以最終tasks.md推算時序。各run均有兩個原生workers及逐一dispatch/checkpoint，再收集結果。
- [Receipt integrity](task-harness-handoff-research-poc-20261003-evidence/receipt-integrity.json)：31/31個receipts可唯一對回實際原生命令argv、cwd、process returncode與current source fingerprints。所有recorded acceptance commands回傳0；沒有拿外層batch exit代替child exit。
- [Artifact checks](task-harness-handoff-research-poc-20261003-evidence/artifact-checks.json)：封存後8份check.py各執行一次，8/8通過；[protected checks](task-harness-handoff-research-poc-20261003-evidence/protected-checks.json)全數無變更。
- [模型觀察](task-harness-handoff-research-poc-20261003-evidence/model-observation.json)、[時間觀察](task-harness-handoff-research-poc-20261003-evidence/timing-observations.json)、[raw usage](task-harness-handoff-research-poc-20261003-evidence/resource-observations.json)保留實際資料。worker lifecycle overlap不當作blocking gate，不推論CPU同時執行；token欄位不換算費用或宣稱效能優勢。

### 本輪錯誤及 disposition

| 觀察 | 證據 | 處理 |
| --- | --- | --- |
| **實驗context污染** | hpoc_56_2 source98 `list_agents {}`、source100結果包含39個scope外actors及歷史／offline oracle結果，見[confounds](task-harness-handoff-research-poc-20261003-evidence/experimental-confounds.json)。 | 當前功能與時序紀錄仍有效，但不列為clean comparison。這是實驗控制缺陷，不等同交接失敗；不修改候選、不補樣。 |
| Receipt inspector誤假設argv | hpoc_61_2 source106 exit1；實際worker採runpy，coordinator在source111修正讀取判準後才接受。 | 保留錯誤；沒有重播worker check或將failed inspection當成功。工具操作觀察，不阻塞本輪研究交付。 |
| 查無檔案／目錄 | hpoc_56_2/subtotal_worker的find、hpoc_56_3的rg各exit1。 | 找不到預期輸入的探索結果，非acceptance failure。 |
| Delete+Add同一路徑patch被拒 | hpoc_56_1、hpoc_56_3、hpoc_56_4各一次，改用Update後成功。 | 工具操作錯誤已恢復；無產品資料遺失。 |
| worker採python名稱，coordinator改用python3再驗證 | hpoc_56_1 T2、hpoc_56_4 T1。 | 原receipt仍保留；屬額外驗證成本，不能單由名稱推論不是Python 3。 |
| 歷史low observations | 部分5.6 workers仍未另存本地check-attempt metadata；receipt/實際check及coordinator記錄可追溯。 | 沿用既有worker-local-attempt backlog，不升格新blocker。本輪不主張所有metadata紀律均修復。 |

完整程序與工具錯誤見[process observations](task-harness-handoff-research-poc-20261003-evidence/process-observations.json)。Root collector曾因import產生一個歷史目錄的pycache，已以birth/mtime確認是本次建立並僅刪除此檔；collector加上禁止bytecode產生。這是收集工具副作用修正，未修改oracle或重跑模型；詳見collection-execution.json。

## R4：結束決策

**Inconclusive；不採用B1，R5不觸發。**

原始B0四筆全部符合handoff時序，未重現本輪要區辨的失敗。候選B1四筆雖也顯示正確時序，其中一筆受歷史結果污染，僅三筆是乾淨對照。即使忽略污染，也沒有證據能把改善歸因於B1。因此不宣稱根因已修復，不用本輪成功改判歷史失敗。

按事先固定的停止條件完成研究交付：不建立B2、不加跑樣本、不更動正式Skill/spec/runner、不為得到Go而改驗收。預先保留的parallel/resume holdout沒有執行；因R4非Go，不構成尚欠的必做測試。

原REVAL2-HANDOFF-ORDER-56保持open。3個既有low observations維持backlog。R1–R4工作完成的依據是研究、校準、固定樣本與決策均可追溯，並非修復成功。

**建議下一步：只做工具列舉範圍的隔離PoC，確認測試agent無法取得其他run／歷史verdict後，再決定是否值得另立新的比較實驗。** 這是後續建議，沒有在本轮啟動或新增goal；不再先改Task Harness指令。成本是隔離設定／host能力驗證，利益是避免把context污染誤認成修法效果。
