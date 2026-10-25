# 統一專案設定：V01–V07 隔離情境可行性研究

最新範圍決策（2026-10-25）：使用者已核准以 demo-002 推進 G00–G09 補驗，並明確指示「不考慮 windows 情境」。因此 V06／G08 為明確排除，不執行、不計通過；以下 Windows 研究保留為歷史與能力說明。實作依[補驗規格](../specs/harness-validation-gap-closure.spec.md)與[核准計畫](../plans/harness-validation-gap-closure.plan.md)執行，其餘未驗證限制不因核准而消失。

2026-10-25（Asia/Taipei）。**結論：改用產品 repo 外的獨立驗收專案可行；使用者已指定既有 demo-002 為驗收目標。** 既有 `/private/tmp` 獨立 project 已成功完成真實驗收，足以支持此執行方式；demo-002 已完成唯讀現況盤點，尚未進行本輪 harness 安裝或試跑。換位置能減少產品 repo 的設定污染，不能自行補齊七項缺口：V01、V04 較適合直接補驗；V02、V03、V07 仍取決於宿主故障／事件邊界，V05、V06 仍需 Desktop UI／Windows 資格。以下均為研究與 Suggested 設計，**本次沒有建立專案或情境、啟動模型、操作信任、注入故障或關閉任何驗證缺口**。

## 範圍與目前依據

- 既有驗收明列正常信任、未知 child 啟動、native re-entry、真實移轉中斷、Desktop、Windows 與非法強度等限制，不能把既有 A–G 組別通過當成這些細項通過：[中央驗收第 46–63 行](/Users/kengp3/Workspaces/mine/simple-skills/docs/research/unified-project-settings-acceptance.research.md:46)。
- 本次直接執行唯讀 `codex --version`、`codex app-server --help`，得到 CLI `0.164.0`、`app-server --stdio`／WebSocket 等 transport 及 schema 產生子命令；未啟動 app-server。help 成功只證明介面列出，沒有驗證重連生命週期。現有 native driver 也以此版本取證：[模型生命週期第 9–12 行](/Users/kengp3/Workspaces/mine/simple-skills/docs/research/unified-project-settings-model-lifecycle.research.md:9)。
- task-harness 仍由模型依 Markdown、同一份合約及宿主原生能力執行。既有 Python driver／checker 可重用作**開發驗收選配**；不新增必要 runtime、dispatcher、MCP server 或外部服務：[模型規則第 3 行](/Users/kengp3/Workspaces/mine/simple-skills/skills/task-harness/references/model-selection.md:3)、[driver 第 1 行](/Users/kengp3/Workspaces/mine/simple-skills/docs/research/unified-project-settings-model-lifecycle-evidence/native-lifecycle.py:1)。

## 獨立專案方案：可行且較適合作為預設

**直接證據：** 既有 driver 在產品 repo 外 `/private/tmp` 建立彼此分開的 project／state，再從候選複製技能；不是只在產品 repo 新增子資料夾。[native-acceptance.py 第 63–69 行](/Users/kengp3/Workspaces/mine/simple-skills/docs/research/unified-project-settings-acceptance-evidence/native-acceptance.py:63)、[native-stop.py 第 120–130 行](/Users/kengp3/Workspaces/mine/simple-skills/docs/research/unified-project-settings-native-stop-evidence/native-stop.py:120)、[native-lifecycle.py 第 85–94 行](/Users/kengp3/Workspaces/mine/simple-skills/docs/research/unified-project-settings-model-lifecycle-evidence/native-lifecycle.py:85)。Stop 的實際事件 cwd 位於獨立暫存 project，取得真實 interrupted 後又以同合約完成續作；生命週期案例也取得同 thread 的兩個 completed 回合：[Stop 原始摘要第 5–20 行](/Users/kengp3/Workspaces/mine/simple-skills/docs/research/unified-project-settings-native-stop-evidence/summary.json:5)、[生命週期原始摘要第 4–52 行](/Users/kengp3/Workspaces/mine/simple-skills/docs/research/unified-project-settings-model-lifecycle-evidence/override/summary.json:4)。這支持「獨立暫存專案可跑通既有具名案例」，不代表 V01–V07 已跑通，也不證明固定長期 Git repo 的信任／Desktop／Windows 資格。

