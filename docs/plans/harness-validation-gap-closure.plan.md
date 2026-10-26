# Harness 驗證缺口補完計畫

日期：2026-10-25；範圍修訂：2026-10-26（Asia/Taipei）。**使用者已核准收斂為產品驗收。** 驗收目標為 `/Users/kengp3/Workspaces/mine/demo-002`，產品來源為 `/Users/kengp3/Workspaces/mine/simple-skills`。G00–G09 保留工作與證據追溯，完成門檻以最新[規格 S1](../specs/harness-validation-gap-closure.spec.md#s1-唯一驗收邊界與狀態)為準；G08 Windows 仍排除。

## Objective（目標）

完成三項產品改版、demo-002 最小日常端到端流程與必要失敗處理。先對帳既有直接證據，只補真正缺少的產品案例，再完成獨立審查。無可控介面的宿主故障注入、原生同事件重送及 Desktop 隔離驗收改列選配未驗證；本輪停止追加宿主研究與環境佈建。實作、驗證及安裝狀態繼續分開記錄。

## Background（背景）

- 0.3.0 的原 T01–T08 來源已實作並完成獨立審查，三項 P2 已修正；既有 A–G 案例不代表所有細分分支通過。原維護測試紀錄為 112 項、略過 Windows 1 項，其餘通過。
- 可用完整候選為 `/Users/kengp3/Workspaces/mine/simple-skills/dist/candidates/kengp3-harness-0.3.0`。manifest SHA-256：`7e37d77315faee550e3f2e1edc4b3a621da490f50ce4a8d937c78f9d71fbfd9e`。執行時仍須重新核對。
- 原本地 marketplace 仍指向 0.2.1。補驗使用指定候選與專用安裝來源，不能從舊入口推定已載入 0.3.0。
- demo-002 為獨立 Git 根、目前分支 `main`；已有 `.gitignore`、`AGENTS.md` 修改及未追蹤的 `.planning/README.md`。目前沒有根目錄 `project-setting.md`、`harness-project.json` 或 `.codex/`。這些只描述本次盤點，實作前重新核對。
- repo 外暫存專案已有真實驗收成功證據；demo-002 本輪接入及 V01–V07 補驗尚未執行。

## Materials（材料）

- [既有產品規格](../specs/unified-project-settings.spec.md)、[設定 ADR](../adr/0001-unified-project-settings.adr.md)、[任務合約用語](../specs/task-harness-glossary.spec.md)。
- [中央驗收](../research/unified-project-settings-acceptance.research.md)、[獨立審查](../research/unified-project-settings-review.research.md)、[隔離與獨立專案可行性研究](../research/unified-project-settings-gap-fixtures-feasibility.research.md)。
- [I/O 故障既有證據](../research/unified-project-settings-settings-faults.research.md)、[原生 Stop](../research/unified-project-settings-native-stop.research.md)、[模型生命週期](../research/unified-project-settings-model-lifecycle.research.md)。
- [demo-002 現行指示](/Users/kengp3/Workspaces/mine/demo-002/AGENTS.md:1)。以目前 source、tests、pom、README 與架構文件為準；`.planning/` 是歷史封存，不能恢復其中舊流程。
- [project-setting 通用設定方式](../../skills/project-setting/SKILL.md)、[task-harness 設定提供者規格](../../skills/task-harness/references/project-settings.md)、[模型規則](../../skills/task-harness/references/model-selection.md)、[移轉規則](../../skills/task-harness/references/settings-migration.md)。

## Boundaries（範圍與授權界線）

使用者已要求依 Matt 流程直到完成目標，並核准本工作圖與驗收邊界。後續僅在本地授權範圍內推進；規格與 tickets 存在不代表已安裝、已授信或已通過試驗。Windows 依最新明確指示排除，既有歷史 skip／限制保留，不計驗證通過。

- demo-002 原工作區供正常初始化、技能接入與無破壞性的驗收。kill、權限拒絕、刪檔與舊設定移轉使用自有可丟棄副本；不對既有應用程式資料或日常程序注入故障。
- 保留兩個 repo 的既有未提交內容，不重設、代為提交、搬移或清理。副本若從 Git 取得，須另外核對適用的未提交指示；不能把乾淨 checkout 說成完整複製現況。
- demo-002 缺少 project-setting 時，先由該技能初始化；一般驗收文件的路徑依其新規範確認，不借用產品 repo 的分類。本計畫與來源研究留在 simple-skills 既有規範位置。
- 以模型及原生宿主執行正常流程；Python 等控制器只屬維護者可選驗收工具，不加入產品必要依賴。參考既有 driver，保留歸檔原始檔，不建另一套通用框架。
- 不修改全域安裝、日常 auth/config、系統網路、防火牆或 managed policy；不建立外部服務，不發布 issue、push 或 PR。不自動切換舊 marketplace 入口。
- 不因本計畫先去安裝 Windows／VM／新宿主或修改 Codex 本體。缺少能力時記錄最小資格與阻礙；若必須擴大操作範圍，再提出具體方案。
- 使用者 Stop 有效。不得為了補記錄繼續操作；重啟或接手前查明舊 worker／程序與副作用，後續操作須有明確續作授權。

## Assumptions（規劃假設）

V01–V07 為補驗主線；D02 與 P02 是可信驗收的共同前置，P03／P04 納入收尾。D01 的日常安裝入口切換、P01 的 CI 自動化各列維護支線，互不阻擋真實行為補驗。具體 host、帳號模型、Desktop 與 Windows 資格由執行時查證，不預設已具備。

## 共用驗收方式

最高層驗收邊界沿用「明確啟用技能 → 原生宿主與模型執行 → 設定／合約／成果 → 讀回核對」。故障控制只放在要驗證的邊界。真實網路、事件重入或 provider 錯誤，必須取得對應層的直接證據。

既有中央驗收表作為狀態來源，不新增第二份長期 tracker。每個具名子情境記錄：實作狀態、驗證狀態（未執行／通過／失敗／部分／受阻）、候選指紋、宿主資格、原始證據、尚缺條件與下一步。受阻或部分不等於通過；必要項目仍受阻時，整體驗收保持未完成。欄位用於文件呈現，不更改產品設定格式。

開跑前須確認：

1. 正確的 project root、適用指示、候選指紋、實際 skills／hooks／plugin 來源與可寫範圍。獨立目錄仍可能受 HOME skills、system／managed 層或共享 daemon／Desktop state 影響。
2. 普通工具可正常啟動，預期的初態及故障注入前置條件確實成立。程序 exit 0 不是下一階段產物已完成的證明。
3. 每案全新 project／專用 state；認證留在版本控制與證據目錄外。V01 持久信任、同任務恢復及 V02 查回，在該案例內保留同一 state／原身分，直到案例結束才重設。

每案保存候選與環境資訊、prompt、原始事件／錯誤、可取得的 thread／turn／child／PID、前後快照與驗收判定。宿主不能提供的值標未知；timeout、模擬 payload、模型自述、driver 成功及證據 checker 均不能單獨證明目標行為通過。

## 工作包與依賴

以下保留原核准工作圖及試驗標準；2026-10-26 起，G05／G06 宿主專屬剩餘分支與 G07 為選配，必要產品門檻以中央 R1–R8 為準。G09 在必要產品證據與增量審查齊備後即可收尾，不再等候這些選配能力。

| ID | 交付 | 真正阻擋者 | 完成條件 |
| --- | --- | --- | --- |
| G00 | 拆開實作／驗收狀態，鎖定候選與環境盤點 | 無 | V01–V07 各細分項有獨立狀態；確認 demo-002 未提交內容基準與候選 manifest，缺少資格有明確紀錄 |
| G01 | demo-002 正常接入與最小成果驗收 | G00 | 初始化自身文件規範，按 provider 規格設定；核對實際載入 0.3.0，完成一個明確無破壞性任務、唯一合約及讀回，既有內容保留 |
| G02 | V04 真實移轉中斷與恢復 | G01 | 可丟棄副本中取得真實命令開始、OS signal、程序退出、檔案現況與同任務恢復證據；三門檻成立才刪舊檔，歷史產物與位置保留 |
| G03 | V01 正常持久信任 | G01、可用的正常人工審閱介面 | 無 bypass 地審閱精確 hook 定義；同 state 的兩次 invocation 均有信任狀態與實際提醒證據；project trust 與 hook trust 分開 |
| G04 | V07 strict 行為及 provider 負例資格 | G01、本帳號當下模型／強度資訊 | strict 範圍兩案取得真實派工或受阻證據；provider 負例按實際拒絕層判定，不把 schema／認證錯誤標為 upstream 拒絕 |
| G05 | V02 持久 child 查回與真正未知啟動能力確認 | G01、可觀測 child 及故障邊界 | 分別驗證 client transport 資訊遺失與原 worker 查回；真正主責 spawn 結果遺失及 provider 網路分支有各自直接證據，無注入能力者維持受阻 |
| G06 | V03 原生來源、重複提醒與同事件重入能力確認 | G01、可觀測事件來源 | startup／resume／compact 等實際來源及不重播成果有證據；只有可關聯同一邏輯事件的 native redelivery 才能關閉重入分支 |
| G07 | V05 Desktop 真實操作 | G01、可用的專用 Desktop 驗收環境與模型資格 | 實際停止按鈕及模型選單操作，畫面與 host 事件相互佐證；舊 worker 未重派、新繼承派工符合選擇 |
| G08 | V06 原生 Windows | 使用者明確排除 | 不執行、不計通過，不阻擋本輪驗收；保留取消原因及歷史限制 |
| G09 | 證據對帳、獨立審查與入口更新 | 各工作包已有明確結果或資格阻礙 | 中央表、tickets 與摘要一致，required findings 已修正；README 可直達當前證據；未通過分支保留待辦，不宣稱整體已驗收 |

建議先做 G00 → G01 → G02，建立完整隔離／中斷／恢復證據鏈，再做 G03 與 G04。G02–G07 通過 G01 後可按資格安排，彼此不是人為線性依賴；它們不得共用可變工作區或認證副本而互相干擾。G08 已排除。G09 可持續彙整；只有範圍內必要項目全通過時才結束整體驗收。

## 各分支的具體驗收與停止條件

### G02／V04：移轉中斷

- 在自有副本放置舊設定、歷史合約／收據與保留 canary，先記錄 bytes。由模型走正常移轉，不手填完成結果。
- 為命中窗口，可在驗收專用命令加入「已寫新設定、尚未刪舊設定」checkpoint；控制器須同時觀測 item/started、自有 PID/token 及磁碟現況，再對該程序施加一次 kill。
- 查明模型、原工具與子程序已退出後，才明確續作同任務；重新讀回三門檻並只完成剩餘操作。若原任務沒有合約，使用同一移轉對帳身分，不為測試另造重複活動合約。
- checkpoint 等待中被殺只證明 workflow 命令中斷，不宣稱命中 write／unlink syscall、斷電、原子寫入或交易回滾。未命中目標窗口保持未驗證。

### G03／V01：正常信任

- 不使用 trust bypass 或改寫信任資料庫。由人類透過正常介面審閱 exact candidate hook，保留來源、hash、trustStatus 與審閱紀錄。
- 同 state 重啟後核對信任保留及真正 developer 提醒；只有 enabled／已安裝不算通過。
- 若另測變更 hash 重新審閱，獨立列測試變體，不冒充未變更候選。人工審閱尚未完成時只阻擋該案例，其他工作繼續。

### G04／V07：強度與 provider

- strict 案一僅限制首選，允許清單後續候選使用各自強度；驗證實際選擇符合限制範圍。案二限制全部派工強度且無合格候選；受影響成果 blocked、無違規派工，無相依成果仍完成。
- provider 負例先找 protocol 可表達但模型 metadata 不支援的強度，以獨立唯讀驗收 probe 觀測一次請求結果；不要求產品模型故意違反正常 preflight。
- host 自動修正、schema 拒絕、模型不存在、認證錯誤與 provider 拒絕分開。無法抵達 upstream 的分支保持受阻，不修改宿主或引入必要代理換取通過。

### G05／V02：未知派工

- 用真實 persistent 唯讀 child 與唯一 case token 記錄 parent／child／合約，對自有 client transport 做受控中斷；重連後先核對原 worker、原 turn 終態與成果，不盲目重派。
- `thread/list` 須用正確來源過濾與分頁；idle／notLoaded 不等於工作完成。新 client、同 state 新 server、新主責 thread 分開記錄，不預設 worker 能跨 server 重啟繼續。
- 外層 RPC 或通知遺失不證明主責遺失 spawn 回應。真正 spawn 結果遺失須在模型接收結果的邊界有故障控制與旁證；provider 網路故障也不能用 client 斷線替代。缺少這些能力就停止相應試驗並保存精確阻礙，其他工作繼續。

### G06／V03：來源與重入

- 沿用同一任務與一次寫入 canary，分別取得真實 startup／resume／compact 的事件、提醒、合約與成果；新增事件不等於同事件 redelivery。
- 相同 payload、兩個 handler、再送一次 prompt 或直接回放 shell 都不足以關閉 native re-entry。若沒有可用宿主控制，該分支維持受阻；replay 只能作補充。
- 若研究 hook continuation，使用明確標記的驗收變體並保留來源紀錄；canonical passive Stop 不生成新授權。caller 提供的 trigger 分類也不取代人類授權證據。

### G07／V05 與 G08／V06：平台資格

- Desktop 停止案須實際命中已開始的無副作用等待命令，保存點擊、原生中斷及程序查核。不能為補記錄再送續作。
- Desktop 模型案須先啟動舊 worker，再以 UI 選擇本帳號可用模型；後續有授權回合的未指定派工，核對其新設定與舊 worker 身分。API 代測或單張截圖不足。
- Windows依最新指示排除，本輪不做資格探查、接入、commandWindows或最小任務，不代建VM；原歷史限制保留、不計passed。
- Desktop 若無法與日常 state、程序及設定分清，保留受阻；不以改全域安裝來解決隔離。

## 交付與維護支線

| 缺口 | 安排 | 結案條件 |
| --- | --- | --- |
| D02 實作／驗收狀態 | G00、G09 | 每個必要細分分支有獨立狀態與證據，done 不掩蓋受阻驗收 |
| P02 試跑前置檢查 | G01 起每案共用 | 普通工具、初態及階段產物未成立就停止該試跑，不把控制器問題混為產品結果 |
| P03 審查能力一致性 | G09 | metadata、指南、copied-skill／plugin 材料與實際能力一致；確定可比對者沿用既有測試 |
| P04 證據入口 | G09 | README 指向當前中央驗收、審查與候選說明，避免誤用歷史報告 |
| P01 自動化維護測試 | 獨立維護工作，不阻擋 G02–G08 | 最小本地 CI workflow 執行既有 unittest；先檢查 runner 需要的系統能力。真實模型、人工信任、Desktop／Windows 資格不冒充一般 CI 已覆蓋；remote 啟用另需授權 |
| D01 日常安裝入口 | 補驗結果與來源核對後的獨立交付決定 | 明確選定安裝範圍，核對載入 0.3.0；本地原入口／全域未切換時如實保留未完成。不以專用驗收 catalog 通過代表日常已升級 |

支線若修改程式，先以相應邊界建立失敗證據再修正，跑相關測試；產品、封裝或 canonical assets 變更後建立新候選，不覆寫原候選或回填舊證據指紋。只重驗受影響案例；平台資格未變且只有報告整理時不重跑昂貴模型試驗。

## Definition of Done（完成條件）

**本次規劃交付：** 此單一計畫已具備來源、範圍、依賴、逐項通過門檻及受阻處理，完成讀回與連結檢查；不代表實作或驗收完成。

**後續補驗完成：**

- [中央產品驗收表](../research/unified-project-settings-acceptance.research.md#產品驗收完成門檻)各必要項目均有真實證據及判定；合約 I/O 負例須補足。必要產品項目未通過時維持未完成。G05／G06 的宿主專屬剩餘分支及 G07 改列選配未驗證，不改判通過；原工作包表與詳細試驗門檻保留供追溯，不再代表每個分支皆為本次必要工作。
- 實作、驗證、平台資格及安裝狀態分開；D01／P01 是否完成獨立回報，不與 V 項目混算。
- 同一任務合約、原授權、Stop、無重複副作用及獨立審查條件保留；不明結果先查明，實際宿主無法提供的證據不編造。
- demo-002 原有修改、應用程式內容、無關 handlers、產品來源及全域狀態保留；清理只處理自有且已退出的試驗程序／目錄，不刪除待恢復 state。
- 完成來源與證據的獨立審查，修正 required findings；對變更執行相稱檢查，原始失敗與未驗證範圍持續可查。

## 建議執行流程

本計畫可先經 `/to-spec` 收斂成補驗規格，確認真實驗收邊界後，由 `/to-tickets` 提出依賴拆分供確認，再建立本地 tickets，最後以 `/implement-spec` 推進已核准的工作圖。本計畫沒有發布 issue 或建立可自動執行的 tickets；不重新開啟已完成的產品行為訪談，只有新增範圍或重大不可逆選擇才需要決策。
