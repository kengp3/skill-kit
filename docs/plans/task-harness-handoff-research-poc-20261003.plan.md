# Task Harness 交接問題：研究、PoC 與修正決策計畫

日期：2026-10-03（Asia/Taipei）。狀態：**已完成研究與PoC；R4 Inconclusive，不採用B1；R5未觸發，原finding未關閉。**

## Objective

針對 REVAL2-HANDOFF-ORDER-56，先以既有證據、限定研究及隔離 PoC 判定問題所在與可行方案，再決定是否修改正式 Skill。交付可驗證的決策，避免「多加規則→碰巧一次通過→又改規則」循環。

原始規劃請求只授權規劃；後續執行授權與完成結果見本檔末段。本檔是後續工作的唯一任務清單；不重開已結案的驗證 goal。當使用者接續要求執行研究／PoC 時，依 R1–R4 推進；正式 Skill 修改屬 R5 的後續執行範圍。

## Background

- 前次八案例測試與錯誤收集已結案，並非 Skill 零缺陷結案。留下1項 medium finding、3項 low observations。
- 5.6 parallel 原生 trace：source98讀 T2 source/receipt；105同一 patch 保存 T2 done 與 T3 running；108保存成功；114才修改 receipt.py。功能及整合檢查通過。
- 現行 Skill/spec 已明文要求兩段保存。因此「規則缺失」不是已證明的根因；重複加同樣一句話不能視為修復。
- 本次已重新讀取實際 trace、findings、current Skill/spec/runner，並做官方資料的初步查證；尚未進行實驗、建立 PoC 或估計成功率。
- 三項 low observations先維持 backlog：coordinator handle、不必要的 receipt 轉抄、worker local attempt 記錄位置。本輪可研究其契約意義，但不一起改，避免無法歸因。

## Materials

現有材料均唯讀：

- [Task Harness Skill](../../skills/task-harness/SKILL.md)、[spec](../specs/task-harness.spec.md)、[runner](../../skills/task-harness/scripts/run_check.py)。
- [本輪 findings](../research/task-harness-revalidation2-20261003-evidence/findings.json)、[逐案例結果](../research/task-harness-revalidation2-20261003-evidence/case-results.json)、[結果報告](../research/task-harness-revalidation2-20261003.research.md)。
- [5.6 parallel trace](../research/task-harness-revalidation2-20261003-evidence/native-traces/reval2_56_parallel.json)、[6.1 parallel trace](../research/task-harness-revalidation2-20261003-evidence/native-traces/reval2_61_parallel.json)：失敗／成功對照。source_line 是原始 native JSONL 行號。
- [既有測試契約](../research/task-harness-revalidation2-20261003-evidence/test-contract.json)、[原始輸入 preimages](../research/task-harness-revalidation2-20261003-evidence/sol61/original-inputs.json)、兩模型 baseline/protected manifest。
- 既有 [export_traces.py](../research/task-harness-revalidation2-20261003-evidence/export_traces.py)、[check_receipts.py](../research/task-harness-revalidation2-20261003-evidence/check_receipts.py) 可作唯讀參考；後者帶寫檔行為，後續需要時複製到新 evidence root 並調整輸入，不能直接覆寫歷史輸出。
- [結案稽核](../research/task-harness-revalidation2-20261003-evidence/completion-audit.json)、[稽核器誤判紀錄](../research/task-harness-revalidation2-20261003-evidence/audit-checker-errors.json)。不執行既有一次性 closeout script 來啟動新研究。

本次規劃核對的 frozen runtime：

| 檔案 | SHA-256 |
| --- | --- |
| SKILL.md | `99114ea67a51c28339a595ed846b3942a5b7d3125327592e7d4f4f57fdbdaf0d` |
| agents/openai.yaml | `76b6ed3aab887a5dcc9870d04d5596d176cd512c7c6bc432511a29fc24271310` |
| scripts/run_check.py | `f25835aac47953927da5e13c711eebad3ffaca8426a2cc548b57dbacb4d7b988` |

後續執行前重新核對；若版本已變，不把舊結果直接套到新版本，先記錄差異與影響。

## Boundaries / Assumptions

