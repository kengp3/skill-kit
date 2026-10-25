# 統一設定改版：實際 agent 與整合驗收

日期：2026-10-25。受測產品為 Kengp3 Harness 0.3.0，來源整合至 `4b8ff38`。本輪 A–G 七組均取得真實 agent 與產物證據；下面逐項說明實際覆蓋範圍，未執行的細分路徑與宿主能力仍保留為未驗證，不宣稱任意任務或所有宿主皆已通過。

依據：[實作規格](../specs/unified-project-settings.spec.md)、[ADR](../adr/0001-unified-project-settings.adr.md)、[用語](../specs/task-harness-glossary.spec.md)。來源問題與修正的獨立 Standards／Spec 審查見[審查報告](unified-project-settings-review.research.md)。

## 候選與來源追溯

最終候選 manifest SHA-256 為 `7e37d77315faee550e3f2e1edc4b3a621da490f50ce4a8d937c78f9d71fbfd9e`。在全新隔離 state 原生安裝及從 0.2.1 升級後，均由新 app-server 讀回四個 skills、三個 hooks；實際安裝檔案逐一符合 manifest，copied-skill 的 canonical hooks asset 與 plugin hooks 完全相同，舊 Python handler 未發行。

- [最終全新安裝／載入](unified-project-settings-acceptance-evidence/final-loader/summary.json)、[原始 RPC](unified-project-settings-acceptance-evidence/final-loader/rpc.json)。
- [最終 0.2.1→0.3.0 升級／載入](unified-project-settings-acceptance-evidence/final-upgrade/summary.json)、[原始升級回應](unified-project-settings-acceptance-evidence/final-upgrade/upgrade.json)、[原始 RPC](unified-project-settings-acceptance-evidence/final-upgrade/rpc.json)。
- [候選差異對照](unified-project-settings-acceptance-evidence/source-comparison.json)保存三個開發中候選的檔案指紋。早期 `2fbb0e…` 到修正 `7e8806…` 增加 canonical asset、provider 接線及 metadata／選配 helper 說明；`7e8806…` 到最終 `7e37d7…` 只改 provider 的 matcher 等效範圍說明。三者的實際 hook 定義位元組相同。

早期案例不改寫來源指紋冒充最終候選。來源型 standalone A 與 G 的對應來源沒有差異；B／C／E／F 的階段快照差異明列於[階段案例摘要](unified-project-settings-acceptance-evidence/staged-summary.json)。它們只支持受測行為，並由後續已安裝候選的小任務、copied-skill 接線、回退與恢復案例補驗。最終 matcher 限定群組的「保留並回報部分涵蓋」已有來源審查，尚無本輪真實 agent fixture；正常無 matcher 的接線案例不受此一文件差異影響。

## A–G：預期 → 實際觀察 → 證據

