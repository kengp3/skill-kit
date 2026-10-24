# 個人 Harness 實作查核紀錄

日期：2026-10-24。狀態：開發進行中，整套驗收未完成。

本紀錄按時間保留查核與修正。原生接入及 C 的 Desktop 只讀純預檢已有證據；可寫 coding 邊界與正式 smoke 尚未完成。最新狀態見文末「C 純預檢的建立與 Desktop 執行」。

## 來源與修改

起點 simple-skills HEAD `7ee5f1c6be075a38e1ab5f2a96c3c84856d1cc99`；無關既有未提交內容保留。原 demo-002 未更動；隔離來源為 `git archive` 的 root POM 與 concurrent-request-scope，不包含 Git history。實際暫存位置與 revisions 見 [workspace manifest](codex-coding-harness-implementation-evidence/lifecycle-workspaces.json)，來源指紋見同目錄 `lifecycle-parent-sources.json` 及 `lifecycle-reference-sources.json`。原始 B runtime 於改動前保存在同目錄 baseline-B，與宿主 trial 配置分開。

runtime 保留四個 skills 的完整子目錄，不包含 docs、tests、評測 fixture。打包器只組裝及核對，不安裝、不執行信任或自動刷新；manifest 不是簽章，需與外部保存的可信指紋比對。

## TDD 與 review

- 首個包邊界測試先因缺少 CLI 失敗，再通過獨立目錄執行 helper。
- manifest 核對測試先因缺少 verify 介面失敗，再通過；檢查內容修改及額外檔案。
- Standards review 發現來源根 symlink 及必要 skill 缺漏；兩項負向測試先失敗，加入前置驗證後通過，獨立複核確認解除。
- Spec review 發現修改前基線與 review 輸出負擔；補主流程規則、內部 review 模式後，獨立複核確認解除。
- 初版 thread grader 只在既有實作辨認到差異；review 發現會誤拒 shared scheduler 等合法解法，因此保留為 initial-thread-probe.java，禁止用它判正式 trial。

## 可取回結果

- [Python 維護測試](codex-coding-harness-implementation-evidence/python-tests-2.json)：原始 argv、cwd、stdout/stderr、最終退出碼及來源指紋；含 skipped，不當成全平台通過。
- [Parent 首輪效果型 grader](codex-coding-harness-implementation-evidence/lifecycle-parent-2.json)、[reference](codex-coding-harness-implementation-evidence/lifecycle-reference-2.json)：12 tests，parent 只有 shutdown 後持續 cleanup 的斷言失敗；reference 全部通過。
- [Parent 複驗](codex-coding-harness-implementation-evidence/lifecycle-parent-3.json)、[reference 複驗](codex-coding-harness-implementation-evidence/lifecycle-reference-3.json)：同一效果型 grader 在新 JVM 重驗，結果相同，相關來源指紋穩定。

效果型 grader 先建立可觀察的 TTL callback，證明背景清理確實運作，再建立另一個 orphan 並關閉 context，確認之後沒有 cleanup callback。接受 shutdown 同步 cleanup；不要求特定方法、私有欄位或 thread 型別。有限等待窗口不證明所有資源均釋放，也不能排除空轉但無可觀察 callback 的排程；資源所有權與合法替代解法仍須補驗。以上是案例資格準備，不是 agent trial，也沒有人工省時結論。

## 必要控制與未完成門檻

| 條件 | 實際執行者及覆蓋 | 失效行為／證據邊界 |
| --- | --- | --- |
| 避免發佈外部 symlink／缺漏入口 | 打包器對固定 runtime 來源 preflight，public CLI 負向測試 | 拒絕建包，不將自洽 manifest 當依賴完整證明 |
| 保護既有 release | 打包器目的地已存在時拒絕；測試 sentinel 保留 | 不覆寫；不是多個惡意並行建包者間的防護服務 |
| 過期來源不得驗收 | helper 前後來源 hash、主流程重開驗收 | checker 即使 exit 0，來源改變時 helper exit 3 |
| 未知結果不得盲重播 | 已存在 receipt 時 helper 在啟動前拒絕；marker 無副作用 | 此證據只涵蓋 helper，其他宿主／MCP 路徑待驗證 |
| 工具權限及外部副作用 | 宿主 sandbox／approval 及專案規則 | 不新增權限；完整工具覆蓋仍未實測，不以提醒 hook 背書 |
| 完成前必要驗收 | workflow 與既有檢查 | 必要結果欠缺即未完成；未實作宿主強制 completion gate |

