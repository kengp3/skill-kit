# 統一設定改版：實際 agent 與整合驗收

日期：2026-10-25。受測產品為 Kengp3 Harness 0.3.0，產品來源整合至 `4b8ff38`，補充驗收整合至 `6974467`（產品內容未變）。本輪 A–G 七組及後述具名負向／生命週期分支均取得真實 agent 與產物證據；下面逐項說明實際覆蓋範圍，未執行的細分路徑與宿主能力仍保留為未驗證，不宣稱任意任務或所有宿主皆已通過。

依據：[實作規格](../specs/unified-project-settings.spec.md)、[ADR](../adr/0001-unified-project-settings.adr.md)、[用語](../specs/task-harness-glossary.spec.md)。來源問題與修正的獨立 Standards／Spec 審查見[審查報告](unified-project-settings-review.research.md)。

## 候選與來源追溯

最終候選 manifest SHA-256 為 `7e37d77315faee550e3f2e1edc4b3a621da490f50ce4a8d937c78f9d71fbfd9e`。在全新隔離 state 原生安裝及從 0.2.1 升級後，均由新 app-server 讀回四個 skills、三個 hooks；實際安裝檔案逐一符合 manifest，copied-skill 的 canonical hooks asset 與 plugin hooks 完全相同，舊 Python handler 未發行。

- [最終全新安裝／載入](unified-project-settings-acceptance-evidence/final-loader/summary.json)、[原始 RPC](unified-project-settings-acceptance-evidence/final-loader/rpc.json)。
- [最終 0.2.1→0.3.0 升級／載入](unified-project-settings-acceptance-evidence/final-upgrade/summary.json)、[原始升級回應](unified-project-settings-acceptance-evidence/final-upgrade/upgrade.json)、[原始 RPC](unified-project-settings-acceptance-evidence/final-upgrade/rpc.json)。
- [候選差異對照](unified-project-settings-acceptance-evidence/source-comparison.json)保存三個開發中候選的檔案指紋。早期 `2fbb0e…` 到修正 `7e8806…` 增加 canonical asset、provider 接線及 metadata／選配 helper 說明；`7e8806…` 到最終 `7e37d7…` 只改 provider 的 matcher 等效範圍說明。三者的實際 hook 定義位元組相同。

早期案例不改寫來源指紋冒充最終候選。來源型 standalone A 與 G 的對應來源沒有差異；B／C／E／F 的階段快照差異明列於[階段案例摘要](unified-project-settings-acceptance-evidence/staged-summary.json)。它們只支持受測行為，並由後續已安裝候選的小任務、copied-skill 接線、回退與恢復案例補驗。最終 matcher 限定群組的「保留並回報部分涵蓋」另由最終候選的真實唯讀 agent 案例驗證；正常無 matcher 的接線案例不受此一文件差異影響。

## A–G：預期 → 實際觀察 → 證據