- 原始規劃階段只新增本計畫；執行階段另建限定research/evidence與隔離fixtures。正式 Skill、spec、runner、舊 plans/results/evidence、README 與無關未提交工作保持原狀。
- 後續研究與 PoC 只寫新的隔離 workspace／evidence；不安裝套件、不連真實外部服務、不送通知、不 commit/push、不新增持久 goal 或排程。
- 保留兩模型 gpt-6.1-sol、gpt-5.6-sol。執行時記錄實際 model context、工具版本／可用能力、reasoning 設定與限制；不可用則標 unverified，不悄悄替換模型。
- Python standard library、既有 runner／原生 trace 足夠做小型驗證；不預設需要 workflow framework、資料庫、event sourcing 或新的 runtime script。
- 研究假設是「主問題位於交接契約、指令呈現或遵循行為」，尚未證明原因。單一過／不過案例無法證明模型普遍能力或穩定改善。
- 故障注入僅在 PoC copy 的 fake checkpoint/product marker 使用。測 write failure 與 reload state；不測真實遠端 side effect，也不把它擴大成完整 crash／斷電／多 writer 保證。
- 任務數上限是本計畫建議的實驗設計，不是使用者設定的 token／費用／時間預算；後續記錄實際用量。

## 初步來源與研究問題

初步查證日期：2026-10-03；以下只提供實驗設計依據，不證明本地根因。