Desktop 原生 plugin 安裝與啟停尚未驗證。Computer Use 禁止操作 Codex 自身；未繞過限制。全域現有 plugin 對 A/B/C 的影響尚未隔離，未知狀態、原生持久證據、回退及完整安全路徑仍是 G01–G05 缺口。目標維持 active，不宣稱整套完成。

最終 grader 補時序有效性檢查：第二個 orphan 在 close 前仍須未清理，且建置至 shutdown 完成不得跨 TTL；不合格以 JUnit assumption 標 skipped。任何 lifecycle skipped／未執行均屬無效觀測，不因 Maven exit 0 而算資格通過。前兩輪結果對應此修正前版本，修正後須另驗並保留原結果。

[時序修正後 parent](codex-coding-harness-implementation-evidence/lifecycle-parent-4.json) 與 [reference](codex-coding-harness-implementation-evidence/lifecycle-reference-4.json) 已重驗。Surefire XML 保存在同目錄 `lifecycle-parent-4.xml`／`lifecycle-reference-4.xml`：lifecycle 各執行 1 項、skipped 0；parent failure 1、reference failure 0。只支持目前案例窗口，不將先前版本的多輪數量轉記為此版本的穩定性結論。

## 後續資格與接入查核

- 加入合法替代實作：共用 static scheduler，只取消本 scope 的 ScheduledFuture，保留共用 executor。來源 patch、manifest、第一輪 receipt/XML 位於同 evidence 目錄的 `shared-scheduler-*` 與 `lifecycle-shared-scheduler-1.*`。同一 grader 及既有 11 測試共 12/0，lifecycle skipped 0；獨立 Spec review 確認不再過度綁定專屬 thread。
- Review 又指出 shutdown 後基線取樣可能被暫停跨過 TTL；現已先取樣再驗時間，使有效性檢查涵蓋基線擷取。最新 `lifecycle-{parent,reference,shared-scheduler}-5.json`／XML：parent lifecycle 1 failure；reference／shared-scheduler 各 0 failure；均 1 lifecycle test、0 skipped，既有 11 測試皆通過。前版本結果保留，不合併成同版重複次數。尚未將有限觀測外推為所有資源釋放已證明。
- 新增 public CLI 輸出 alias 防護測試，先紅後綠：實際目的地落入 runtime 來源時拒絕；Standards 獨立複核通過。新增 POSIX 真正中斷測試，helper 保留 unknown／returncode null；既有 receipt 防重播仍有效。最新 `python-tests-3.json`：26 tests、skipped 1、退出 0、來源穩定。Windows interruption 未驗證。
- `native-retrieval.json` 保存宿主 read_thread 從上一個已完成 turn 讀回的命令事件；含命令、cwd、最終狀態、結果及截斷標記。證明跨 turn 取回，不等於新 session 恢復或所有原始輸出完整。
- 先前以為本機安裝只能靠 Desktop UI，現已更正：PATH CLI 及 Desktop 內附 CLI 都有 `plugin add`。直接執行內附 `0.163.0-alpha.11.2`，以僅本次命令的 marketplace 設定可辨識本 repo 的 personal-harness 0.1.0，見 `bundled-plugin-discovery-1.json`；狀態 installed false／enabled false。沒有寫入全域設定或執行安裝。
- 安裝預設行為仍須處理：目前官方 upstream `install_resolved_plugin` 會在安裝後呼叫 set_user_plugin_enabled(true)。此為 main 分支來源，不能直接斷言安裝中版本完全相同；但有足夠理由不直接執行 add，以免違反各專案 opt-in。當時尚待查明可維持全域停用的原生安裝／專案採用路徑，後續已由正式專案設定解除（見文末）；未採用短暫全域啟用再停用。