| 組別 | 實際觀察與判定 | 直接證據 |
| --- | --- | --- |
| A：project-setting 單獨使用 | **受測路徑通過。** 只安裝 project-setting，原生模型建立五類文件規範並讀回；沒有 Task Harness 區段或專用分類，preserve.txt 未變。 | [執行與來源](unified-project-settings-acceptance-evidence/staged/A-standalone/run.json)、[原始回合](unified-project-settings-acceptance-evidence/staged/A-standalone/stdout.jsonl)、[實際設定](unified-project-settings-acceptance-evidence/staged/A-standalone/artifacts/project-setting.md) |
| B：包含 harness、初始化與有效性 | **初始化、格式修復及受測負例通過。** 原生小任務透過規格建立單一設定、兩個路徑分類與唯一合約，精確產出 BASIC_TASK_OK。另一個已安裝 0.3.0 案例在唯讀限制下辨識重複分類、互斥路徑、重複版本鍵及不支援版本 9，未選其中一值或改動任一檔案。最終候選另修復缺少的 schema_version，保留既有分類列順序／空白、自訂區塊與模型預設；受限 matcher 案例只回報部分覆蓋，不重複或擴大 handler 範圍。 | [小任務原始回合](unified-project-settings-acceptance-evidence/staged/BD-nohelpers/stdout.jsonl)、[唯一合約](unified-project-settings-acceptance-evidence/staged/BD-nohelpers/artifacts/docs/plans/basic-result.task-contract.md)、[唯讀負例前後指紋](unified-project-settings-acceptance-evidence/readonly-invalid/summary.json)、[負例原始回合](unified-project-settings-acceptance-evidence/readonly-invalid/model.stdout.jsonl)、[格式與 matcher 補充](unified-project-settings-settings-faults.research.md) |
| C：移轉、衝突與恢復 | **成功、衝突、I/O 失敗保留及部分完成狀態恢復通過。** 成功案例逐項對帳並在三門檻成立後刪舊檔；衝突案例保留新舊檔。最終候選的恢復 fixture 已有新 Markdown、舊 JSON 尚在，agent 只補核對並刪舊檔，Markdown 位元組未改、未新增重複分類，歷史合約及 JSONL 收據未改。另有真正 OS EPERM 寫入／刪除拒絕及 EACCES 讀回拒絕：agent 保留原檔、歷史產物，未變更保護屬性、未假稱移轉完成。恢復 fixture 是預置狀態，不宣稱實際 OS 中斷移轉。 | [成功前態](unified-project-settings-acceptance-evidence/staged/C-migration/fixture-before.json)、[成功移轉對帳](unified-project-settings-acceptance-evidence/staged/C-migration/artifacts/docs/research/task-harness-settings-migration.research.md)、[衝突原始回合](unified-project-settings-acceptance-evidence/staged/C-conflict/stdout.jsonl)、[最終候選恢復指紋](unified-project-settings-acceptance-evidence/migration-resume/summary.json)、[恢復後合約](unified-project-settings-acceptance-evidence/migration-resume/artifacts/docs/plans/harness/settings-migration.task-contract.md)、[三種真實 I/O 失敗](unified-project-settings-settings-faults.research.md) |
| D：選配腳本／工具不成必要依賴 | **受測核心與封裝路徑通過。** B 的技能 scripts 目錄實際移除，七個完成的命令沒有執行 Python／Node／run_check，仍完成成果與合約驗收。封裝公開測試在空 PATH 執行真正發行的三種 handler，沒有外部 runtime。純複製安裝也省略 scripts，依自帶資源完成設定與接線。這不是宣稱測試機所有 interpreter 都已移除。 | [B 的來源／移除後清單](unified-project-settings-acceptance-evidence/staged/BD-nohelpers/run.json)、[B 原始回合](unified-project-settings-acceptance-evidence/staged/BD-nohelpers/stdout.jsonl)、[copied-skill 執行](unified-project-settings-acceptance-evidence/standalone-copy/model.stdout.jsonl)、[完整維護測試](unified-project-settings-review-evidence/fixed-tests.log) |
| E：hooks 不可用、恢復與去重 | **受測接手、兩回合恢復及原生 Stop 邊界通過。** 無 hooks 的案例先核對未知 append，保留 ledger 的一次寫入、清除 unknown 並完成剩餘成果。另一個 owned fixture 以兩個已知 exit 17 定義開始；agent 依授權修復，保留無關 sentinel，完成 T1 後保存 wait、沒有提前執行 T2。控制器核對新定義為 allowlist/canonical 後，第二個明確續作回合收到兩個實際 developer 提醒，沿用同 task ID／一份合約，ledger 仍一次，完成 T2。原生 Stop 補充在工具已開始後中斷，T2 未執行；先確認舊程序退出，才由明確新授權接續同一合約，ledger 仍一次。CLI 未另提供每個初始壞 handler 的 exit event，不能把定義與缺少提醒擴稱完整逐 handler 遙測。 | [未知結果恢復原始回合](unified-project-settings-acceptance-evidence/staged/E-resume/stdout.jsonl)、[第一階段合約](unified-project-settings-acceptance-evidence/hook-recovery/artifacts-phase1/docs/plans/hook-recovery.task-contract.md)、[第二階段原始回合](unified-project-settings-acceptance-evidence/hook-recovery/model-phase2.stdout.jsonl)、[實際注入紀錄](unified-project-settings-acceptance-evidence/hook-recovery/hook-session-records.json)、[兩階段摘要](unified-project-settings-acceptance-evidence/hook-recovery/summary.json)、[原生 Stop 與續作](unified-project-settings-native-stop.research.md) |
| F：模型規則、真實派工與回退 | **受測政策、派工、回退及原生生命週期通過。** 實際 agent 判讀 11 組優先序／清單／default／去重／限制／新任務資料，明示它們是政策輸入，不冒充 provider 事件。正常派工由角色選到 gpt-6-sol，宿主 turn_context 記錄主責 gpt-6.1-sol、子 agent gpt-6-sol。實際不可用首選回傳 HTTP400 model_not_found；先查 handle 由 running 轉 errored，才派第二候選並取得 completed。另由本次原生 model/list 判定 gpt-6-sol 不支援 none、預設 medium，保留模型並成功派出 medium worker，長期設定未變。最終候選另以實際多回合證明覆寫留在同任務、新任務用專案預設；原生 API 切換主責後，舊 worker 保留原模型／強度、新 worker 繼承新選擇；首選與專案預設都真實失敗且各只嘗試一次，T1 blocked、無關 T2 完成。 | [11 案政策判讀](unified-project-settings-acceptance-evidence/model-policy/artifacts/docs/research/model-policy.research.md)、[正常獨立派工](unified-project-settings-acceptance-evidence/staged/F-independent/artifacts/docs/research/model-review.research.md)、[正常派工宿主上下文](unified-project-settings-acceptance-evidence/staged/F-independent/session-model-contexts.json)、[真實 model_not_found 與回退](unified-project-settings-acceptance-evidence/fallback-dispatch/model.stdout.jsonl)、[回退結果](unified-project-settings-acceptance-evidence/fallback-dispatch/artifacts/docs/research/fallback.research.md)、[本次模型 metadata RPC](unified-project-settings-acceptance-evidence/effort-preflight/metadata-rpc.json)、[medium worker 上下文](unified-project-settings-acceptance-evidence/effort-preflight/session-contexts.json)、[三組原生模型生命週期](unified-project-settings-model-lifecycle.research.md) |
| G：無子 agent、獨立審查缺口 | **受測限制通過。** 原生 state 設定 agents.enabled=false，模型看到沒有建立工具；未解除限制、未安裝外部派工器。唯一合約的獨立審查 T1 保留 blocked，主責完成無相依 T2，整體保持 blocked，精確產出 MAIN_WORK_DONE。 | [限制及執行來源](unified-project-settings-acceptance-evidence/staged/G-disabled/run.json)、[原始回合](unified-project-settings-acceptance-evidence/staged/G-disabled/stdout.jsonl)、[合約](unified-project-settings-acceptance-evidence/staged/G-disabled/artifacts/docs/plans/no-agent.task-contract.md) |