| 組別 | 實際觀察與判定 | 直接證據 |
| --- | --- | --- |
| A：project-setting 單獨使用 | **受測路徑通過。** 只安裝 project-setting，原生模型建立五類文件規範並讀回；沒有 Task Harness 區段或專用分類，preserve.txt 未變。 | [執行與來源](unified-project-settings-acceptance-evidence/staged/A-standalone/run.json)、[原始回合](unified-project-settings-acceptance-evidence/staged/A-standalone/stdout.jsonl)、[實際設定](unified-project-settings-acceptance-evidence/staged/A-standalone/artifacts/project-setting.md) |
| B：包含 harness、初始化與有效性 | **初始化及受測負例通過。** 原生小任務透過規格建立單一設定、兩個路徑分類與唯一合約，精確產出 BASIC_TASK_OK。另一個已安裝 0.3.0 案例在唯讀限制下辨識重複分類、互斥路徑、重複版本鍵及不支援版本 9，未選其中一值或改動任一檔案。 | [小任務原始回合](unified-project-settings-acceptance-evidence/staged/BD-nohelpers/stdout.jsonl)、[唯一合約](unified-project-settings-acceptance-evidence/staged/BD-nohelpers/artifacts/docs/plans/basic-result.task-contract.md)、[唯讀負例前後指紋](unified-project-settings-acceptance-evidence/readonly-invalid/summary.json)、[負例原始回合](unified-project-settings-acceptance-evidence/readonly-invalid/model.stdout.jsonl) |
| C：移轉、衝突與恢復 | **成功、衝突、未有效讀回及部分完成狀態恢復通過。** 成功案例逐項對帳並在三門檻成立後刪舊檔；衝突案例保留新舊檔。最終候選的恢復 fixture 已有新 Markdown、舊 JSON 尚在，agent 只補核對並刪舊檔，Markdown 位元組未改、未新增重複分類，歷史合約及 JSONL 收據未改。此 fixture 是預置狀態，不宣稱實際 OS 中斷。 | [成功前態](unified-project-settings-acceptance-evidence/staged/C-migration/fixture-before.json)、[成功移轉對帳](unified-project-settings-acceptance-evidence/staged/C-migration/artifacts/docs/research/task-harness-settings-migration.research.md)、[衝突原始回合](unified-project-settings-acceptance-evidence/staged/C-conflict/stdout.jsonl)、[最終候選恢復指紋](unified-project-settings-acceptance-evidence/migration-resume/summary.json)、[恢復後合約](unified-project-settings-acceptance-evidence/migration-resume/artifacts/docs/plans/harness/settings-migration.task-contract.md) |
| D：選配腳本／工具不成必要依賴 | **受測核心與封裝路徑通過。** B 的技能 scripts 目錄實際移除，七個完成的命令沒有執行 Python／Node／run_check，仍完成成果與合約驗收。封裝公開測試在空 PATH 執行真正發行的三種 handler，沒有外部 runtime。純複製安裝也省略 scripts，依自帶資源完成設定與接線。這不是宣稱測試機所有 interpreter 都已移除。 | [B 的來源／移除後清單](unified-project-settings-acceptance-evidence/staged/BD-nohelpers/run.json)、[B 原始回合](unified-project-settings-acceptance-evidence/staged/BD-nohelpers/stdout.jsonl)、[copied-skill 執行](unified-project-settings-acceptance-evidence/standalone-copy/model.stdout.jsonl)、[完整維護測試](unified-project-settings-review-evidence/fixed-tests.log) |
| E：hooks 不可用、恢復與去重 | **受測接手與兩回合恢復通過。** 無 hooks 的案例先核對未知 append，保留 ledger 的一次寫入、清除 unknown 並完成剩餘成果。另一個 owned fixture 以兩個已知 exit 17 定義開始；agent 依授權修復，保留無關 sentinel，完成 T1 後保存 wait、沒有提前執行 T2。控制器核對新定義為 allowlist/canonical 後，第二個明確續作回合收到兩個實際 developer 提醒，沿用同 task ID／一份合約，ledger 仍一次，完成 T2。CLI 未另提供每個初始壞 handler 的 exit event，不能把定義與缺少提醒擴稱完整逐 handler 遙測。 | [未知結果恢復原始回合](unified-project-settings-acceptance-evidence/staged/E-resume/stdout.jsonl)、[第一階段合約](unified-project-settings-acceptance-evidence/hook-recovery/artifacts-phase1/docs/plans/hook-recovery.task-contract.md)、[第二階段原始回合](unified-project-settings-acceptance-evidence/hook-recovery/model-phase2.stdout.jsonl)、[實際注入紀錄](unified-project-settings-acceptance-evidence/hook-recovery/hook-session-records.json)、[兩階段摘要](unified-project-settings-acceptance-evidence/hook-recovery/summary.json) |
| F：模型規則、真實派工與回退 | **受測政策、派工與回退通過。** 實際 agent 判讀 11 組優先序／清單／default／去重／限制／新任務資料，明示它們是政策輸入，不冒充 provider 事件。正常派工由角色選到 gpt-6-sol，宿主 turn_context 記錄主責 gpt-6.1-sol、子 agent gpt-6-sol。實際不可用首選回傳 HTTP400 model_not_found；先查 handle 由 running 轉 errored，才派第二候選並取得 completed。另由本次原生 model/list 判定 gpt-6-sol 不支援 none、預設 medium，保留模型並成功派出 medium worker，長期設定未變。 | [11 案政策判讀](unified-project-settings-acceptance-evidence/model-policy/artifacts/docs/research/model-policy.research.md)、[正常獨立派工](unified-project-settings-acceptance-evidence/staged/F-independent/artifacts/docs/research/model-review.research.md)、[正常派工宿主上下文](unified-project-settings-acceptance-evidence/staged/F-independent/session-model-contexts.json)、[真實 model_not_found 與回退](unified-project-settings-acceptance-evidence/fallback-dispatch/model.stdout.jsonl)、[回退結果](unified-project-settings-acceptance-evidence/fallback-dispatch/artifacts/docs/research/fallback.research.md)、[本次模型 metadata RPC](unified-project-settings-acceptance-evidence/effort-preflight/metadata-rpc.json)、[medium worker 上下文](unified-project-settings-acceptance-evidence/effort-preflight/session-contexts.json) |
| G：無子 agent、獨立審查缺口 | **受測限制通過。** 原生 state 設定 agents.enabled=false，模型看到沒有建立工具；未解除限制、未安裝外部派工器。唯一合約的獨立審查 T1 保留 blocked，主責完成無相依 T2，整體保持 blocked，精確產出 MAIN_WORK_DONE。 | [限制及執行來源](unified-project-settings-acceptance-evidence/staged/G-disabled/run.json)、[原始回合](unified-project-settings-acceptance-evidence/staged/G-disabled/stdout.jsonl)、[合約](unified-project-settings-acceptance-evidence/staged/G-disabled/artifacts/docs/plans/no-agent.task-contract.md) |