| 一手來源 | 可採用的依據 | 本地推論及限制 |
| --- | --- | --- |
| [OpenAI Evaluation best practices](https://developers.openai.com/api/docs/guides/evaluation-best-practices) | 模型輸出有變異；先定義 objective、dataset、metrics，再比較；自動評分應與人工判讀校準。 | 預先固定採樣與判準、先校準 evaluator。此文件沒有規定本專案必須兩次寫 tracker；不需導入其雲端評估平台。 |
| [Python os.replace](https://docs.python.org/3/library/os.html#os.replace) | 成功 rename 為原子操作；跨 filesystem 可能失敗。 | 只對該 primitive 的語意成立；不能據此認定 apply_patch、整個 handoff、或斷電持久化具原子性。若研究替代單次 commit，須驗證實際 primitive 與邊界。 |

R1 的官方來源範圍限於能回答下表的 host/tool 文件、檔案寫入 primitive、agent eval 設計；缺來源或取不到實作就記 unknown，不展開一般多 agent 文獻巡覽。每個來源記錄 URL、查證日期、支持的具體命題與不支持的推論。

| 假設 | 目前證據 | 研究／PoC 如何判定 |
| --- | --- | --- |
| H1：規則分散或重複，使模型把邏輯接受與 persisted handoff 合併 | Skill Start、Accept、Persist 多處提及，但本次仍合併；不能由此推出唯一原因。 | 只改規則位置／表達，維持同一契約，與原版作固定 paired comparison。 |
| H2：兩次獨立保存是必要安全條件，或只是本專案的稽核形式 | 現行契約確實要求；實際產品寫入仍晚於成功 patch，尚無資料損壞證據。 | 列出需保存的可恢復狀態及發生錯誤時的處置；比較「契約遵循」與「產品動作前狀態有效」兩種判準。任何替代只能列提案，不能用它改判歷史 pass。 |
| H3：一次成功 patch 被誤當成具有 transaction／durability 保證 | 原生工具顯示成功，不足以證明 crash-safe persistence。 | 查 host/tool 實作或契約；只在 fake adapter 測已知語意。unknown 不假定成立。 |
| H4：evaluator 的比較／歸屬錯誤使測試反覆返工 | 已發生 identity projection 誤判並修正。 | 以正例、反例與 missing evidence 校準，再評模型；不能用待測模型自己的宣稱作 ground truth。 |

**R1 必須先回答：兩段保存具體保護哪個失敗情境？** 若無法支持其必要性，提出「保留契約」與「改為等價狀態轉移契約」的 trade-off；不自行放寬既有驗收。

## 方案比較與預設路線

| 路線 | 內容 | 代價與採用條件 |
| --- | --- | --- |
| A：同契約的最小指令調整（預設 PoC） | 將分散的 handoff 指令收斂成一段清楚的順序，明確成功回覆先於下一步；減少重複，不更動功能或 gate。 | 成本最低，但仍由模型遵循；需要固定對照與保留測試支持，不能靠一次 pass。 |
| B：改成可證明等價的單次狀態提交 | 驗收接受＋狀態 transition 在同一可驗證 commit 後，才允許產品動作。 | 必須研究實際原子性、source freshness、恢復語意及 authority。這是契約變更；列出具體證據及可 review 的差異後另作決策，不納入本輪模型競賽。 |
| C：由 deterministic helper 強制 transition | 程式拒絕缺 receipt、stale fingerprint 或不合法 state transition。 | 增加 runtime 與維護／測試責任；一般 helper 若可被直接檔案寫入繞過，並非真正強制執行。只有 A 不足且 host 有可落實 enforcement 的證據，才另提 PoC。 |

本輪預設只有 baseline B0 與一個 A 路線候選 B1。沒有足夠 R1/R2 證據時可以得出「不進模型 PoC／不採用修改」，這是研究決策完成，並非問題修復完成。

## 任務清單與依賴

Authority：本檔。Current coordinator：/root。下表 owner 是後續責任角色，並非已派出的 worker handle；未啟動的 task/check attempt 一律 not started。

| ID | Outcome | 依賴 | Owner／寫入範圍 | 狀態 |
| --- | --- | --- | --- | --- |
| P0 | 規劃、固定範圍與檢查材料 | none | /root；本計畫 | done |
| R1 | 根因假設與契約研究判讀 | P0＋後續執行授權 | /root；新 research 報告 | done |
| R2 | 可區分真／假失敗的離線 PoC | R1 | /root/handoff_poc_oracle；新 evidence root、temp fixture | done |
| R3 | baseline／候選的固定雙模型對照 | R2 pass＋預先凍結矩陣 | /root＋8個預登記actors；各自隔離 fixture | done |
| R4 | 選擇／拒絕候選的證據決策 | R3 終態，或 R1/R2 有明確 No-Go | /root；同份 research 報告 | done |
| R5 | 正式修訂與限定回歸確認 | R4 Go＋正式修改授權 | not applicable；R4非Go，無正式修改 | not triggered |

順序：R1 → R2 → R3 → R4 →（Go 才進）R5。不可同時改候選與收集其結果。角色之間可分工查來源與整理 trace，但驗收器凍結、實驗、決策按依賴串行；單一 coordinator 寫本 tracker。

產物位置（現已建立，實際temp root见matrix.json）：

- 研究／決策報告：`docs/research/task-harness-handoff-research-poc-20261003.research.md`。
- 測試資料與輸出：`docs/research/task-harness-handoff-research-poc-20261003-evidence/`。
- 執行副本：新建 `/private/tmp/task-harness-handoff-poc-*`；執行前記錄實際路徑與 frozen hashes。不得覆寫既有 revalidation fixtures。
- R2 預計只有一個 stdlib PoC/checker script 與一份 fixture/expected-results 資料；其餘 JSON 是實驗輸出，不新增 runner/framework。檔名及命令在寫出可執行檔後記入新報告；不可將本計畫的擬定命令說成已執行。

### R1：先界定根因與契約

預計 S：只寫一份研究報告。讀回 current runtime、spec 與兩份 native traces，建立「accept evidence→persist done→persist start→first product action」的實際事件表。對每項 unknown 說明缺少何種直接證據；不猜測模型內部推理、速度或 scheduler。

驗收：

1. H1–H4 各有 supported／contradicted／unknown、依據及下一個可區辨測試。
2. 列出兩段保存欲防止的具體錯誤，與 current trace 實際後果分開。
3. 決定 R2 oracle：現行嚴格契約繼續生效；狀態安全判準只作補充觀察。不能以補充觀察通過覆蓋 strict failure。

Verification：來源逐命題核對，事件綁 actual call/result／source_line；由 coordinator 按現行條文手工判讀一次。R1 若要改契約，先提出具體差異與理由；在決策前不把 B 路線算成修復。

### R2：先校準 evaluator，再跑模型

預計 M：一個小型 script、一份 fixtures/expected-results，加研究報告結果。只用歷史 trace 副本、明確標記的 synthetic mutation 與 fake local writer。產品操作替換為本機 marker；禁止執行歷史 argv，以免 replay side effect。

固定離線案例：

| ID | 輸入情境 | 預期判定／證據 |
| --- | --- | --- |
| O1 | 真實6.1成功 trace；同一 exec 內兩個 sequential awaited write，均有個別成功事件 | strict pass；不能因只有一個外層 exec 誤判同一 patch。 |
| O2 | 真實5.6 source105：一個 patch 同時 done／running，後續才產品動作 | strict fail；產品提前動作否；原子性 unknown。 |
| O3 | 缺少／失敗的 prerequisite receipt，仍嘗試 start | fail，fake product marker 不得產生。 |
| O4 | receipt 後來源 fingerprint 改變 | fail，不能沿用舊接受版本；不產生 marker。 |
| O5 | prerequisite done 寫入明確失敗 | 正確分支應保留可恢復狀態、不 start／不產生 marker；若仍 start 則 fail。 |
| O6 | prerequisite 已 done、successor start 寫入失敗 | 正確分支不得產品動作；reload 後依實際狀態 reconcile，禁止聲稱 successor 已執行。 |
| O7 | 缺 call result、缺必要 native observation | unverified／evidence invalid，不判 pass，也不算模型 protocol fail。 |
| O8 | native metadata 多出欄位、export 僅保留欄位 | 精簡欄位＋raw-line hash 一致時可接受；改任一保留欄位或 raw hash 必須拒絕。 |

O3–O8 為 offline synthetic/injected 資料，不能列為模型實測。fake writer只注入預定寫入結果並記錄事件；evaluator被動判讀，不替待測流程阻止不合法動作。每個故障案例同時保留正確停止分支與違規繼續分支：前者依其真實state/marker判定，後者必須被拒絕。reference flow通過只代表oracle已校準，不代表Skill已修復；R3也不使用helper替agent強制交接。O5/O6 測明確 write failure 與 reload，不宣稱覆蓋任意程序 crash 或硬體斷電。判讀實際 effect 與 state；不靠「PASS」文字、heading 或最終表格外觀。

若 R1 認為 B 路線值得比較，可在同一小型 state table 加註其預期，但不先實作另一套 runtime。`apply_patch success` 不自行升格為 `atomic commit success`。

驗收：O1–O8 預期分類及 marker/state 結果全部相符；實際讀寫路徑被限制在新 temp scope；不存在 ambiguous case 被當 pass。獨立於模型 verdict，以原始事件和實際檔案狀態作 oracle。

停止：最多一次有已知原因的 evaluator 修補，重新檢查受影響 O cases；仍有歧義即 No-Go，交付未解釋處，不先跑昂貴模型。checker 若在 R3 後改變語意，原模型資料可離線重判，須保留舊 verdict 和新版本；不得挑結果或重播模型求綠。

### R3：固定小樣本對照 PoC

預計 M：只在新 evidence/fixture 內工作；正式 Skill 不變。B0 為上述 frozen runtime；B1 只做 A 路線的 handoff 指令調整。先完成 diff、validator 及兩份 runtime manifests，之後凍結直到全部樣本結束。

**固定模型矩陣：2模型 × 2版本 × 2次事先登記的獨立樣本＝8個 coordinator runs；每 run 恰兩名 native workers，共16 workers。** 兩次是預先設計的採樣，不是第一次失敗才重跑；保留全部結果。這個小樣本只用於篩選明顯退步／改善線索，不提供高可靠度成功率保證。

控制方式：

- 每次 fresh context、相同 minimal raw inputs／中性產品要求／tool permissions、獨立 writable scope；不給預期答案、finding 或前次 verdict。
- B0/B1 除已凍結的指令 diff 外，其餘 fixture/checker/runner 相同；兩模型各內部使用相同可用 reasoning 設定，完整記錄而不推測預設值。
- 每模型順序 B0、B1、B1、B0，減少執行順序偏差；不同模型可在獨立 scope 執行。不得插入 sleep／barrier 製造 worker overlap。
- 初始 fixture、prompt、expected gate、holdout 與所有 run IDs 在第一個 run 前寫入 manifest；failed dispatch 或缺 native evidence 列 invalid，不能換一筆較好結果。
- 模型不可用或 host interruption：完成其他獨立可做的部分，保留 unverified；本矩陣不自動補樣。後續補測須明確標成另一次實驗，不以舊名覆寫。
- 同一組樣本全部終態後才比較。若出現越界寫入、錯誤接受或未知副作用，立即停止受影響實驗，不為湊齊樣本繼續危險動作。

固定 gates：

1. **Handoff**：各 prerequisite 自己的有效 receipt/fingerprint 經驗收；done-write success 早於 successor start-write；start-write success 早於 first product action。
2. **State/evidence**：real handle、numeric task/check attempts 可追溯；保存失敗不得被當成功；不用 integration receipt 補作 prerequisite 接受。
3. **Dispatch/scope**：逐一 dispatch/checkpoint，群組派完前無主動 wait/accept/無關工作；sole tracker writer、disjoint product/evidence ownership、恰兩 workers。
4. **Outcome/safety**：整合 check.py 通過；protected inputs 不變；沒有未授權副作用、無界 retry、evidence 偽造。

Overlap、dispatch delay、token／時間僅觀察，不新增隱含門檻。三項已知 low observations照記，不在比較中變成新 blocker。

驗收／比較：逐 run 同時列 strict gate、核心 outcome、evidence validity與資源用量。B1必須4/4 valid且固定 gates全過；B0若有同一主要流程失敗且沒有其他混雜因素，才可描述「本批支持 B1 改善」。B0/B1均全過則是無法區辨，不能宣稱根因已修；B1出現任何 fixed-gate fail，或缺必要 evidence，均不得進正式採用。

### R4：一次決策，不啟動無限候選循環

預計 S：同一 research 報告加一份 decision table。不新增第二 tracker／reviewer 階層。

| 結果 | 決策 |
| --- | --- |
| R1顯示原契約需要修訂，或 R2 oracle 尚不清楚 | No-Go：交付契約選項及最小缺證；不先加 prompt／helper。 |
| B1符合全部固定 gates，B0重現主要失敗，且沒有混雜因素 | Go to confirmation：只建議採用已凍結 B1，再進 R5 保留案例確認。 |
| B0/B1都通過，或差異不能歸因 | Inconclusive：保留現行版本與 finding；不擴樣直到觀察到想要的結果。 |
| B1失敗／回歸 | No-Go：保留失敗，提出一個有證據的後續方向與代價；不自動產生 B2。 |

研究＋PoC 階段可用 Go／No-Go／Inconclusive 結案；只有 Go 且 R5 通過，才可主張限定範圍修復完成。不得把實驗完成當成修復完成。

### R5：採用一次、確認一次

只在正式修改已授權且 R4 Go 後執行。預計 S–M：修改核准的 Skill 指令；spec 僅在契約確有變更且已決定採用時同步。A路線預設不改 runner／metadata、不新增 runtime檔。

第一個 PoC run 前凍結一個未提供給實驗 agents 的 parallel holdout（仍是兩個獨立產物後整合，但換 task IDs、金額資料與姓名邊界），保留其 inputs／expected checks。採用後兩模型各跑此 holdout 一次；因 Start/Persist 指令可能影響 resume，另各跑既有 resume 一次，共4個確認 coordinator runs，parallel再有4 workers。

Verification：新正式 runtime 與選定 B1 bytes/hash一致（路徑差異不改內容），官方 Skill validator通過；固定 parallel gates及resume的stale acceptance、unknown send不重播、缺工具 blocked、bounded retry、unknown歷史／local attempt分離通過。runner沒變則沿用同hash自測證據；若實際改動超出原影響範圍，先重做 impact map，不能靜默增加全八案例。

成功後做一次 evidence／scope／completion audit；新 low findings進 backlog。任一固定 gate失敗或unverified即交付失敗並停止，不再自動修候選／重跑；正式檔案可在核對無他人後續變更後還原本輪 diff，隔離 evidence保留。不宣稱修復成功。

## 固定結束條件

- 本次規劃 DoD：範圍／材料／假設／研究問題／方案trade-off／PoC fixtures／模型矩陣／owner與依賴／各階段驗收／停止及rollback齊全；existing links有效；正式runtime與歷史evidence未改。
- 下一次研究／PoC DoD：R1、R2有可追溯結論；若允許R3，固定8runs皆有結果或明確invalid/unverified；R4給出Go／No-Go／Inconclusive及理由。PoC不合格仍可完成研究交付。
- 後續修復 DoD：R4 Go、同一候選被採用、4個預登記確認案例達到固定gates；沒有data loss、incorrect acceptance、未授權side effect、無界retry或evidence錯誤歸屬。
- 1個候選、1輪預登記對照、1輪確認；不因一般新finding擴DoD，不在本計畫自動啟動另一輪候選。預設最大12個coordinator runs、20 workers；若前段No-Go，後段不執行。
- 新高風險 finding 只有直接打破固定correctness／safety／evidence gate才阻止採用，需指出確切 gate及證據；其他問題只記 backlog。

## 風險與處理

| 風險 | 處理 |
| --- | --- |
| 根因不是缺規則，繼續加字沒有改善 | 先研究H1/H2，B1只改一個因素，保留對照；不承諾PoC一定選出修法。 |
| 小樣本偶然全過 | 預登記兩次樣本、保留不同輸入holdout；結論限定於本批，不宣稱普遍穩定。 |
| evaluator再次誤判 | 先用O1–O8校準；缺證判unverified，projection與batch/child exits各自核對。 |
| 為通過放寬契約 | strict與補充安全判準分欄；B路線需獨立決策，歷史結果保留。 |
| helper膨脹、需要驗證新的驗證系統 | 預設只做一個離線PoC；不新增runtime，C路線不是自動fallback。 |

## 原始規劃交付 checkpoint（歷史）

P0已完成。R1–R5均未啟動，無新worker、無PoC結果、無正式修正。下一個可執行步驟為R1：契約與根因研究，接續R2離線校準，再依固定判準決定是否進R3。

## 執行授權與 checkpoint（2026-10-03）

使用者已授權按開發流程執行至完成，涵蓋R1–R4及符合Go條件後的R5正式修訂／確認；無需再詢問同一範圍授權。上方「本次只規劃」為規劃交付時的歷史邊界。固定研究矩陣、不得求綠重跑及No-Go停止條件仍有效。R1 attempt1，owner /root，研究報告／新evidence root已確認；既有檔案SHA基線已保存。

R1 attempt1已完成：[研究報告](../research/task-harness-handoff-research-poc-20261003.research.md)，保留strict contract，A路線候選。R2 task attempt1，owner /root/handoff_poc_oracle，handle同名；寫入範圍限新evidence中的offline_poc.py、offline-fixtures.json、offline-result.json與離線過程證據。

R2 accepted：offline-result.json共21/21分支相符，原始events、marker、state與receipt已核對；O7分類用去一次允許修補，未新增case或改expected。正式runtime未改。

R3 task attempt1，owner /root；B0/B1與矩陣已凍結。dispatch前R2已done且結果有效。各actor dispatch記錄另見新evidence/actors.json（觀察紀錄，任務authority仍為本檔）。

R3 accepted as completed assessment：8/8 runs終態、24 actors/502 tool events、31 attributable receipts、8 integration checks通過；1筆樣本有context contamination，完整保留為confounded，不作乾淨對照。Handoff native時序8筆均兩段成功寫入。正式Skill未改。

R4 task attempt1，owner /root；R3結果與原生refs已成功保存，按固定decision table判讀，不再新增候選或樣本。

## 最終 checkpoint

R1–R4完成，R4為Inconclusive；[最終研究報告](../research/task-harness-handoff-research-poc-20261003.research.md)、新evidence中的decision.json與case-results.json為本輪結果。R5因採用條件未成立而不觸發，未採用B1，未跑holdout，沒有下一候選或補樣。8 coordinators與16 workers全數terminal；正式runtime三檔保持B0 hashes，既有finding未關閉。本計畫研究交付完成，不宣稱修復完成。