## 已安裝候選與 copied-skill 的實際接線

- 已安裝候選的小任務取得精確 PACKAGED_OK 與一份 done 合約；[session 紀錄](unified-project-settings-acceptance-evidence/packaged-hooks/hook-session-records.json)包含兩個真實 developer message，內容分別等於發行 SessionStart／UserPromptSubmit 提醒。這是實際模型上下文注入，不只是 hooks/list 列舉。
- [純複製案例](unified-project-settings-acceptance-evidence/standalone-copy/summary.json)沒有 plugin 安裝，只有已複製的四個 skills 且 scripts 被省略；模型透過 generic project-setting 讀取 harness 自帶 asset，寫入 project-setting.md、專案 hooks/config。每個 canonical handler 恰有一份，preserve.txt 未變，沒有依賴來源 repo 的 packaging 目錄。
- native 執行使用單次 `--dangerously-bypass-hook-trust`。此為測試控制器對已核對的固定命令使用的隔離 automation 選項；兩回合案例在第二階段前再次比對所有新命令與 canonical／PS 資源及未改 sentinel。它不是正常持久信任驗收，也不應成為日常安裝的建議捷徑。
- Stop 發行命令為固定 `{}` 被動回應。公開封裝測試直接回放含重複 Stop；真實任務正常結束，但 CLI 沒有獨立的每次 Stop handler 執行通知。本輪不宣稱條件式阻擋、一次性補救、原子收據或抵抗使用者停止。

## 最終候選的三組補充驗收