## 已安裝候選與 copied-skill 的實際接線

- 已安裝候選的小任務取得精確 PACKAGED_OK 與一份 done 合約；[session 紀錄](unified-project-settings-acceptance-evidence/packaged-hooks/hook-session-records.json)包含兩個真實 developer message，內容分別等於發行 SessionStart／UserPromptSubmit 提醒。這是實際模型上下文注入，不只是 hooks/list 列舉。
- [純複製案例](unified-project-settings-acceptance-evidence/standalone-copy/summary.json)沒有 plugin 安裝，只有已複製的四個 skills 且 scripts 被省略；模型透過 generic project-setting 讀取 harness 自帶 asset，寫入 project-setting.md、專案 hooks/config。每個 canonical handler 恰有一份，preserve.txt 未變，沒有依賴來源 repo 的 packaging 目錄。
- native 執行使用單次 `--dangerously-bypass-hook-trust`。此為測試控制器對已核對的固定命令使用的隔離 automation 選項；兩回合案例在第二階段前再次比對所有新命令與 canonical／PS 資源及未改 sentinel。它不是正常持久信任驗收，也不應成為日常安裝的建議捷徑。
- Stop 發行命令為固定 `{}` 被動回應。公開封裝測試直接回放含重複 Stop；真實任務正常結束，但 CLI 沒有獨立的每次 Stop handler 執行通知。本輪不宣稱條件式阻擋、一次性補救、原子收據或抵抗使用者停止。

## H1–H8 宿主能力判定

| 能力 | 已觀測 | 明確限制／未驗證 |
| --- | --- | --- |
| H1：接入、載入、信任、觸發 | 最終新安裝及升級的 loader／manifest；固定提醒實際進入 developer context | 正常持久 hook 信任未驗證；原生 loader 仍顯示 untrusted，執行案例有測試 bypass |
| H2：上下文、阻擋、續作、Stop | 兩種提醒實際注入；wait 回合沒有提前做 T2；被動 Stop 回放與正常收尾 | 本版沒有條件式阻擋或一次性續作保證；未測使用者 UI 的原生 interrupt |
| H3：身分、回合、重複與恢復 | 真實 thread/turn 識別、跨回合同一合約、一次寫入保持；不存在的身分在合約保留 null | 未測 hook 生成續作與真正輸入的全套辨識；本版 passive Stop 不生成該續作 |
| H4：模型、強度與角色優先序 | 正常角色派工、真實候選拒絕與安全改派；host turn_context 的模型／強度、medium 修正 | 底層 provider 的模型權重身分不可獨立觀測；報告不以模型自述填補 |
| H5：目前對話及手動切換 | 原生主責／子 agent 上下文與不擅改主責的實際案例 | 任務中使用者手動切換對話模型、既有 agent 維持原設定的完整 UI／API 生命週期尚未實測 |
| H6：不可用／強度不支援／派工失敗 | 真實 model_not_found；本次 model/list 強度支援與預設；實際保留模型改 medium；早期歷史載入失敗不被誤認模型不可用 | 未故意送出 provider 的非法強度請求；strict 範圍以真實模型判讀測試資料驗證，沒有違反限制的呼叫 |
| H7：未知啟動查核 | 真實 handle running→errored 後才回退；未知 append 先核對；過期 driver trial 保留未知 | 未完成真實網路斷線後的跨 session worker 終態全流程 |
| H8：安裝／升級與來源一致 | 最終 7e37d7… 全新安裝及 0.2.1 升級均讀回完整來源與 exact manifest | 沒有更動既有日常安裝／全域 cache；不宣稱所有宿主或 Windows 已測 |