官方查證：[CLI plugin 命令來源](https://github.com/openai/codex/blob/main/codex-rs/cli/src/plugin_cmd.rs)、[plugin manager 安裝行為](https://github.com/openai/codex/blob/main/codex-rs/core-plugins/src/manager.rs)。上述 main URL 為動態參考，不能代替安裝中 binary 的實測證據。


## 原生接入落地（目前狀態）

1. 對單次 CLI 覆寫的停用配置只辨識套件，沒有準備快取。正式 repo `.codex/config.toml` 加上候選 `enabled=false` 後，內附 app-server 自動準備快取，installed true／enabled false；`skills/list` 無候選技能。見 disabled-cache-probe-4.json。原始 sandbox 初始化失敗的 stderr 與第一次觀測亦保留，不當成成功。
2. project-opt-in-probe.json：只暫時在 simple-skills 啟用，載入四個具 namespace 的快取技能；demo-002 為零。disabled-after-enable.json：新的 app-server 程序中已回到零。每次 user config 前後 hash 相同。
3. 以官方 marketplace add 註冊共用來源，未執行 plugin add。marketplace-registration-{before,after}.json 證明來源已註冊、候選 user plugin 設定仍不存在、其他 plugin 設定不變。registered-source-probe.json 為無 CLI 覆寫的停用查核。
4. update-probe-2.json／rollback-probe-2.json 的 argv 僅為官方 binary、app-server、--stdio，沒有配置覆寫。原生技能實際路徑依序為 0.1.1／0.1.0，另一專案始終零。回退前 update-cache-verification.json 實際核對 0.1.1 快取完整 manifest/hash 與可信探測包相同；0.1.0 也核對相符。舊的僅路徑證據仍保留，不用它代替完整核對。
5. 最終本 repo 明確啟用 0.1.0 作後續開發使用；development-adoption-probe.json 在無 CLI 覆寫下列出本 repo 四個快取技能、demo-002 零，skills errors 為空。marketplace 已指回原包，demo-002 原工作樹不變；沒有新增全域 plugin 啟用項目。

這次真實快取目錄以 0.1.0／0.1.1 命名，與部分動態文件所述 local 不同；以實際來源及 manifest 為準。宿主可能清除已不用的快取，因此另外保存可信 release。當次 probe 來源留在 probe-sources（.py.txt）及其 manifest，僅為歷史證據，不是新增 runtime 工具。

上述由 Desktop 內附的獨立 stdio app-server 完成，證明原生引擎的專案配置選取、技能發現及快取內容。尚不能取代 Desktop 活躍 session 的模型行為、必要工具控制、更新中任務的版本固定或跨 session 恢復。下一個驗收切片是必要執行邊界與真實 coding smoke 的前置資格；三組尚未開始。

## 執行邊界與 smoke 前置查核

- 首次 `sandbox-boundary-probe.json` 不合格：app-server 從來源 repo 啟動，僅將 command/exec 的 cwd 設為暫存 workspace，實際自身 marker 寫入被拒，而原 repo 的新 canary 寫入成功。已刪除探測自己建立的新 canary，原檔未變。該失敗完整保留，不作安全證據，也沒有在此配置啟動模型。
- 改為 app-server 本身從隔離 workspace 啟動，並使用 workspaceWrite、excludeSlashTmp=true、excludeTmpdirEnvVar=true、networkAccess=false。sandbox-boundary-probe-2.json／observation-2.json：自身 marker exit 0；原 repo 新 canary 寫入為 PermissionError／exit 1；連線至同一探測建立的本機 listener 也為 PermissionError／exit 1。user config hash 不變。此結果只驗證 command/exec 路徑，尚不泛推為 apply_patch、MCP 或任意工具完整覆蓋。
- 原生 model/list 可取得 gpt-6.1-sol，支援 high reasoning，與目前使用者設定相同；見 model-inventory-probe.json。這是精確 slug，沒有聲稱不可見的底層模型 build 版本。只讀查詢，沒有模型 turn。
- 已準備三份相同 parent archive（smoke-preparation.json）：A 無額外 harness；B 帶不可變舊版 skill；C 帶完整候選包、repo marketplace 及專案 opt-in。三組相同 TASK.md 與既有 AGENTS.md（含相關 dirty content 的共同版本），均未開始 trial。試行讀取邊界尚未隔離答案，因此不得作公平能力比較。
- 預檢 A 沒有候選 workflow，B 可辨識舊版；C 的 project config 被宿主列為未受信任而停用（trial-discovery-preflight-2.json）。SessionFlags 的 projects trust 設定未解除這個決策，原生回應要求 user config 中的 canonical project trust。此為實際資格阻礙，不以 config 檔案存在當作已載入。後續須在選定宿主方法後依原生信任流程處理受控 trial workspace；尚未開始 C 模型 trial。
- 使用者已核定三組各 1 次、各 15 分鐘、不整次補跑與不購買額度。是否改用 Desktop 內附 CLI 執行首輪 smoke 已詢問，仍待回答；沒有把 CLI smoke 偷換成 Desktop 主視窗驗收。

可見任務與外部 grader 另補上多 context 行為：關閉一個 context 不應停止另一個仍存活 context 的清理。最新版 lifecycle-{parent,reference,shared-scheduler}-6.json／XML：總共 13 tests，lifecycle 2 tests，均 skipped 0；parent 僅目標 shutdown 行為失敗，reference 與合法共用 scheduler 全部通過。第 7 組以同版 grader 重驗，結果相同；receipt 另補綁定全部 47 個 root／module POM 與 Java production／test 輸入，前後 hash 及取回時目前檔案皆相符，XML 保存在 lifecycle-{parent,reference,shared-scheduler}-7.xml。前幾版只綁 grader 的 receipt 仍保留，不追溯冒稱完整來源綁定。這些仍是資格檢查，不消耗或冒稱三組模型 smoke。原生 API schema 來自當前內附 binary 的 generate-json-schema；使用的 probe source 已按原始內容保存為 .py.txt，避免誤作 runtime 腳本。

## 持久證據跨程序取回

[native-persisted-read.json](codex-coding-harness-implementation-evidence/native-persisted-read.json) 保存兩個全新 app-server 的實際 argv、cwd、PID、請求／回應與終止結果。程序依序啟動、終止；均只 initialize 後用 `thread/items/read` 查詢既有 thread／turn／item ID，未 resume、啟動模型或執行該歷史命令。兩次 commandExecution item 完全相同，command、cwd、completed、exitCode 0 與 aggregatedOutput 均對上先前 native-retrieval.json 的第一筆命令，user config 前後 hash 相同。Probe 原始碼另保存在 probe-sources 的 .py.txt 並納入其 manifest。

這補足原生持久結果在新程序可取回的窄邊界。未證明模型能在新 session 正確恢復待辦、核對 writer liveness 或處理未知副作用；原先命令對應的歷史來源也不能直接作目前版本的通過證據。首輪三組仍未開始，宿主方法的決定與 C 專案信任資格保持未決。

## 發佈包的獨立目錄資格

[standalone-runtime-qualification.json](codex-coding-harness-implementation-evidence/standalone-runtime-qualification.json) 記錄同一 0.1.0 包在開發 checkout 之外的查核。18 個內部 Markdown 連結均能在包內解析；封裝的 review.py 從該目錄以小型 Git fixture 執行 prepare／verify，快照內容與兩個版本一致；check_report_hashes.py 亦可載入包內 review 模組，接受正確 hash、拒絕檔案變更後的過期 hash。19 個 runtime 檔案前後符合相同 manifest，未寫入開發來源或原 demo-002。暫存 fixture 於查核後清除，命令／cwd／退出碼／輸出保存於上述紀錄，原始查核輸入在本任務的命令事件中可取回。

此結果支持這些入口的依賴完整性，不代表模型已使用該包完成 coding／review，也未重驗不受本次改動影響的全部 migration 比較行為。規格中原先「歷史版本尚未執行」的假設同步更新為設計時背景，避免與目前案例資格證據矛盾。

## 原生 standalone exec 的取消

首次 native-cancel-probe.json 未形成有效觀測：fixture 子程序的字串語法錯誤，未證明預定副作用。native-cancel-probe-diagnosis.json 保存編譯診斷與當時程序表查核，沒有該 fixture 的存活程序；原始 probe 另保留為 initial.py.txt，不算宿主取消成功，也不隱藏為未嘗試。

修正 fixture 後，[native-cancel-probe-2.json](codex-coding-harness-implementation-evidence/native-cancel-probe-2.json) 記錄實際 command/exec、cwd、sandboxPolicy、自限時 worker 原始碼及取消請求。送出取消前已有 heartbeat `tick` 與 parent／child PID；command/exec/terminate 回覆後，原 exec 最終 exit 137、stdout started。最終結果後與清理前兩次 ps 均未列出這兩個 PID，且無 stderr；heartbeat 保留既有 4 字元、後續觀察未增加，user config hash 不變。Probe 原始碼及指紋在 probe-sources，獨立 Standards review 已核對原始證據與此界定。

只支持此 standalone exec fixture 的取消、最終結果與程序存活查核；不能據此保證所有 process tree、模型 turn、MCP 或斷線失聯的行為。既有寫入沒有因取消消失，符合「取消不證明 mutation 未發生」的設計。這些探測未啟動模型或消耗 smoke 次數；首輪執行宿主仍待使用者決定。

## 首版整合審查

以 `7ee5f1c6be075a38e1ab5f2a96c3c84856d1cc99` 為起點，對此次 tracked working-tree diff 與明列的新打包／配置／測試／fixture 檔案進行兩軸獨立 review；未將其他既有 untracked 內容當成本次實作。此間沒有本 repo 的新增 commit。

- Standards：無新增可行動 finding；前次打包邊界及 grader 問題保持已解除。
- Spec：兩項文件問題已解除。新規格及計畫前段不再將目前現況寫成尚未實作／啟用，實作前盤點明標歷史；README 說明 task-harness 的 define-task／ai-code-review 按需相依目錄，舊 task-harness 規格保留正文並標明歷史基線。Spec reviewer 已唯讀複核修正，沒有新矛盾。

本次文件修正未改 runtime，不因此重建包或重跑無關測試。兩軸 review 沒有代替仍欠缺的實際工具控制、模型續作、Desktop 主視窗及三組 smoke 驗收。當時仍待宿主選擇；後續使用者已選擇維持 Desktop，見下節，不再等待是否改用 CLI 的決定。

## 維持 Desktop 後的其他查核

使用者明確選擇「維持 Desktop 主視窗，先完成其他查核」。正式模型 smoke 不改用 CLI，先前已詢問的宿主選擇已結案。

- **案例資源所有權：**獨立 Spec review 讀取 reference／shared-scheduler 的 scope、Spring postprocessor 與 grader，六份來源目前 hash 均符合第 7 組 receipt。專屬 executor 經 disposal 關閉；共用 scheduler 的替代實作只取消自身 future，兩者可作本案例的合法資格實作。見 lifecycle-ownership-review.json。未將 shutdownNow／cancel(true) 解讀為可強制中止忽略中斷的 callback；其他 BeanFactory、classloader 整體生命週期未驗證，每個實際 trial 產物仍要查所有權。
- **受控目錄信任：**project-trust-preflight.json 先對三組全部記錄檔案及檔案集合核對，拒絕未列檔案／symlink，再用原生 config/value/write 設置三個 canonical workspace trust，串接 expectedVersion。實際語意差異僅這三項 trust；未停用必要關卡或填入 hook 信任 hash。C 專案層不再有 disabledReason，但該輪技能尚為零，未當成已載入。
- **來源註冊與刷新：**trial-marketplace-registration.json 記錄官方 marketplace add 只增加 personal-harness-trial-C 來源，user-level 候選 plugin 啟用項仍不存在，既有 plugins 不變。第 3 次未刷新 catalog，C 仍為零；第 4 次先呼叫原生 plugin/list，再取得 A 無本次額外 harness、B 一個舊版入口、C 四個候選快取技能，errors 均空，該程序前後 config hash 不變。三組仍有共用全域 skills，不宣稱純淨 A 或公平能力比較。
- **內容資格：**trial-input-readiness.json 記錄 A48／B51／C70 個原檔指紋不變，共同 48 個輸入一致，三組無 Git history／remote。B 仍吻合修改前快照；C 完整快取經 verifier 核對，manifest 符合原可信 cdd9… 指紋。準備紀錄的 host_choice 已更新為 desktop_main_window，三組模型 trial 仍為零。

Standards reviewer 已唯讀複核上述設定變更與證據界線，沒有新增 finding。原始 probe 以 .py.txt 保存於 probe-sources 並納入 manifest。三項 project trust 與 C marketplace 來源是持久副作用，目前保留以準備 Desktop 試行；結束或取消時需針對這些項目清理，不回寫舊整份 config 覆蓋其他使用者變更。

這些結果仍只證明原生引擎或案例的窄邊界資格。Desktop 活躍對話的實際配置、原工作與 grader 的寫入保護、各工具副作用控制、取消／續作、時間上限及正式三組 smoke 尚未完成。下一個最小切片是實際 Desktop 的純載入與執行邊界預檢；Computer Use 禁止操作 Codex 自身的限制仍適用，不透過其他 UI 技術繞過。

### 目前 Desktop 對話已收到候選技能目錄

後續宿主提供的 developer skills_instructions 已新增四個 personal-harness:* 入口，精確來源是 personal-harness-local/personal-harness/0.1.0/skills。主 agent 直接讀取快取 task-harness 並在本輪採用；原生完整包核對 exit 0，manifest SHA-256 符合既存可信 cdd9… 指紋。desktop-active-catalog.json 保存宿主目錄的明示轉錄、四個入口的當前 hash 與原生讀取／核對事件定位。原宿主訊息是目錄依據，JSON 不是另一個自動檢測工具。

此證據只對應目前 simple-skills Desktop 對話，不能替代 C 隔離對話、實際 GUI、coding 行為或完整權限驗收。原生專案清單尚無 C，現有 create_thread 必須選擇已登錄專案且無任意路徑參數；本工具組無新增專案入口。配套計畫已準備 C 路徑及只讀預檢任務，先由使用者在 Desktop 加入該目錄，再依明確的新對話授權接續。沒有啟動任何模型 smoke。


## C 純預檢的建立與 Desktop 執行

使用者明確授權建立新對話並再次確認 C 路徑後，已完成「C 純預檢」：thread `01a16bf4-9fbb-7681-8d9e-ae1d1cf68edf`、turn `01a16bf5-3b73-7e22-9d46-f5bde9a32914`，Desktop 回報 completed。正式 smoke 次數仍為零。

接入改用[官方 App Server 的 thread/start 與 inject_items](https://learn.chatgpt.com/docs/app-server)：只建立對話、保存初始任務及名稱，不呼叫 turn/start。第一個空白 ID 未持久化，Desktop 回報找不到；後續只讀查核回報 not loaded，再以 resume 確認沒有舊 rollout 後，才建立可持久取回的任務。原始請求與結果保存在 desktop-C-thread-create.json、-2.json、-3.json。準備程序沒有執行模型；Desktop 工具確認可讀後，透過原生 send_message_to_thread 啟動模型，再以 wait_threads 取得 completed。inject_items 僅保存使用者已授權的初始任務；Desktop 模型結果另取原生執行事件，未改寫內部資料庫。對話沒有專案 ID 的登錄證據，但實際 cwd 與 runtime root 都是指定 C。

[原生讀回](codex-coding-harness-implementation-evidence/desktop-C-preflight-readback.json) 保存 Desktop 命令事件、退出碼、輸出及最終回報；[Owner 核對](codex-coding-harness-implementation-evidence/desktop-C-preflight-owner-check.json) 直接檢查 pwd 與完整 E14 結果，並在本對話重新核對 C 的 70 個輸入及檔案集合未變。E14 為 19/19 source／cache hash 相符，manifest 符合原可信 cdd9… 指紋。讀回仍有一筆長技能輸出截斷，初期工具啟動失敗也未全部呈現為 commandExecution，沒有把這份資料稱為完整無缺的原始軌跡。

準備回應的原生版本為 0.164.0-alpha.11.1，配置模型為 gpt-6.1-sol／high，sandbox 為 readOnly 且 networkAccess false。這些是配置及版本證據，未證明實際 serving build 或路由；先前 0.163 的執行邊界證據不能直接外推新版本。Desktop 只讀預檢遇到 heredoc／Python launcher 的暫存寫入限制，最後改用不需這些寫入的讀取方式完成，沒有升權。遭拒範圍不泛推所有工具或 coding workspaceWrite。

Standards reviewer 已唯讀複核交接、Owner 證據與限制，沒有新增重大 finding。原始準備程式另保存於 probe-sources 並納入 manifest。新對話及模型預檢紀錄是本輪已授權的持久副作用；未修改程式、專案設定或啟動正式 smoke。下一個必要驗收仍是 Desktop 可寫 coding 的操作邊界與恢復能力。


## Desktop 可寫控制預檢：已證明的路徑與剩餘缺口

使用者授權一個控制預檢對話及合格後的三組 smoke；已建立控制對話 `01a16c0c-7b36-73e3-8a16-209598391f8d`，尚未開始 smoke。共用試行配置及實測限制詳見[計畫第 14 節](../plans/codex-coding-harness-pilot.plan.md#14-desktop-控制預檢與-smoke-進入門檻)。未修改 runtime 發佈內容。

`desktop-control-thread-create.json` 保存原生 0.164.0-alpha.11.1 的有效 workspaceWrite／networkAccess false／tmp exclusion；`desktop-control-readback-1.json` 保存 Desktop 實際命令結果。指定自身寫入成功，外部 exec／symlink 寫入與指定 loopback connect 遭拒。補取的 `desktop-control-patch-call-and-result.json` 由本輪對話的精確原始 rollout 按同 call_id 配對輸入與拒絕，沒有修改內部紀錄。Owner 核對三份 guard hash 未變，實際 listener connections 0 且已停止。

同 handle Ctrl-C 使合作型父子 canary 在自限時間前退出；`desktop-control-worker-owner.json` 顯示兩 PID 缺席、heartbeat 在觀察期間穩定。此結果不能推論模型 turn 已取消。外部獨立 server 的 `turn/interrupt` 回覆 thread not found，見 `desktop-control-interrupt.json`；文字停止後 turn 為 completed。[官方 App Server 文件](https://learn.chatgpt.com/docs/app-server)說明成功取消應有 interrupted 最終狀態，本輪未取得。15 分鐘的可靠停止仍是必要缺口。

`desktop-control-owner-reconciliation.json` 核對三組記錄輸入 49／52／70 份全數未變及全域配置未變；canary 原檔保存於 desktop-control-canary-artifacts，連結只記目標、不跟隨；worker 結束後已清除 C 的測試檔與 escape 連結，見 desktop-control-canary-cleanup.json。歷史 probe 程式以 .py.txt 保存於 probe-sources 並記 hash，不納入 runtime。

Standards 獨立 review 支持受測路徑的窄結論，提醒 first-party 工具與額外 visualization 可寫 root 仍存在；不能宣稱所有外部工具已封鎖，也不能以 C 實測直接外推 A／B。原生清單目前沒有可直接中止其他 Desktop turn 的工具；handoff 會移動 checkout，不能為了停止而改變試行宿主。未使用 Computer Use 操作 Codex 或其他繞路。後續是否採使用者在場手動 Stop 尚待決定，且須先驗證並記入人工投入；不預設使用者同意。


## 人工 Stop 的首次直接測試未通過

使用者選擇人工監看／Stop 後，在同一個 Desktop 控制對話執行 120 秒自限父子 canary。使用者兩次回報點擊，但第一次回覆後的 owner 原始查核仍見兩 PID 存活、heartbeat 增加；最終 command 執行 120085ms，自行到期，parent_stop_signal=null。模型 turn `01a16c29-3650-7b10-ab8e-49bcd72c4152` 為 completed，沒有 interrupted。原始 command／cwd／final output 見 manual-stop-desktop-readback.json；三個 owner observation 保留操作前後狀態，最後 PID 均缺席且 heartbeat 穩定。

Standards 獨立複核封存指紋與退出原因，結論是不足以證明 UI Stop 有效；child 的 SIGTERM 是 parent 到期清理。此結果也不證明使用者按錯、UI 普遍故障或特定根因。首次 canary 原檔已封存，確認 terminal 後清理。成本只知兩次使用者回報操作，人工 active seconds 未量測。

下一個診斷準備為同一對話中由使用者直接送出 canary 任務，worker source hash 與首次相同；只檢查回合啟動路徑是否影響可停止性，尚未執行。此假說與原生 C project 清單仍缺席均不能當成原因結論。詳見[計畫第 15 節](../plans/codex-coding-harness-pilot.plan.md#15-人工-stop-首次驗證結果與下一個診斷)。未啟動任何正式 smoke，runtime 不變。


## 直接 UI 回合的後續 Stop 診斷結果

使用者直接輸入任務的原生 userMessage 已保存於 manual-stop-direct-ui-desktop-readback.json，排除「第二項診斷其實又由 controller 派送」的混淆。使用者回報按 Stop 後，owner 仍觀察到回合 inProgress、父子 PID 存活且 heartbeat 增加，未取得 interrupted。隨後由 controller 對核對過的 canary parent 發 SIGTERM 清理；command 最終 signal15 不能歸因 UI Stop。模型以 completed 結束，父子程序均消失；原檔封存、測試目錄清空、三組記錄輸入未變。

這不支持「由使用者直接啟動即可解決」假說，也不足以確定宿主根因。兩種人工路徑已實測，不再要求使用者重複點擊。Desktop 到時停止仍未合格，正式 smoke 為零。計畫第 16 節列出待使用者選擇的宿主調整建議：同一內附 CLI、自有 App Server 連線、先驗證當前版本控制，保留 Desktop 驗收未通過；不是已執行或默認同意的改動。


## 核定改採內附 CLI 後的驗證

使用者已明確改採同一份 Desktop 內附 CLI。0.164.0-alpha.11.1 的獨立連線通過正常模型取消、縮短時限及故障收尾測試；三組指定執行邊界與各 11 項離線基線亦通過，詳見[計畫第 17 節](../plans/codex-coding-harness-pilot.plan.md#17-使用者核定內附-cli-與控制資格)。兩種 Desktop 人工路徑的失敗不被覆蓋，Desktop 驗收仍未通過。

原生取消／背景 terminal 管理重用[官方 App Server](https://learn.chatgpt.com/docs/app-server)能力。獨立 review 找到異常路徑漏清理 writer 的具體缺口，已補獨立所有權核對與收尾，並保存正向、負向與通訊故障注入結果。故障操作本身保留 unverified；另有 owner 直接查核與原 turn interrupted 的跨程序證據，兩者不混成「RPC 成功」。driver 僅作本輪評測控制，不新增通用 scheduler 或 runtime 元件。

首輪仍為流程 smoke，不能作公平能力優劣比較：全域 skills 未純淨隔離，答案讀取也未完整隔離。尚未開始三組模型 trial，不預告解題或效益結果。設定回應僅保留必要控制欄位；首次 A 錯誤 Maven 路徑的未啟動結果已保存，後續使用實際 PATH 並確認 XML test counts。


## 第一組回放揭露 grader 過度限制

A 的唯一 CLI trial 已完成，原始全模組測試90項全過。V1 外部驗收失敗後，獨立 Spec review 發現手動加入 internal post-processor 繞過公開 bean 啟用生命週期，錯誤拒絕由 Spring 管理 PP 的合法資源所有權方案。僅修正 bootstrap，不改行為斷言，升版 public-entry-v2；原方法與結果保留，不算 A 產品失敗。

V2 的 parent 仍失敗、reference／shared-scheduler／A固定交付均通過，13 tests各含2個lifecycle、0 skipped；A未重新啟動模型。新舊 A 驗收來源除了外加 grader 相同，獨立 review 已核對。進度及凍結紀錄缺口見計畫第18節；這個案例說明驗收依據與測試啟動方式也須檢查，不能把所有綠燈或失敗直接當產品結論。


## 首輪完成與收尾

三組各一次原生CLI流程smoke已完成，完整數據與限制集中於[交付報告](codex-coding-harness-smoke-20261024.research.md)。原V2外部13項三組皆過；交付後公開factory-close診斷只在B失敗，與凍結驗收分開保留。C有一次controller誤認子回合事件後的同trial續作，657.25秒含修復及等待，原上限未重設；真實事件串流回歸已補主回合歸屬。

0.164啟用／停用／更新／回退已獨立重查，0模型回合、全域設定不變；首次CLI覆寫引號錯誤的未載入紀錄保留。原工作60檔與git status未變、無trial writer，暫時來源與trust已清理；完整共同輸入及候選runtime已持久保留。首版僅列CLI受控試用，人工效益、公平比較、第二專案與Desktop Stop仍未證明，不將本輪升格為全面採用結論。