- [設定／I/O 補充](unified-project-settings-settings-faults.research.md)：五個具名案例，59 項獨立核對通過。格式修復保留列順序與空白；受限 matcher 只診斷不改動；真正寫入、讀回、刪除拒絕時保留新舊狀態。初次三個遭 sandbox 啟動限制的試跑保留為受阻，未冒充目標 I/O 分支通過。
- [模型生命週期補充](unified-project-settings-model-lifecycle.research.md)：三組實際原生多回合案例，60 項獨立核對通過。任務覆寫／恢復／新任務、主責 API 選擇變更後的舊新 worker，以及候選連同專案預設耗盡均有實際 handle、事件、session context 及成果。
- [原生 Stop 補充](unified-project-settings-native-stop.research.md)：真實 `item/started` 與 OS PID 已觀測才發送一次 `turn/interrupt`，取得 `interrupted`。Stop 後沒有 T2 或新工具事件；舊 shell／sleep 曾短暫存活，因此等其退出並回收原 app-server，約 19.9 秒後才送明確續作授權。新 thread 接續同一合約，ledger 一次、T2 完成。[事後核對](unified-project-settings-native-stop-evidence/verification.json)保存 raw 行號、時間及 SHA-256。這是實際中斷與查明後續作，沒有即時終止任意 shell 或原子回滾保證。

## H1–H8 宿主能力判定

| 能力 | 已觀測 | 明確限制／未驗證 |
| --- | --- | --- |
| H1：接入、載入、信任、觸發 | 最終新安裝及升級 loader／manifest；固定提醒實際進入 developer context；受限 matcher 真實診斷保持原範圍 | 正常持久 hook 信任未驗證；原生 loader 仍顯示 untrusted，執行案例有測試 bypass；matcher 案例不冒充 live hook 事件 |
| H2：上下文、阻擋、續作、Stop | 兩種提醒實際注入；wait 回合沒有提前做 T2；真正 native API 中斷命中已開始工具，查明退出後明確授權續作 | 本版沒有條件式阻擋或一次性續作保證；Desktop UI 停止按鈕未測；回合 interrupted 不保證已啟動 shell 同步退出 |
| H3：身分、回合、重複與恢復 | 真實 thread/turn 識別、跨回合同一合約、原生中斷後跨 thread 接手及一次寫入保持；不存在的身分保留 null | 未測相同 hook event 的完整 native re-entry、全部輸入來源辨識或多主責競爭；passive Stop 不生成新授權 |
| H4：模型、強度與角色優先序 | 正常角色派工、真實候選拒絕及安全改派；host turn_context 的模型／強度、medium 修正；任務覆寫跨回合／新任務原生派工 | 底層 provider 模型權重身分不可獨立觀測；報告不以模型自述填補 |
| H5：目前對話及手動切換 | 同一 native thread 的兩次 user-turn 模型／強度控制實際改變；原 worker 跨切換保留原 session／設定，新 worker 省略模型／強度後實際繼承最新選擇 | 本案是原生 API 控制，不是 Desktop 模型選單 UI 驗收；模型在對話內取不到的 observed 值仍標未知，外部 session context 另行核對 |
| H6：不可用／強度不支援／派工失敗 | 真實 model_not_found、含專案預設的兩候選耗盡與去重；model/list 強度支援／預設及實際 medium worker；歷史載入失敗未誤認模型不可用 | 未故意送出 provider 非法強度請求；strict 範圍以真實模型判讀測試輸入驗證，沒有違反限制的呼叫 |
| H7：未知啟動查核 | 真實 handle running→errored 後才回退；未知 append 先核對；原生 Stop 後實際程序仍存活時先查明而不重播；過期 trial 保留未知 | 未完成真正子 agent 啟動回應遺失、網路斷線後跨 session 查回 worker 終態全流程；Stop 工具案例不替代未知 child 啟動試驗 |
| H8：安裝／升級與來源一致 | 最終 7e37d7… 全新安裝及 0.2.1 升級均讀回完整來源與 exact manifest；三組補充亦逐一核對同 manifest | 沒有更動既有日常安裝／全域 cache；不宣稱所有宿主或 Windows 已測 |

## 未驗證細分路徑與風險

以下是仍保留的驗證限制，不是已確認產品缺陷，也不能標成通過。正常信任／Windows／Desktop UI 屬平台資格限制；真正未知 child 網路故障、native hook re-entry 與移轉命令中斷則是具名行為驗證缺口，不佯稱只是平台差異。上述具名 B／C／F 分支與 native API 模型切換已補驗，不再列作整組未驗證：