## 未驗證細分路徑與風險

這些不是已確認的程式缺陷，也不能標成已通過：

1. B 的「缺少必填鍵後自動修復」、純空白／列順序重排的全部變體，尚未各做獨立真實 agent 案例；已測新初始化、有效讀回、重複／衝突／無效版本的拒絕與保留。
2. C 未注入實際磁碟寫入失敗、寫後讀回 I/O 故障、刪檔失敗或原生進程中斷。本輪涵蓋衝突、唯讀禁止寫入、未有效讀回時不刪除，以及已寫新設定／舊檔仍在的真實 agent 恢復；後者明確是 fixture，不冒充發生過的 OS 中斷。
3. E 沒有故意重送相同宿主 hook event 的完整 native 事件重入試驗；已觀測恢復後相同 ledger 未重寫、同一合約未複製，這不是跨程序原子去重保證。
4. F 的「包含專案預設也全部不可用」、「真正啟動逾時後跨 session 查回」、「實際同任務保存單次模型覆寫後恢復／新任務」、「手動切換主責後的後續派工」尚未全部實測。已測實際模型選擇、首選拒絕後改派、host-default 強度修正；default／去重／新任務不沿用的政策判讀沒有冒充完整 provider 生命週期。
5. normal trust、原生 Windows 與所有帳號的模型可用性仍是平台限制。維護測試略過的 1 項就是 native Windows，沒有以 POSIX replay 取代。

## 失敗、未知與開發端問題保留

- [早期 F](unified-project-settings-acceptance-evidence/staged/F-prelaunch-failure/stdout.jsonl)的 ephemeral 歷史載入失敗由真實 host 回報；未取得成功 handle，agent 保留獨立審查缺口。後續獨立新 fixture 使用 persistent session／自足輸入完成正常派工，未改寫原失敗紀錄。
- [T06 原抽樣](unified-project-settings-acceptance-evidence/staged/FG-timeout/run.json)到期前未取得回合終態，仍為未知，不算 G 通過或未執行證明。G 的判定另有真正 agents.enabled=false 案例。
- [final-upgrade-launcher-failed](unified-project-settings-acceptance-evidence/final-upgrade-launcher-failed/launcher-note.json)是開發 probe 的 argparse 名稱被迴圈變數遮蔽，尚未啟動任何模型回合。保留當時原始 CLI 回應；修正後在另一個新隔離 state 完成最終升級。它不被歸為產品失敗或產品通過。

## 證據核對與隔離

[唯讀核對器](unified-project-settings-acceptance-evidence/check-evidence.py)以獨立的精確內容、before／after 指紋、既有 task ID、合約狀態、native error 與 session context 核對產物；[核對結果](unified-project-settings-acceptance-evidence/assertions.json)記錄 39 項通過。這是既有證據的查核，不是另一輪產品測試，也不是 runtime 依賴。完整原始檔案的實際 SHA-256 見[證據索引](unified-project-settings-acceptance-evidence/evidence-index.json)。

所有新增模型案例使用獨立 state/project/catalog。登入檔僅在 owned 0700 暫存 state 內建立 0600 複本，結束時清除；封裝 loader 不需 auth。每輪保存正常 config.toml／auth.json 前後相同的判定，沒有將憑證複本歸檔。歸檔檢查亦逐檔比對實際憑證字串，沒有發現值被保存；只保留無憑證的 raw、產物與來源指紋。

上述保留證據直接涵蓋 config/auth 與操作使用的隔離 cache 路徑，不是整台機器／OS keychain 的全面差異稽核。部分 exec 在沙箱啟動前被拒，真實紀錄保留後由宿主批准的同一 scoped 操作完成；沒有為此安裝 runtime、改全域設定或操作其他專案。

原始產物保持逐位元組不變，因此 staged diff 的完整 whitespace 檢查保留三項原始產物警告：兩份舊設定檔尾端空行、一份舊審查檔的 hexdump 尾端空白。沒有為了消除警告改寫 raw；本輪撰寫的報告、票與開發 probes 另行檢查通過。

維護者完整測試為 112 項、略過 1 項，另有九個公開封裝案例與獨立兩軸審查；這些與真實 agent 行為證據分開判定，詳見[來源審查](unified-project-settings-review.research.md)與[封裝報告](unified-project-settings-package.research.md)。