| 選項 | 主要取捨 | 本次判定 |
| --- | --- | --- |
| 產品 repo 外的專責驗收 Git 專案 | 方便版本控制情境與追蹤證據，明確區隔產品變更；仍需防止驗收專案自身設定污染 run | **採用方向**；使用者已指定 demo-002，本輪尚未安裝或實測 |
| repo 外、沒有 Git 的獨立暫存 root | 最小、易重設；需另歸檔來源與證據，且核對 project-root 發現及 CLI 非 repo 啟動限制 | **已有成功直接證據**；適合實際執行，非 Git 不等於無父層／全域來源 |
| 產品 Git worktree | 便於鎖定來源 revision、避免碰現有 working tree；會帶入該 revision 的產品 config、hooks、instructions | 可作候選來源／對照；**不推薦當乾淨驗收根**，獨立 checkout 不等於獨立設定 |
| 產品 repo 內子專案 | 材料管理省事；父 repo config／hooks／skills 發現與誤寫風險較高 | 保留為替代方案，須滿足下一節隔離門檻 |

移到產品 repo 外且有效 root 已核對後，可避開產品祖先路徑上的 `.codex`、AGENTS 及專案 skills／plugins 發現，也較容易把 writable roots 限於 run。仍須核對 `CODEX_HOME`、認證、HOME skills、system／managed 層與實際載入來源；獨立 Git root 不是全機隔離。daemon 需是此次自有程序／已核對 endpoint，不能因切換 cwd／state 就推論未連上既有 daemon；Desktop 也須另確認它實際使用的 workspace 與 state，不能假設繼承 shell 的 `CODEX_HOME`。[官方 root detection／config layers](https://learn.chatgpt.com/docs/config-file/config-advanced)、[App Server：transport／configuration](https://learn.chatgpt.com/docs/app-server)。

**Suggested 最小執行設計：** 不需要七個手工 repo、新框架或搬移產品。

1. 在一個專責驗收專案管理七個具名情境的任務、初態與預期；先確認該專案自己的 project-setting，受測 run 也自帶設定及唯一合約，不借用產品設定。
2. 只使用**已凍結 0.3.0 候選**的安裝／複製快照，核對 `runtime-manifest.json` 及逐檔 hash；本輪對照為 `7e37d77315faee550e3f2e1edc4b3a621da490f50ce4a8d937c78f9d71fbfd9e`。不以 symlink、產品 live working tree 或舊 marketplace 0.2.1 代替。候選暫存路徑失效時先取得同指紋來源，不自行換版。[既有 manifest 核對第 85–92 行](/Users/kengp3/Workspaces/mine/simple-skills/docs/research/unified-project-settings-model-lifecycle-evidence/native-lifecycle.py:85)。
3. 每個獨立 case/run 建立全新 project 根與 repo 外 0700 state、0600 必要認證；核對 effective config／skills／hooks allowlist 與 sandbox，才啟動一次最小工作。控制器為開發選配，產品流程仍由模型完成。
4. **重設以獨立案例為界。** V01 的兩次 invocation 必須保留同 state 驗證信任；同合約跨回合、V02 查回與 Stop／kill 後續作須保留該 case 的 project／state／原身分，查明舊 worker 及程序後才接續。不能在待恢復途中刪 state 或重建初態，再把新案通過稱恢復成功；真正 Stop 之後仍等待明確新授權。
5. 該 case 已取得終態、完成驗收及確認自有程序退出後，才歸檔去識別的事件、快照與指紋並清理；下一 case 全新重建。長期驗收 repo 與實際 run 互不依賴可寫來源；認證不入 Git／fixtures／證據。

**對 V01–V07 的影響：** V01 的獨立 trust state、V04 的自有程序／檔案控制最直接受益；V02 的持久 child 查回、V03 的來源觀測、V07 的 strict 模型行為也更容易排除產品設定干擾。真正 spawn 回應遺失、native 同 event redelivery、provider 實際非法強度拒絕仍需各自的宿主能力；Desktop UI／Windows 平台資格也完全不會因獨立 repo 而取得。各項完整限制與最小試驗見下節 V01–V07，驗證狀態維持未補驗。

## 已指定驗收目標：demo-002

使用者指定的根目錄為 `/Users/kengp3/Workspaces/mine/demo-002`；本次以 `git rev-parse --show-toplevel` 確認是該獨立 Git 根，分支為 `main`。它是已有應用程式及專案指示的工作區，不視為空白、可任意重設的測試目錄。

- 本次 `git status --short`：`.gitignore`、`AGENTS.md` 已有修改，`.planning/README.md` 未追蹤；全數保留，不代為提交、覆寫或清理。
- 根目錄目前沒有 `project-setting.md`、`harness-project.json` 或 `.codex/`；`.agents/` 僅見 `workflows/`。這是磁碟現況，不證明全域 skills／plugins 或宿主狀態不存在，也不代表缺少舊 JSON 的原專案適合直接測移轉。
- 已讀 [demo-002 的 AGENTS.md](/Users/kengp3/Workspaces/mine/demo-002/AGENTS.md:1)。其目前程式、tests、pom／README 與架構文件為依據，`.planning/` 為歷史封存，不從中恢復舊 workflow。應用程式本身的建置需求不轉成 task-harness 核心依賴。
- **Suggested 使用安排：** 原專案用於正常初始化、技能接入與實際專案任務驗收；強制中斷、權限拒絕、刪檔、舊設定移轉等故障案例，另取以此專案為基底的自有可丟棄副本，記錄來源及適用指示。不可直接重設原工作區；若使用 Git clone／worktree，須注意它不會自動包含目前未提交的指示與內容。
- 後續在 demo-002 寫驗收文件前，先由 project-setting 初始化該專案的文件規範，再依 task-harness 自帶規格設定；不借用 simple-skills 的文件分類。測試 state 仍獨立，V01／恢復等同案例跨回合保留所需 state，無關案例使用新環境。

本次僅在 simple-skills 更新此研究；未修改 demo-002 的任何檔案、建立副本、安裝技能或執行案例。指定目標不等於已完成環境資格或驗收。

## repo 內隔離的成立條件

目前 repo 的 [.codex/config.toml 第 1–2 行](/Users/kengp3/Workspaces/mine/simple-skills/.codex/config.toml:1) 啟用 hooks，[.codex/hooks.json 第 3–22 行](/Users/kengp3/Workspaces/mine/simple-skills/.codex/hooks.json:3) 有 SessionStart／SubagentStart 提醒；`.agents/plugins` 存在、`.agents/skills` 不存在。本次查過專案根及其父路徑、`docs/`、`docs/research/`，沒有讀到適用的磁碟 AGENTS／AGENTS.override；工作階段提供的 AGENTS 指示仍有效。這些是本次磁碟觀察，不能作未來情境的固定假設。

官方說明 project config 由 project root 到 cwd 累積，hooks 則跨來源累加；較近層不會取代較遠層 hooks。`CODEX_HOME` 分開 user state，不會因此證明父 repo 的 config、instructions、skills／plugins 都未載入。故**子資料夾不是天然隔離**；也不能只建立子層同名 hook 便宣稱覆蓋父層。[Advanced Configuration：project config／root detection](https://learn.chatgpt.com/docs/config-file/config-advanced)、[Hooks：來源合併](https://learn.chatgpt.com/docs/hooks)。

**Suggested 替代安排（仍選 repo 內時）：** 可版本控制的靜態材料放既有 `tests/fixtures/` 下，例如 `task-harness-gaps/{case}/`，各 case 自帶 project-setting.md、測試任務、初態與預期；實際 run 明確確認該 case 為測試專案根，使用獨有 project。認證與 runtime state 放 repo 外的專用 0700 目錄。若要求 run project 也在 repo 內，先以已查證的 root marker／`project_root_markers` 設定界定 case root。nested Git repo 可列候選，但不能只憑 `git init` 推論所有發現路徑已截斷；全域／managed 層仍須盤點。此為建議，未授權建目錄或新設定。既有 fixtures 的 `case.json`／`task.md`／`check.py` 是放置慣例參考，不代表其舊產品或合成事件適用本版。一般研究證據仍依根目錄規範放 `docs/research/`；若未來需要 ignored run project，須另明列新增 ignore 規則，不能假設 `.scratch` 已被忽略。

在任何真實試驗前，完成以下一次性資格核對即可；失敗時保留「隔離未成立」，不進入故障試驗：

1. 記錄 resolved case root、適用 project-setting／AGENTS、候選 manifest、實際 CLI／OS 與 sandbox writable roots；限制到 case，避免父 repo 成為可寫工作區。現有 Stop driver 已將 `runtimeWorkspaceRoots` 指向獨有 project：[第 96–99 行](/Users/kengp3/Workspaces/mine/simple-skills/docs/research/unified-project-settings-native-stop-evidence/native-stop.py:96)。
2. 用宿主唯讀列舉 effective config layers、hooks sourcePath／currentHash／trustStatus、skills／plugins 及 `instructionSources`，比對 allowlist；不能只看磁碟是否存在。skills/list 應 forceReload 核對 enabled 路徑，另留意 HOME 下 `.agents/skills` 與 system layers；不藉重設 HOME 或系統環境宣稱隔離。現有 schema 提供 [instructionSources／runtimeWorkspaceRoots，第 268–307 行](/Users/kengp3/Workspaces/mine/simple-skills/docs/research/unified-project-settings-host-capabilities-evidence/native-schema-excerpt.json:268) 與 [hook 來源及信任，第 734–780 行](/Users/kengp3/Workspaces/mine/simple-skills/docs/research/unified-project-settings-host-capabilities-evidence/native-schema-excerpt.json:734)。欄位不足以排除污染時，改到已核對的獨立根目錄，或保留未驗證。
3. repo 外 case 專用 state 以最小權限保存必要認證，不把認證／token 放入 fixture、Git 或歸檔；先定義自有程序清理及證據去識別方式。歷史 driver 含硬編碼 Darwin CLI／暫存候選路徑，只供參考或最小抽出成參數化維護入口，不改寫歸檔原檔、不視為跨平台可直接執行，也無需新測試框架：[native-acceptance.py 第 5–15、63–69 行](/Users/kengp3/Workspaces/mine/simple-skills/docs/research/unified-project-settings-acceptance-evidence/native-acceptance.py:5)。

## V01：正常持久 hook 信任

**可行性：可以在合格 case project／state 測試，但需要人類正常 review。** 既有試驗用了單次 bypass；它沒有覆蓋持久信任。[中央驗收第 31–34 行](/Users/kengp3/Workspaces/mine/simple-skills/docs/research/unified-project-settings-acceptance.research.md:31)。

**最小真實試驗：** 在沒有 bypass 的專用 CLI 互動工作階段，先分別記錄「專案層受信任」與「精確 hook 定義受信任」；由人類透過 `/hooks` 檢視來源、命令及 hash 並正常核准。完成一個小任務，退出後用**同一 state 的新 invocation** 再完成一個小任務；確認信任保留且固定提醒真正進入模型上下文。可另改一個僅屬 case 的無害定義，驗證新 hash 重新待 review；這是額外負向分支，不能改候選後仍稱 exact candidate。

**必要證據／可重用：** 前後 hooks/list 的 sourcePath、currentHash、trustStatus、正常 review 的 UI／文字紀錄、兩次 session 的真實 developer 提醒、各自 turn 終態及檔案保留指紋；重用 packaged-hooks 的記錄方式和候選資產。官方將信任綁定目前 hash，plugin 安裝不自動授信：[Hooks：Review and trust](https://learn.chatgpt.com/docs/hooks)。

**界線：** 不能寫 trust database、設 project trust 或加 bypass 取代人類 review；也不能把 hooks/list 的 enabled 當實際執行。managed policy 若禁止或強制 hook，保留該資格限制，不承諾其他帳號／Desktop 共用此信任。

## V02：child 啟動回應遺失、斷線與跨 session 查回

**可行性：repo 可承載持久 worker 及查回試驗；目前材料不足以保證能製造「主責模型遺失 spawn 回應」或 provider 網路故障。** 已有真實 worker handle／session／完成事件，但未做目標故障：[模型生命週期第 20–28 行](/Users/kengp3/Workspaces/mine/simple-skills/docs/research/unified-project-settings-model-lifecycle.research.md:20)、[中央驗收第 60 行](/Users/kengp3/Workspaces/mine/simple-skills/docs/research/unified-project-settings-acceptance.research.md:60)。

**最小分段試驗：** 先由真實主責建立 persistent 唯讀 worker，工作名稱帶 case token，保留 parent／child ID 與原合約。控制器在觀測真實 child start 後，只對自有 client transport 中斷／延遲交付，保留 server 端持續紀錄；新 client／session 使用同一 state，先查原 parent 與 child，再讀回原終態／成果，確認沒有第二個同工作 worker。`thread/read` 的 idle／notLoaded 不是工作完成，還要核對原 turn 的終態及 worker 結果。查不到就保存 unknown，不重派。原生 driver 的 persistent thread、RPC 保存及 session context 可重用：[native-lifecycle.py 第 14–55 行](/Users/kengp3/Workspaces/mine/simple-skills/docs/research/unified-project-settings-model-lifecycle-evidence/native-lifecycle.py:14)。官方可查 stored thread／turn／items；尋找 child 時須核對來源過濾，不能使用預設 interactive listing 就斷言沒有 child：[App Server：Threads](https://learn.chatgpt.com/docs/app-server)。

**必須拆開的結論：**

- 丟掉外層 `turn/start` 回應或 `subAgentActivity` 通知，只證明 client／observer 看不到；主責模型可能早已拿到 spawn handle。**不能據此關閉真正未知 child 啟動缺口。** 要關閉它，需宿主可在實際 spawn 結果交付主責前注入一次遺失，並另有可查原 child 的證據；目前 driver／本次官方核對未建立此能力。
- stdio 中斷、client 關閉或 WebSocket 斷線是 client↔app-server transport；不是 app-server↔provider 網路失敗。後者須另有僅影響自有程序／連線的可回復故障控制與原始 network error／時序；不改全機網路或新增必要代理。做不到就保留 provider 網路分支未驗證。
- 新連線、同 state 新 app-server、主責新 thread 是不同範圍，需分別標示；worker 跨 server 重啟仍可運作／查回並非既有證據已保證。WebSocket transport 可選不構成重連保證；官方目前將它列為 experimental。收不到回應與 timeout 都不是未啟動證明。[既有未知狀態處理規則第 71–81 行](/Users/kengp3/Workspaces/mine/simple-skills/skills/task-harness/references/model-selection.md:71)、[App Server：transport](https://learn.chatgpt.com/docs/app-server)。

## V03：相同 hook native re-entry 與輸入來源辨識

**可行性：可測真實不同來源與重複提醒的耐受性；無已核實的 native「重送同一事件」控制，完整 re-entry 仍有條件。** 本版 Stop 是被動 `{}`，既有公開測試直接執行兩次 Stop command，僅屬 replay：[package test 第 62–80 行](/Users/kengp3/Workspaces/mine/simple-skills/tests/test_harness_package.py:62)、[中央驗收第 61 行](/Users/kengp3/Workspaces/mine/simple-skills/docs/research/unified-project-settings-acceptance.research.md:61)。

**最小真實試驗：** 使用同一合約與一次寫入 canary，分別正常 startup、resume／compact 後明確授權續作，保存每次 native hook run、thread／turn、實際提醒與合約／ledger 指紋。如要研究 Stop 產生的 continuation，另設**驗收專用且有界**的 hook，保存實際 `stop_hook_active` 與來源控制；它改變了 hook 定義，只能證明宿主來源語意，不能冒充 canonical passive Stop 的產品能力。使用者真正 Stop 仍優先，後續只有明確新授權才能續作。

**辨識與限制：** 官方 SessionStart 有 `source`，UserPromptSubmit 只有該事件已公布的欄位；不能自行虛構通用 input-source 欄位。本機 `turnTrigger` 是 caller 提供的分類，不是獨立認證的人類授權：[schema 第 570–575 行](/Users/kengp3/Workspaces/mine/simple-skills/docs/research/unified-project-settings-host-capabilities-evidence/native-schema-excerpt.json:570)。外部控制器可保存輸入來源作核對；模型看不到時仍填未知，不能靠提示內容猜身分。[Hooks：SessionStart／UserPromptSubmit／Stop](https://learn.chatgpt.com/docs/hooks)。

**何時才能稱同 event re-entry：** 要有宿主提供的重入／redelivery 依據，能把兩次 invocation 關聯到原邏輯事件，再驗證沒有重播成果。相同 payload、相同 thread／turn、兩個同定義 handler、另一次 resume 或新 prompt 都不足以單獨成立。現有 hook started/completed schema 可留存 run：[第 579–617 行](/Users/kengp3/Workspaces/mine/simple-skills/docs/research/unified-project-settings-host-capabilities-evidence/native-schema-excerpt.json:579)；沒有可用重入機制時，僅把上述來源與 replay 分支標為已測，完整 native re-entry 保留未驗證。多主責競爭／原子 exactly-once 不加入本版承諾。

## V04：移轉命令執行中真實 kill

**可行性：可在 disposable case 的真實 OS 程序內驗證。** 既有新檔已寫的狀態是預置 fixture；讀回故障也在兩次 invocation 之間施加，均不是命令中 kill：[中央驗收第 62 行](/Users/kengp3/Workspaces/mine/simple-skills/docs/research/unified-project-settings-acceptance.research.md:62)、[I/O 報告第 27–29 行](/Users/kengp3/Workspaces/mine/simple-skills/docs/research/unified-project-settings-settings-faults.research.md:27)。

**最小真實試驗：** 使用 canary 舊設定／歷史合約／收據，由真實模型執行普通移轉。為可靠命中窗口，可在驗收專用工具命令內於「新設定已實際寫入、舊設定尚未刪除」加入可觀測 checkpoint 與短暫等待；控制器同時核對 native `item/started`、唯一 token／PID、檔案現況，對這個自有程序發送一次 OS kill。保存 signal／PID／工具結果及中斷後 bytes；確認舊執行者及子程序退出、阻止原模型繼續操作後，才由明確續作授權接續原合約，重新核對三門檻及歷史保留，完成剩餘步驟。

**證據／可重用：** 重用 I/O 案例的歷史 canary、hash 核對及 Stop driver 的精確工具／PID 辨識：[native-stop.py 第 15–49 行](/Users/kengp3/Workspaces/mine/simple-skills/docs/research/unified-project-settings-native-stop-evidence/native-stop.py:15)。完成條件是原命令確曾開始、kill 命中其存活窗口、現況讀回、同合約恢復與無重複移轉；不能以 marker 或 exit code 單獨判定。

**界線：** 插入等待屬受控時序，報告需明列；kill 命中 checkpoint 等待程序只能證明「移轉 workflow／工具命令仍在執行時中斷」，不能稱 write／unlink syscall 正在進行時 crash。若要證明完全未加 checkpoint 的自然命令被 kill，還要另取直接證據，可能因窗口太短而未命中。程序 kill 不證明斷電、寫入耐久性、任意 bytes 中斷、原子寫入或交易回滾。API interrupted 也不等於同步殺掉 shell，既有案例已觀測子程序短暫存活：[Stop 報告第 7–9、24–28 行](/Users/kengp3/Workspaces/mine/simple-skills/docs/research/unified-project-settings-native-stop.research.md:7)。

## V05：Desktop 停止按鈕與模型選單

**可行性：case 可放 repo，缺口須在目標 Desktop 的實際 UI 補驗。** 現有 API 中斷及模型切換沒有操作 UI：[Stop 報告第 39 行](/Users/kengp3/Workspaces/mine/simple-skills/docs/research/unified-project-settings-native-stop.research.md:39)、[模型生命週期第 45 行](/Users/kengp3/Workspaces/mine/simple-skills/docs/research/unified-project-settings-model-lifecycle.research.md:45)。

**最小真實試驗：** 在已確認只連到 case 的 Desktop chat，啟動無產品副作用的可觀測等待命令，實際點停止；保存點擊前後畫面、chat／turn、native 終態與程序查核，不為記錄而再送續作。模型選單另案：原 worker 已啟動後，用 UI 切換到本帳號實際可選的另一模型／強度；下一個有授權回合建立未指定模型的新 worker，核對舊 worker 未重啟、新 worker 的 host context 符合新選擇。

**證據／界線：** 重用既有 Stop canary 與 M2 的 old/new worker 設計：[M2 第 32–43 行](/Users/kengp3/Workspaces/mine/simple-skills/docs/research/unified-project-settings-model-lifecycle.research.md:32)。需要正確 Desktop build、可用 UI 控制及帳號模型資格；截圖只證明畫面選擇，仍需宿主事件／session context。桌面若共享日常 state 或無法取得直接證據，標為受阻／部分觀測；不能修改日常設定或把 API 代測當 UI 通過，也不能聲稱辨識 provider 內部權重。

## V06：Windows native

**可行性：可共享 repo 情境材料，不能由 macOS 子專案替代 Windows qualification。** 既有 package test 明確只跑 POSIX，Windows 另列：[test_harness_package.py 第 16、46 行](/Users/kengp3/Workspaces/mine/simple-skills/tests/test_harness_package.py:16)。

**最小真實試驗：** 在已具備 Codex、認證與合格 sandbox 的 Windows 主機，以該機 repo case／專用 state 開啟原生 CLI／PowerShell；正常 review hooks，實際執行候選 `commandWindows`、最小模型任務與讀回，保存 Windows build、CLI 版本、sandbox mode、命令／事件／檔案 bytes；Stop／恢復等細項依該平台可用控制另取證。路徑空白、換行與檔案保留可共用 canary 但須以 Windows 實測。產品資產確有 Windows 命令欄位：[canonical hooks 第 8–10 行](/Users/kengp3/Workspaces/mine/simple-skills/skills/task-harness/assets/codex-hooks.json:8)。

**外部資格／界線：** 原生 Windows sandbox 受 OS 能力與管理政策限制；部分模式需既有管理員設定。使用已配置的主機，未經授權不安裝／provision 或變更防火牆；官方資格應以現場狀態核對。[Windows sandbox](https://learn.chatgpt.com/docs/windows/windows-sandbox)。WSL、POSIX shell replay、mock Windows path 與一台機器的結果不能推廣成所有 Windows 環境通過。

## V07：provider 非法強度拒絕與 strict 限制

**可行性：strict 可做真實模型行為試驗；provider 拒絕只能有條件補驗。** 既有 effort-preflight 使用真實 metadata 並成功派出預設強度，strict 僅是政策輸入判讀：[中央驗收第 26、51 行](/Users/kengp3/Workspaces/mine/simple-skills/docs/research/unified-project-settings-acceptance.research.md:26)。

**最小分段試驗：** 先取得本帳號當下 model/list，選一個 protocol 可表達、該模型 metadata 不支援的強度。在**驗收控制器的獨立唯讀 probe**發一次原生請求，保存原始 request／error／turn 終態及實際可觀測來源；不要求產品模型故意違反正常 preflight。只有能證明 upstream 拒絕，才稱 provider 非法強度分支；若 host 先修正、schema 先拒絕、模型根本不可用或認證失敗，按實際層級記錄，不能強行標通過。既有 schema effort 是 ReasoningEffort 參照，隨便送不存在的字串可能只測到 protocol 層：[第 411–420 行](/Users/kengp3/Workspaces/mine/simple-skills/docs/research/unified-project-settings-host-capabilities-evidence/native-schema-excerpt.json:411)。可重用 [metadata probe 第 35–61 行](/Users/kengp3/Workspaces/mine/simple-skills/docs/research/unified-project-settings-acceptance-evidence/native-acceptance.py:35)；官方 metadata 依帳號／client 變動：[App Server：Models／Errors](https://learn.chatgpt.com/docs/app-server)。

strict 另以真實主責執行兩個小案例：一案只限制首選強度、後續候選允許另一強度；另一案限制所有 agent 只能指定強度且沒有合格候選。核對前者只使用符合範圍的後續候選，後者保存 blocked 與原因、無違規派工，無相依成果仍完成；兩案皆保留原設定與唯一合約。用宿主真正 child start／context 佐證，不能只交模型答案或預先填 observed 欄位。[現行模型規則第 75–89、99 行](/Users/kengp3/Workspaces/mine/simple-skills/skills/task-harness/references/model-selection.md:75)。

**界線：** 宿主若總在到 provider 之前合法修正／拒絕，就不能在不改宿主或服務的本次範圍內保證觸發 provider 拒絕；mock error 只測恢復策略。strict 成功可能表現為「沒有違規呼叫」，因此需保存完整派工紀錄、受影響條件與成果，不以缺少單一錯誤當成功。任何不明啟動仍先查明，不立刻試預設強度或改派。

## 建議採用與本次交付

**Suggested：採一個產品 repo 外的專責驗收專案管理情境，先以獨立 run 確認候選載入／來源隔離，再補 V01 與 V04；V05／V06 依平台資格，V02／V03／V07 先確認可觀測邊界。** 不為填滿矩陣製造假通過。每次只保留該次的 prompt、候選指紋、原始事件／錯誤、thread／turn／child／PID、前後快照與精確判定；`timeout`、driver exit 0、fixture 狀態或模型自述都不取代目標分支證據。既有 checker 只能核對已保存證據，不能替代真實試驗：[中央驗收第 65–74 行](/Users/kengp3/Workspaces/mine/simple-skills/docs/research/unified-project-settings-acceptance.research.md:65)。

本次研究唯一產物仍為本文件；依使用者追加問題原地補充獨立專案比較，未新增重複報告。依根目錄 project-setting 的 research 分類，首次建立前已確認目的地不存在；本次更新再讀規範及現檔，確認 `docs/`及 `docs/research/`不是符號連結且解析後位於已確認專案內，完成後讀回核對。未建立獨立專案、修改產品／設定／fixtures／歷史證據或既有未提交工作；未執行模型／故障／信任試驗、安裝、commit 或 remote 操作。新增設計均未實測，七項驗證狀態維持原限制。