1. 正常持久 hook 信任、原生 Windows、Desktop 停止按鈕／模型選單 UI 及所有帳號的模型可用性未驗證。維護測試略過的 1 項是 native Windows，沒有用 POSIX replay 代替。
2. H7 真正 child 啟動回應遺失、網路斷線及跨 session 終態查回尚未實測。已知 handle 的終態查核與中斷後原工具退出查核有直接證據，但不外推為上述網路故障能力。
3. E 沒有故意重送相同宿主 hook event 的完整 native 事件重入試驗，也未測多主責競爭。真實恢復前後 ledger 一次、同一合約及無重複派工不構成跨程序原子去重或 exactly-once 保證。
4. C 的中斷恢復使用「新設定已寫、舊檔仍在」明示 fixture，加上兩次真實 invocation 之間施加讀回拒絕；未在移轉工具命令執行中強制終止 OS 程序。B 列順序／空白已有一個真實組合案例，未窮舉所有文字排列。
5. Stop 後 shell 曾短暫存活；控制器等其退出才允許接手。本次受控命令無產品副作用，不能宣稱任意 shell 在 Stop 後即時停止或回滾；純 Markdown 流程不提供 OS 程序鎖。這個限制已由真實觀測揭露，沒有把 native interrupted 當作工具完成或重試授權。

## 失敗、未知與開發端問題保留

- [早期 F](unified-project-settings-acceptance-evidence/staged/F-prelaunch-failure/stdout.jsonl)的 ephemeral 歷史載入失敗由真實 host 回報；未取得成功 handle，agent 保留獨立審查缺口。後續獨立新 fixture 使用 persistent session／自足輸入完成正常派工，未改寫原失敗紀錄。
- [T06 原抽樣](unified-project-settings-acceptance-evidence/staged/FG-timeout/run.json)到期前未取得回合終態，仍為未知，不算 G 通過或未執行證明。G 的判定另有真正 agents.enabled=false 案例。
- 設定 I/O 補充的三個初試遭 sandbox 啟動限制，另有初版 driver 前置條件不足；正式重跑只修正驗收提示／控制器。原始失敗仍留在補充報告，未混入正式五案例。
- [final-upgrade-launcher-failed](unified-project-settings-acceptance-evidence/final-upgrade-launcher-failed/launcher-note.json)是開發 probe 的 argparse 名稱被迴圈變數遮蔽，尚未啟動任何模型回合。保留當時原始 CLI 回應；修正後在另一個新隔離 state 完成最終升級。它不被歸為產品失敗或產品通過。

## 證據核對與隔離

[唯讀核對器](unified-project-settings-acceptance-evidence/check-evidence.py)以獨立的精確內容、before／after 指紋、既有 task ID、合約狀態、native error 與 session context 核對產物；[核對結果](unified-project-settings-acceptance-evidence/assertions.json)記錄 39 項通過。這是既有證據的查核，不是另一輪產品測試，也不是 runtime 依賴。完整原始檔案的實際 SHA-256 見[證據索引](unified-project-settings-acceptance-evidence/evidence-index.json)。三份補充證據各自保存 raw／產物及核對結果；本次彙整重跑原 39、模型 60 與設定 59 項共 158 項核對皆通過，Stop 另依 verification 的原始行號與檔案指紋讀回。這些是不同證據集的查核數，不是 158 個獨立產品情境。

所有新增模型案例使用獨立 state/project/catalog。登入檔僅在 owned 0700 暫存 state 內建立 0600 複本，結束時清除；封裝 loader 不需 auth。每輪保存正常 config.toml／auth.json 前後相同的判定，沒有將憑證複本歸檔。歸檔檢查亦逐檔比對實際憑證字串，沒有發現值被保存；只保留無憑證的 raw、產物與來源指紋。

上述保留證據直接涵蓋 config/auth 與操作使用的隔離 cache 路徑，不是整台機器／OS keychain 的全面差異稽核。部分 exec 在沙箱啟動前被拒，真實紀錄保留後由宿主批准的同一 scoped 操作完成；沒有為此安裝 runtime、改全域設定或操作其他專案。

原始產物保持逐位元組不變，因此 staged diff 的完整 whitespace 檢查保留三項原始產物警告：兩份舊設定檔尾端空行、一份舊審查檔的 hexdump 尾端空白。沒有為了消除警告改寫 raw；本輪撰寫的報告、票與開發 probes 另行檢查通過。

維護者完整測試為 112 項、略過 1 項，另有九個公開封裝案例與獨立兩軸審查；這些與真實 agent 行為證據分開判定，詳見[來源審查](unified-project-settings-review.research.md)與[封裝報告](unified-project-settings-package.research.md)。
