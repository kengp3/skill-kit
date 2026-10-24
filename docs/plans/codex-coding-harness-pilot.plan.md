# 個人 Harness 首版實作準備與試行計畫（Codex Coding）

日期：2026-10-24（Asia/Taipei）
狀態：N01–N03 P0 實作及整合驗收已通過，四項 review 修正已合併，兩軸複核通過（0待處理finding），見第 21 節與[P0 報告](../research/codex-harness-p0-20261024.research.md)。Desktop 為主要日常入口，CLI 為開發評測路徑；P1 及新的模型 trial 未執行，首輪既有結果與限制保留。
設計依據：[首版設計規格](../specs/codex-coding-harness.spec.md)

目前執行授權補充（P0）：使用者已核定依本修訂實作 N01–N03，套用 ask-matt／to-tickets／implement-spec，包含必要本機回歸與隔離 canary；不啟動新的模型 trial、不影響 Desktop 日常作業、不要求人工觀察。下文「本輪僅文件」保留為前一輪文件交付的歷史邊界，不限制此次 P0 授權；P1 及後續 trial 仍未授權。

## Objective

以 simple-skills 整個 repo 建置、整合與維護個人 harness，首版聚焦 Codex coding；先依能力缺口完成必要的 skills、hooks、工具及接入，再以 demo-002 的一個可重現真實 bug，確認三組配置可以在一致條件下執行、驗收與記錄。首輪已完成，後續先補強 CLI 開發評測，再分項驗證主要日常入口 Codex Desktop app，並在開發環境加入少量代表性案例。第二專案及其他宿主依採用需求後置。初始單案例只驗證試行方法，不足以判斷新版普遍優於其他配置；不要求使用者改用 CLI。

## Background

減少人工總投入仍是主要目標、打斷為次要目標，交付品質不得退步。最新 R04 決策取消人工計時、填表與觀察窗口要求；由機制整理可取得的證據，無法觀測的人工時間保留未知。A／B／C 用於開發階段比較，日常工作不承擔評測隔離或量測負擔。

候選新版允許必要的 skill、hook 與工具，並非單純提示詞比較；結果是整套配置的比較，不能聲稱單一元件的因果效果。

新版可跨本 repo 內的技能、共用工具、測試、Codex 接入及入口說明演進，不限定修改 task-harness，也不預設另建 coding-harness skill。B 組保留的是變更前完整快照，並非要求 repo 來源永遠維持舊架構。Repo 定位已確認；I01–I09 保留原首版責任基線，完成狀態見第 19 節；本輪待實作清單以第 20 節 N01–N07 為準。

## Materials

| 材料 | 用途與狀態 |
| --- | --- |
| [設計規格](../specs/codex-coding-harness.spec.md) | 已確認設計、能力邊界、驗收情境 |
| [研究報告](../research/coding-harness-best-practices-20261024.research.md) | 來源與歷史分析；舊版建議由最新設計決策取代 |
| [B 組固定快照](../research/codex-coding-harness-implementation-evidence/baseline-B/manifest.json)及[目前來源](../../skills/task-harness/SKILL.md) | B 已在修改相依內容前保存，執行時只讀快照；目前來源屬 C，不作 B 的可變輸入 |
| `/Users/kengp3/Workspaces/mine/simple-skills` | 個人 harness 的來源與整合 repo；可重用入口、工具及測試見第 1.3 節 |
| `/Users/kengp3/Workspaces/mine/demo-002` | 首輪來源專案，現有未提交內容保留 |
| `concurrent-request-scope` 模組 | 已有局部 unit tests；全模組也包含較重的測試，不能直接視為全部可獨立執行 |
| 修正 commit 與 parent | 下節列出精確 Git objects；案例資格的實際驗證與限制見第 11 節，Git objects 本身不是執行證據 |

## Boundaries

本輪只授權修改設計規格與本計畫、整理具體改動及一致性檢查；不修改 skill、hook、程式或設定，不執行測試／試行，不更新快取、不 commit／push／PR／部署。第 11–19 節是首輪已完成工作的歷史紀錄，不構成本輪繼續執行的授權。

首輪 A／B／C 各 1 次、各最多 15 分鐘、整次 trial 不補跑；保留組內修復、不購買 API 額度或付費資源。首輪已結束，此上限不是新增 trial 配額；新模型回放的次數、總資源上限及回饋政策須在後續執行授權內固定。

首輪因 Desktop Stop 未取得有效證據，使用者改採 Desktop 內附 CLI 執行；該歷史選擇只涵蓋首輪評測，不代表日常入口改為 CLI。最新定位是 Desktop 日常、CLI 開發評測。Desktop skills 日常使用與外部派送／限時取消 trial 分項驗證；取消缺口只阻擋相依操作，不等同所有 Desktop 功能失效。

隔離測試只在 harness 開發評測環境進行，禁止干擾日常全域設定、記憶、資料、既有對話／程序。優先程序內覆寫與獨立副本；不能先修改日常環境再以事後回復宣稱無影響。原 demo-002 及無關未提交內容保留。若無法確保不干擾，停止相依測試；不要求使用者反覆操作 Stop，也不接管日常工作作替代。

後續 repo 級補強範圍可涵蓋來源 skills、工具、測試與發佈說明，但須另依實作授權推進；本計畫不新增固定 hook、通用 runner 或日常隔離機制。

## Assumptions

- 首輪已固定的模型／reasoning／CLI 配置見第 19 節；下一輪需重新核對，不把舊證據當目前能力。
- 工具事件可提供足夠的證據歸屬；不足部分需依設計規格補足，不能手工編造結果。
- 首輪 V2 案例資格已有證據；需求、fixture、依賴或環境有相關變更時按影響重驗。Desktop 獨立且不干擾日常的測試方式仍是待驗證能力。
- 使用者對此專案的熟悉度由其選擇確認；不能由測試檔存在推論業務需求已完整。

## 1. 唯讀查證結果

本節保留實作前的唯讀盤點與當時缺口；不是目前完成狀態。後續案例資格、實體接入與仍未驗證部分統一見第 11 節及實作查核紀錄。

### 1.1 環境與模組

2026-10-24 定向查核：

- 模組 POM 沒有相依其他 demo-002 模組；使用 Spring、Servlet、Micrometer 等外部依賴。
- 局部 `ConcurrentRequestScopePropertiesTest`、`ConcurrentRequestScopeCreationTest` 可見 mock／直接建構的測試方式，已讀部分不需 DB／Redis。
- 全模組另有 Spring、load/performance、external HTTP PoC 測試，須分開選擇，避免把未知外部依賴帶入最小回放。
- 模組當時 `git status --short` 無輸出。整個 repo 仍有既有未提交變更；執行前重查並保存，不以本次快照當成永遠乾淨。
- 歷史 parent POM 使用 Java 25、preview 及 Mockito javaagent。唯讀版本命令回報 Temurin Java 25.0.1、Maven 3.9.10（Java 25.0.1）。**版本相符不代表依賴可解析或歷史測試可通過。**
- 前輪唯讀查核本機 CLI 為 codex-cli 0.164.0，含 hook 相關能力；這不證明桌面聊天使用相同 runtime，也不證明 hook 已載入或可阻擋。

### 1.2 真實 bug 候選：TTL cleaner 在 context shutdown 後的資源釋放

| 項目 | 證據／狀態 |
| --- | --- |
| Reference commit | `2967203c8e5c7aa1384762cf61db10c7a810cd9d` |
| Parent baseline | `172c69de58767e8fd8b0675513381eaea022585d` |
| 題名 | `fix(26-06): close ttl cleaner on context shutdown` |
| 變更 | 兩個 production files；加入 scope close 及 Spring disposal callback；沒有新增測試或需求文件 |
| 可見需求依據 | Commit 題名與 parent 建立 scheduled cleaner、缺少對應關閉路徑的程式結構 |
| 缺口 | 尚無已確認的獨立完整需求規格，也無穩定 fail→pass 證據 |

目前檔案僅供定位，精確歷史依據以以上 Git objects 為準：

- [Scope](../../../demo-002/concurrent-request-scope/src/main/java/com/example/concurrentrequestscope/ConcurrentRequestScope.java)
- [Spring 註冊](../../../demo-002/concurrent-request-scope/src/main/java/com/example/concurrentrequestscope/internal/ConcurrentRequestScopeBeanFactoryPostProcessor.java)
- [TTL 測試](../../../demo-002/concurrent-request-scope/src/test/java/com/example/concurrentrequestscope/ConcurrentRequestScopeTtlCleanupTest.java)

Parent 的 TTL cleanup tests 使用 manual clock 與不啟動 scheduled cleaner 的建構方式；它們可作相關回歸，不能驗證 context shutdown。既有 request completion disposal 測試也不等於 application context shutdown 驗收。

**建議的待資格驗證行為：**在隔離 JVM 建立啟用 TTL cleaner 的 Spring context，確認背景工作確實開始，再關閉 context，觀察其背景工作停止／資源在合理有界等待內釋放，同時保持原有清理功能。具體觀測方法與等待條件尚未定案，必須以外部 lifecycle 行為判斷，不強制採用 reference 的介面、私有欄位或 callback 寫法。

若需求依據不足、無法穩定重現，或只能以實作形狀判分，該候選不得升格為正式案例；另選有證據的真實 bug，不能改造缺陷後仍稱為原始歷史案例。

### 1.3 Repo 現況與可重用元件

以下來自本輪及同一討論中的唯讀檔案查核，只確認內容與入口存在，不代表新的組裝方式已通過測試。

| 現有來源 | 可重用內容 | 首版處置與限制 |
| --- | --- | --- |
| [README](../../README.md) | 現有技能入口及安裝說明 | 調整為 repo 級 harness 導覽，區分獨立 skill 與整套配置；現有技能安裝命令不直接當整套 harness 安裝方式 |
| [define-task](../../skills/define-task/SKILL.md) | 依歧義與返工成本選擇任務定義深度 | 供 M1 按需引用；不對每個任務強制完整 brief；若入口重整才同步改 metadata／引用 |
| [task-harness](../../skills/task-harness/SKILL.md) | 授權、依賴、證據、整合責任與未知結果核對 | 可改寫、整併或替換；不直接搬入固定 tracker 與密集 checkpoint；先保存 B 完整依賴快照 |
| [ai-code-review](../../skills/ai-code-review/SKILL.md) | 需求、影響分析與具證據的 findings | 風險觸發時按需使用；不將完整報告流程變成每次小修改的必經步驟；改共用契約時同步相關 references／tests |
| [project-setting](../../skills/project-setting/SKILL.md)及 [設定說明](../../skills/project-setting/references/configuration.md) | 文件位置、保留既有設定、提醒的啟停責任 | 保留單一規範來源；可重用接入經驗，不把提醒當強制控制 |
| [開發用 hooks](../../.codex/hooks.json)、[設定](../../.codex/config.toml) | Repo 目前的 SessionStart／SubagentStart 文件提醒與 hooks 開關 | 與可發佈設定分開；現況不證明 Desktop 已信任或必要操作已被攔截 |
| [run_check.py](../../skills/task-harness/scripts/run_check.py) | 單一程序的輸入、分流輸出、結果與指定來源前後指紋 | 原生證據不足才考慮使用；目前無 timeout／持久程序追蹤，不直接當通用執行器。需要移到共用位置時同步所有引用與測試，B 仍使用舊快照 |
| [project-setting 測試](../../tests/test_project_setting.py)與既有 review 測試 | 既有測試風格及局部回歸 | 僅重跑受改動影響部分；不能拿舊 tracker 形狀作新版契約，也不以舊通過紀錄當新版驗收 |
| [demo-002 指示](../../../demo-002/AGENTS.md)、POM 與局部 tests | 專案必要 review、建置與驗證入口 | 共用於三組；保留未提交內容，實際命令按受測 revision 核對。既有 TTL tests 不取代 lifecycle grader |

現有 source layout 可作起點，沒有證據要求先搬動整個目錄樹。新增共用位置只在確有多個使用者或發佈需求時建立；首版不新增一般化插件框架或自製套件管理器。

## 2. 三組配置與共同基線

| 組別 | 配置 | 固定要求 |
| --- | --- | --- |
| A | 同宿主原生流程，不載入 B/C 額外 harness 配置 | 保留必要宿主／專案規則與驗收要求 |
| B | 同宿主＋現行 task-harness 與完整相依資源的固定快照 | 不為配合新版修改快照；不讀後續被 C 改動的 repo 來源 |
| C | 同宿主＋本 repo 產出的新版發佈配置，包括實際啟用的 skills／hooks／工具／設定 | 記錄完整 runtime 依賴及版本；不把整個 repo、研究或答案資料自動載入 |

共同固定：模型精確識別與 reasoning 設定、宿主、初始程式與相關設定、任務提示、可見測試、驗收標準、工具與網路政策、CPU／RAM、JDK／Maven／依賴狀態、最大資源、外部驗收回饋與整次 trial 補跑政策。額外 reviewer、worker、hook 所執行的檢查與重試都計入總用量。

各組內部的診斷、修復與工具重試策略屬於比較對象，保留差異並記錄成本，不為統一策略而修改 A/B。共同的外部上限不限制每組在上限內如何取得診斷進展；工具重試、外部 grader 回饋後的修復與重新開始整次 trial 須分別記錄，不能混成同一重試次數。

原生／現行／新版對工具的使用方式可以不同；可用外部資源與授權須一致。若特定新工具本身就是 C 的變更，明列為配置差異，不能稱為純指引比較。

先盤點 B 的 skill、metadata、references、工具及其外部相依，再保存可重現的內容與載入方式，包含相關未提交檔案。之後 repo 的現行來源可重構，B 的 manifest 及實際內容不變。C 的版本由實際發佈配置與內容指紋識別，不能只依 repo HEAD；發佈配置排除 grader、reference 答案及不需要的歷史紀錄。

**配置隔離必須查實際載入內容。** 同一聊天或同一工作目錄切換文字標籤不足以隔離。每次使用新上下文與獨立工作副本；公平比較須確認 A 不殘留 B/C 的 skill、hook 或快取設定，B 不殘留 C。必要既有控制不可移除。若桌面／個人全域設定無法隔離，在實際配置與限制可辨識且符合第 4 節 smoke 門檻時，僅能檢查流程；不得把受污染配置當成純 A/B/C 基準，公平比較須先處理環境。

## 3. 答案、工作內容與副作用隔離

以下原工作保護、副作用限制與驗收完整性適用於所有回放；答案讀取與組間配置隔離則是公平比較的額外資格。隔離不足的 smoke 仍須揭露實際配置、可能洩漏的答案與結論限制，不得讓受測 agent 改寫外部 grader 或評分標準。

1. 保存原 checkout 的 HEAD、tracked diff 與必要 untracked 內容清單；不 reset、stash 或覆寫現有工作。
2. 回放使用固定歷史 parent 的獨立副本，不把目前 dirty 工作混進歷史案例。必要環境修補若不可避免，先記錄為共同 fixture，再對三組一致使用。
3. 公平比較時，reference commit、grader、本計畫及含解法的聊天內容，只能由案例維護者／外部驗收端讀取。受測 agent 使用新上下文，不繼承本對話。
4. Parent checkout 若仍帶完整 Git history，agent 可直接讀後續修正；公平比較因此需隔離後續 Git objects、remote 與其他可讀副本。單用 worktree 或「請勿查看」不等於答案保護。
5. 使用可限制實際讀取範圍的執行環境，避免從來源 repo、聊天紀錄或網路找回答案。若無此能力，明列洩漏風險，結果只能視為流程 smoke，不能當公平解題能力比較。
6. 各組使用一致可見需求與開發測試；外部 grader 在 agent 結束後驗收其產物。若提供修復回饋，固定可見資訊與次數政策，且不得揭露 reference 解法。
7. 各次執行隔離暫存、程序、port、cache 及外部狀態；依賴 cache 的冷／熱狀態保持一致或記錄。禁止真實外部寫入，除非另有明確試驗授權。

本計畫本身包含答案線索，公平比較時不能放進受測 agent 的可讀 workspace；smoke 若無法排除可讀性，須記錄洩漏風險。案例來源為公開／既有程式時仍可能有模型預訓練污染，限制應保留於結果中。

## 4. 分階段步驟與進入條件

以下保留首版階段定義，首輪最終結果見第 19 節；本輪補強順序見第 20 節。依明列的依賴條件推進，不把階段編號視為所有工作必須串行；不要求為每一步新增 tracker。

### 4.1 首版具體改動清單

M1–M5 沿用規格的模組名稱；G01–G07 對應第 9 節能力缺口。下表保留設計基線的實作責任；已落地檔案與限制見第 19 節；後續具體待改檔案見第 20 節。既有位置以連結為準；未定的發佈／hook 落點在 P1 選定宿主原生方式後才固定，不以預造目錄決定架構。

| ID／模組 | 預計改動與受影響位置 | 重用／新增與依賴 | 最小完成證據 |
| --- | --- | --- | --- |
| I01 導覽與使用契約／跨模組 | 更新 README 的 repo 定位、能力入口、完整配置與單 skill 使用差異；同步受影響文件連結 | 修改既有入口；依 I02–I04 的實際選擇完成說明，不先更名 repo 或大量搬檔 | 使用者能找到啟用、版本、停用及回退方式；未把未驗證機制寫成可用 |
| I02 開發流程／M1 | 精簡 task-harness 或整併為新的工作流程入口；按需連接 define-task、review 與 bug／功能／重構指引；同步實際受影響的 SKILL、metadata、references | 重用有效行為；允許新增、替換或重新命名，無需永久維護兩份核心規則；先完成 B 快照 | 小任務沒有多餘 tracker／角色；風險驗證、進展修復、結果不明及交付契約均保留 |
| I03 Codex 發佈與採用／M3 | 建立可辨識的 runtime 內容清單、專案 opt-in、版本及啟停／回退流程；處理必要的套件描述及 hook 接入 | 依 G01/G04 優先原生格式；新增缺少的組裝資料。Repo 開發用 .codex 設定與對外發佈分開，保留既有提醒 | 可核對載入版本及完整依賴；未啟用專案不受影響；更新及回退有效，研究／答案不入 runtime |
| I04 專案資料／M4 | 定義最小接入資料及 demo-002 範例：既有指示來源、針對性命令、觀測入口、必要條件及允許副作用 | 重用專案指示與 POM；原生設定足夠就不新增獨立 profile。範例隨共用配置維護，實際試用設定只寫入獲准的隔離副本 | 不覆蓋專案原規則；動態狀態即時取得；未知命令不被當成已驗證 |
| I05 可靠控制／M2 | 依實際操作建立必要控制清單：依據、條件、執行者、覆蓋路徑、失效處置；補既有宿主／專案關卡沒有覆蓋的可靠檢查 | G02 逐條判定；必要且可判定的缺口才新增 hook／工具，提醒仍標提醒 | 必要控制失效停止相依操作；既有控制完整時可零新增 hook，但不能省略覆蓋證據 |
| I06 證據與恢復／M2 | 接入原生最終結果與產物歸屬；不足時重用或調整 run_check，必要才新增最小保存／核對工具 | 依 G03；不預設新 runner，不默默新增語言 runtime。移動 helper 時同步呼叫端及封裝依賴 | 證據可取回且對應目前內容；逾時／失聯不被視為可直接重試，缺結果不算完成 |
| I07 Harness 回歸／M1–M4 | 在現有 tests 下增加必要的配置、啟停／回退、控制失效、過期證據、未知結果與小任務行為案例；回歸受影響既有能力 | 重用現有測試慣例與可用案例素材；不把所有歷史 PoC 納入每次必跑 | 按風險選取的情境有直接證據；發佈配置離開開發 checkout 仍具完整 runtime 依賴 |
| I08 真實案例與外部驗收／M5 | 新增固定需求、parent/reference 指紋、開發材料與 lifecycle grader；置於評測用 fixture／資料，與 runtime 發佈分開 | 重用 demo-002 歷史程式及相關 tests；依 G06 資格、G05 隔離結果選定執行位置；不修改原 checkout | 穩定 fail→pass，接受其他合法解法；grader 不由受測 agent 改寫 |
| I09 成本與回放紀錄／M5 | 自動整理最小 manifest、原生事件與來源參照，記載全部結果、交付、求助、重試及修復；人工時間未知保留缺值 | 原生事件與既有範本優先；不要求人工計時、填表或觀察，不另建監控服務 | 原始事件與判讀分開；等待不算人工時間；失敗／缺值保留；共同上限與回饋政策可追溯 |

首版不以檔案數作完成條件。可由原生能力滿足的 I03/I05/I06，仍需整合與驗證，無須為表格每列製作新程式。所有會影響 B 依賴的 repo 改動都在保存 B 快照之後；所有必要控制在相依操作之前成立。

### 4.2 進入門檻與階段依賴

| 用途 | 進入門檻 | 可作結論 |
| --- | --- | --- |
| 流程 smoke | 原工作受保護；相依操作的必要控制有效；真實案例資格通過；實際配置與固定輸入可辨識，具備可執行驗收及結果取回能力 | 方法能否運作及本案例觀察；配置或答案隔離不足時明示限制，不判斷能力優劣 |
| 公平解題能力比較 | 全部 smoke 條件，加上合格的配置與答案隔離，以及一致的外部限制與驗收回饋政策 | 在既定案例與條件內比較；仍不得以單案例宣稱普遍優勢 |

必要控制能力不足時，兩種用途都停止相依操作，只有經驗證的等效控制可替代；不得降為建議或以事後 CI 取代副作用前的控制。配置／答案隔離不足屬於比較有效性缺口，不放寬必要控制，也不代表所有準備工作必須停止。

| 階段 | 工作 | 完成證據／停止條件 |
| --- | --- | --- |
| P0：確認比較原則 | 依當前授權確定兩個 repo 的角色、寫入位置、宿主、模型、實際限制及原工作保存方式；修改任何 B 依賴前保留完整快照 | 可取回的準備紀錄與 B 依賴清單；不要求尚未建置的 C 已凍結內容 |
| P1：宿主能力查核 | 依 G01–G05 查明接入、控制、證據、發佈及隔離能力，配合 G07 固定當階段限制；先唯讀，必要時另在獲准環境探測 | I03–I06 的實際新增／重用清單與缺口；不等同候選已驗收；必要控制不足停止相依操作 |
| P2：案例資格 | I08 依 G06 釐清 lifecycle 需求並在 parent/reference 驗證；檢查既有正常行為 | 穩定 fail→pass、沒有僅匹配 reference 形狀的判定；未合格不得進入 P4 或公平比較 |
| P3：候選建置、驗證與配置凍結 | 完成 I02–I06 的最小可用組裝，以 I07 驗證；同步 I01 說明及 I09 紀錄，再凍結三組實際配置及共同輸入 | 完整 runtime 清單、啟停／回退及失效證據、已凍結 manifest；依兩種門檻標示用途資格，不以檔案存在宣告就緒 |
| P4：三組流程 smoke | P0、P2、P3 已完成且符合 smoke 門檻後，在固定順序政策與獨立工作副本執行首個 bug 回放 | 保留全部結果與隔離限制；確認流程可運作及結果可判讀，不在此宣告能力優劣 |
| P5：可靠性與擴樣 | 在開發測試環境按變更影響回放少量 bug／功能／重構案例；只有作公平比較時才須另取得配置與答案隔離資格 | 依類型報告正確性與不必要流程負擔；案例與配置另立版本，舊 smoke 不升格為公平比較 |
| P6：採用與移植 | 依需求確認 Desktop 適用性及後續第二專案／其他宿主；證據使用可取得的原生結果，不要求人工觀察 | Desktop 為近期主要入口；其他移植後置；缺少人工時間不宣稱省時，未驗證第二專案不宣稱通用 |

候選的依賴順序是 P1 宿主能力查核 → P3 建置 → 候選實際驗證 → 凍結三組配置 → P4。P2 可與 P1／P3 不相依的工作分開進行，但案例及驗收須在 P3 最終凍結前合格。P0 只固定比較原則，不預先要求候選內容或驗收證據。公平比較須在執行前另完成配置與答案隔離；只做 smoke 不必為此先建完整隔離環境，但必要控制不可省略。實作以使用者後續授權推進；階段門檻仍須逐項完成。

P3 內以可驗收行為整合：先讓 I02/I04 能形成任務與驗收契約，再讓 I03/I05/I06 提供實際採用、執行控制與證據；每個行為切片同步補對應 I07 檢查，最後完成 I01 導覽、I09 紀錄及發佈驗收。這不是要求所有 skills 寫完才處理 hooks；控制依賴優先，I08 案例準備可獨立推進。

### 4.3 命令候選（僅供後續核對，未執行）

在隔離副本中，可先核對下列現有局部測試入口：

```sh
mvn test -pl concurrent-request-scope -am \
  -Dtest=ConcurrentRequestScopePropertiesTest,ConcurrentRequestScopeCreationTest \
  -Dsurefire.failIfNoSpecifiedTests=false
```

這不是 lifecycle bug 的驗收命令。執行前須確認指定 revision 是否有這些測試、實際 test count 與選取結果；`failIfNoSpecifiedTests=false` 可能使零測試模組不報錯，因此不可只讀整體 exit code 判定所需測試已執行。新 bug grader 的命令待資格驗證時產生，不能先填為通過。

## 5. 回放資格與判定標準

### 案例資格

- 行為需求可理解且可追溯；隱藏測試不得要求提示、契約與專案材料無法推得的額外行為。
- 資格依案例類型判定，不把 bug 的失敗基線套到所有任務：

| 類型 | 最小資格／驗收 |
| --- | --- |
| Bug | 未修改的缺陷基線能重現目標問題，已知正確修正通過，相關正常行為維持；歷史真實 bug 保留 parent／reference 來源 |
| 功能 | 新增契約、必要失敗處理及既有行為有可觀察預期；未實現新增契約能被辨識，不要求存在歷史缺陷與修正 commit |
| 重構 | 修改前後符合已確認外部契約，並確認要求的結構調整；修改前測試通過是正常情況，不製造失敗基線 |

背景排程與 shutdown 的 race／等待穩定性只在相關案例檢查。各類型均檢查 grader 是否誤判，按風險用已知結果或最小判別案例驗證，不一律新增完整替代實作。

- 無關正常行為仍受檢查；其他合法解法不能因未採用 reference API 而被拒絕。
- 實際案例能在隔離環境執行；執行失敗、測試本身瑕疵與程式缺陷分開記錄。
- 資格尚未通過時標為「待驗證」，不算 agent 失敗或成功。
- 新增 grader 或需求、fixture、依賴、執行環境有相關變更時按影響重驗；使用公開入口並按上述類型核對已知結果，有實作耦合風險時再檢查合法替代解法。
- 保留 grader 與相關輸入版本及資格證據；未受影響部分可重用，不要求每次 trial 全套重驗。checker 缺陷升版後重評所有受影響的固定產物，不自動重跑 agent；原產物及結果不覆寫。

### 每次 trial 的三種結果

| 維度 | 檢查 |
| --- | --- |
| 成果 | 對應類型的目標是否達成：bug 修正、新增功能契約或重構要求；相關回歸與整合通過、必要條件有證據 |
| 行為 | 是否讀取必要現況、依據可追溯、未偽報完成、未越界、未盲目重試未知副作用 |
| 品質 | 是否過度實作、破壞相容性或留下重大可維護性問題；依具體準則，不單用 LLM 分數 |

任務成果必須由對應類型的外部驗收確認，agent 最後說「完成」不是分數。人工或 LLM 輔助 review 的爭議需保留證據，LLM reviewer 不取代必要可執行檢查。

基礎設施錯誤、時間／用量上限、不可判定結果另列；保留原始嘗試。若需補跑，先定義補跑政策並保留補跑前結果，不能刪失敗只留下最好的一次。

### 執行數量與上限

首輪已按各一次／最多 900 秒／整次不補跑完成。後續新模型回放尚未核定次數或資源預算；開始前依後續授權固定，所有 workers／reviewers 計入，順序政策與外部回饋一致。未預先固定的自適應加跑只能列探索結果，不沿用首輪授權無限擴樣。僅重放歷史事件或重評固定產物與新模型 trial 分開記錄。

## 6. 自動證據與成本限制

R04 取代人工計時、填表、少量實測及 7／14 天返工觀察窗口提案。由 agent 重用原生事件與現有產物，自動整理；不新增日常監控、人工核准或要求使用者補資料。

| 記錄 | 必要內容 |
| --- | --- |
| Run manifest | task/trial/config ID、需求／grader 版本、來源指紋、宿主／模型／元件版本、限制與工具政策 |
| 配置證據 | 實際啟用／信任與快取版本；開發比較才核對共同可見材料與其他組排除條件 |
| 執行證據 | thread／turn／operation 歸屬、原始結果參照、產物身分、取消／續作與原期限；重複事件去重 |
| 驗收與修復 | 驗收狀態、checker／產品／環境缺陷分類、重試與修復、人工接手可見事件；保留所有嘗試 |
| 打斷 | 可確認必須由人類處理才能推進的事件，純進度通知不計；資料覆蓋範圍與未知歸屬明示 |
| 人工時間 | 無可靠來源則 unavailable；不以訊息間隔、agent wall-clock、token 或求助次數推算，不要求補填 |
| 其他成本 | 可取得的用量、wall-clock、設定／維護及離線評測成本另列；缺值不填零，避免重複計算 |

每個摘要均保留原始來源，區分直接事件、推導統計與 agent 判讀。後續已有修復證據可關聯原任務；不能僅因相同檔案再次變更就認定返工。沒有觀察到不等於沒有缺陷／返工；不建立需使用者持續觀察的窗口。

未完成、人工接手、受阻、取消與驗收未過並列，不因後來修復而改寫原 trial。自動統計屬輔助能力，失效明示後可繼續；必要驗收證據缺失仍不得完成。品質及可觀測流程指標可供診斷，但未取得可靠可比的人工時間前不能宣稱人工省時。

## 7. 回歸與採用規則

- 評測期間固定任務、可見材料與 grader。checker 缺陷修正後升版，重評所有受影響固定產物，保留原結果，不自動重跑 agent 或只重評有利組。
- 先用開發案例診斷 C；保留沒有用來修改 C 的題目驗證。首個已深入調查的 bug 只能算開發／smoke 案例，不能冒稱 held-out。
- 局部指引改變跑相關案例；模型、宿主、核心工具／控制改變時擴大回歸。任務成果與關鍵行為均應保留。
- 在開發測試環境加入少量簡單 bug、小功能、局部重構；agent 整理不必要澄清、文件、委派與重複驗證的證據，依風險判讀，不設固定工具次數。所有回放不得干擾日常作業。
- 交付品質先滿足；只比較資料來源與可見範圍相容的指標。人工時間缺值時不宣稱省時，不為填滿資料要求人工觀察。必要品質不以時間節省抵銷，提早受阻或放棄不算省時。
- 結果依任務類型與每組全部嘗試呈現，不只報最佳一次或只算成功樣本。
- 若新版只有某類任務受益，採情境式啟用；若無可辨識收益，修正或移除增加負擔的機制。
- 初期不設定來源未支持的改善百分比門檻，也不從一個案例做顯著性或跨專案推論。

## 8. Definition of Done

### 本次計畫完成

- 本輪 R01–R07 與規格一致；第 20 節列出具體待改檔案、重用／新增、優先序、執行依賴、能力缺口及最小驗證；只修改兩份文件。
- Desktop 為主要日常入口、CLI 為開發評測路徑；不干擾日常、不要求人工觀察、grader 按影響重驗及不自動重跑 agent 均有可檢查條件。
- Repo 定位、M1–M5 責任、I01–I09 改動／重用／驗收及 G01–G07 能力缺口可對照；三組定義、候選資格、控制變因、隔離、證據與量測明確。
- 已知／建議／待驗證分開；沒有把歷史 commit 或版本輸出當作回放成功。
- 與設計規格一致，保留原工作、授權與未知副作用邊界。

### 首次三組 smoke 完成條件（已執行；結果見第 19 節）

- P0 比較原則、P1 必要宿主能力、P2 案例資格及 P3 候選驗證／配置凍結已有證據；包括案例需求與穩定 fail→pass，並符合流程 smoke 門檻。
- 三組各有可辨識的實際配置、獨立初始狀態、完整執行結果與外部驗收，並列交付狀態與人工時間；B 從固定快照執行，C 的 runtime 依賴完整且不依靠開發 checkout 的隱藏檔案。
- 失敗／無結果／受污染情形如實保留；原 checkout 與無關內容未被修改。
- 報告結論限於方法是否可用與本案例觀察，明列下一個最有價值的調整。
- 配置或答案隔離未合格不單獨阻擋 smoke 完成，但須明示限制；公平解題能力比較須另通過兩項隔離資格，不能沿用受污染結果作能力優劣證據。

## 9. 未決清單與解除方式

下表保留初次查核的 G01–G07 索引與當時缺口，不作目前狀態；第 19 節是首輪結果，第 20.4 節是本輪剩餘能力與最小驗證。這些缺口不阻擋本次文件交付，但限制後續實作保證或試行。檔案存在、過去報告與 CLI 版本皆不能代替實際 Desktop 或新發佈配置的驗收。

| ID／能力缺口 | 現有證據與最小解除方式 | 影響／失敗處置 |
| --- | --- | --- |
| G01 宿主載入與信任 | 已有 repo hook/config；先唯讀核對 Desktop 的有效來源、版本與信任，再於獲准環境確認實際載入 | 決定 I03 的接入方式；未確認不宣稱已啟用，不以 CLI 代替 Desktop |
| G02 必要控制覆蓋 | 現有 hook 是提醒；先盤點每條必要條件及既有執行者，再對預定事件、工具路徑、逾時、錯誤與未信任情境實測 | 決定 I05 新增量；本控制未有效且無經驗證的等效控制，即停止相依操作 |
| G03 證據取回與產物歸屬 | 原生工具結果與 helper 可作材料；核對跨 session 取回、最終結果及相關 dirty content 的綁定，必要時測試中斷恢復 | 決定 I06 是否新增工具；必要證據缺失不完成；未知結果先核對 |
| G04 發佈依賴、啟停與回退 | 已有 skills 來源及安裝說明，尚無本候選的完整驗收；先定 runtime 依賴與原生封裝，再檢查安裝快取、有效版本、啟停／回退及離開開發 checkout 的可用性 | 決定 I03 的套件格式與實體落點；阻擋相關發佈完成聲明，不預建套件管理器 |
| G05 配置與答案隔離 | 查有效配置、完整 Git objects、其他副本與聊天內容可讀性；保護 grader 不可被受測 agent 修改 | 影響 I08 與公平比較；不足時僅能在必要控制及 smoke 門檻成立下檢查流程 |
| G06 真實案例資格 | 查 lifecycle 原始 issue／契約，必要時請使用者決定具體行為；後續在隔離 JVM 驗證 parent/reference、正常行為與穩定性 | I08 未合格即阻擋 smoke 與公平比較；不得以合成缺陷冒充歷史案例 |
| G07 限制與量測 | 查實際模型與可取回用量；固定當階段時間／成本／次數、外部回饋及補跑政策，對尚未授權額度取得決定；R04 已取消人工返工窗口，改為自動證據及觀測範圍 | I09 缺值明示；缺當階段必要限制就不開始，不要求人工計時、填表或持續觀察 |

## 10. 來源

- 設計與平台來源集中於 [設計規格](../specs/codex-coding-harness.spec.md)，查閱截止 2026-10-24。
- 本地來源：demo-002 的 root／module POM、上述 production/test files 與固定 Git objects；相關 README 只作入口參考，不能代替執行結果。
- Repo 來源：第 1.3 節列出的現行 skills、helper、設定、README 與測試。既有材料不是新版驗收結果。
- 歷史文件階段僅查版本、Git objects、文件與原碼，當時未執行試行或測試。後續實作的實際執行證據見第 11 節。

## 11. 實作執行紀錄（2026-10-24，歷史）

第 11–19 節保留首輪按時間推進的紀錄；其中「目前／下一步／尚未」均指當時。最新補強決策、邊界與順序以第 20 節及本文件前段現行規則為準。

目前依使用者持續開發授權執行。ask-matt 路由採 implement → 已確認邊界的 TDD → Standards／Spec 獨立 review；本地計畫作任務來源，沒有新增外部 issue 或推送。

| 切片 | 現況與直接證據 | 待辦 |
| --- | --- | --- |
| P0／B | 已保存 [B runtime](../research/codex-coding-harness-implementation-evidence/baseline-B/manifest.json)，內容指紋重核相符 | Trial 前仍須固定完整宿主配置及隔離 |
| I01 | README 已區分完整 plugin 與 task-harness 的兩個按需相依目錄；新規格及本計畫的現況已同步，舊規格標為歷史基線；宿主已確認維持 Desktop | 實際 Desktop 預檢與 smoke 結果仍須回填 |
| I02 | 主 skill 精簡完成；保留驗收、風險升級、未知結果、主責及按需持久化；review 增加內部精簡輸出模式 | 真實 agent 行為回歸尚未執行 |
| I03 | 原生包與來源註冊完成；內附 app-server 已驗證快取準備、專案啟停、更新與回退；C 的 Desktop 只讀對話已核對四個技能及 19/19 內容指紋；demo-002 未啟用 | 實際 coding 行為、可寫權限配置及執行中版本固定仍待驗證 |
| I04 | 沿用 demo-002 AGENTS／POM，不另建 profile，原 checkout 不變 | 啟用只在隔離試用專案進行 |
| I05 | 無新增強制 hook；來源 symlink／缺必要入口拒絕建包，release 不覆寫；原 hook 仍為提醒 | 逐路徑宿主控制實測未完成，不宣稱完整覆蓋 |
| I06／I07 | 原生結果優先；跨 turn 與兩個全新原生程序均取回同一命令的原始輸入／最終結果；standalone exec 取消後取回 exit 137 並觀察到 fixture parent／child 已停止、既有寫入仍在；helper 含 inner failure、過期來源、未知 receipt 防重播與 POSIX 中斷測試 | 模型接續未完成工作、模型 turn／MCP 的取消、失聯及未知副作用恢復仍待驗證 |
| I08／P2 | 隔離 archive 的 parent/reference／合法共用 scheduler；最新版 grader 含兩個 context 行為，最新兩輪各 13 測試、0 skipped，parent 1 failure、其餘全過；第 7 組 receipt 綁定全部 47 個 POM／Java 輸入；兩份資格實作的資源所有權 review 已完成 | 每個實際 trial 產物仍需驗收與所有權 review；資格結果不是三組 smoke |
| I09 | [最小紀錄範本](../../tests/fixtures/harness-run.template.json)保留 null、人工時間方法、接手及原 trial 結果 | 尚無可比較人工時間與效益結論 |

新增接點：`scripts/package_harness.py`、`packaging/codex/.codex-plugin/plugin.json`、`.agents/plugins/marketplace.json`；生成物 `dist/personal-harness` 不提交。第一份生成物保留於 `dist/releases/initial-candidate`。目前包 manifest SHA-256：`cdd9c5a7dd48c40993de8eaab226d98cb4bd79faed76ae76b322ef4392f5eb9d`，未凍結為試行配置。

全部原始結果、來源指紋及審查修正摘要見 [實作查核紀錄](../research/codex-coding-harness-implementation.research.md)。

目前宿主阻礙：Computer Use 以安全限制禁止操作 `com.openai.codex`；現有 plugin connector 無本機安裝能力。未繞過此限制、未改宿主內部資料庫或直接填寫信任 hash。CLI 結果不替代 Desktop 驗收。仍可繼續本機元件與案例查核；完整完成狀態保持未達成。

使用者核定 smoke 上限：每組一次／15 分鐘／整次不補跑、不購買 API 額度及付費資源；此核定不解除 P0–P3 門檻。下一步先完成效果型 grader 審查及合法替代方案驗證，再處理 Desktop 能力驗收與配置凍結。

後續 grader review 又找出 orphan 可能在 close 前到期的假通過；已加入時間窗口與 skipped 有效性判定。修正後第 4 組原始紀錄與 XML 顯示 parent lifecycle 1 項失敗、reference 1 項通過，兩者 skipped 0。之前兩輪只屬先前 grader 版本，最終版本的穩定性及替代解法資格仍需查核。

後續進展：合法共用 scheduler 替代實作通過相同 grader，並修正最後的基線取樣時序窗口；最新 parent/reference/shared-scheduler 三份第 5 組 receipt/XML 均無 lifecycle skipped，parent 失敗，其餘通過，既有測試通過。Python 維護測試更新為 26 項（1 skipped）。跨 turn 原生紀錄讀回已驗證，跨 session 尚未驗證。

接入阻礙已縮小：Desktop UI 仍不可由工具操作，但已直接確認其內附 CLI 有 plugin add，且能發現本地包。未執行 add，因 upstream 安裝路徑會將 user-level plugin 設為 enabled true；須先查明如何符合專案 opt-in，不能以短暫全域啟用再關閉當成設計已成立。完整進度及來源見實作查核紀錄的後續章節。


### 原生接入驗收更新

正式 repo 停用設定已觸發宿主原生快取準備，無須 plugin add 的全域啟用副作用。後續已官方註冊共用 marketplace，並在無 CLI 覆寫下驗證專案四個技能／另一專案零、停用零、0.1.1 更新及 0.1.0 回退。回退前保存 0.1.1 完整快取核對結果。最新證據為 registered-source-probe.json、update-probe-2.json、rollback-probe-2.json、update-cache-verification.json、development-adoption-probe.json。

目前本 repo `.codex/config.toml` 明確 enabled=true 供後續開發，來源指向原 0.1.0 包；demo-002 不增加設定。全域只註冊 marketplace 來源，候選 plugin 啟用項目不存在、其他 plugins 設定不變。G01/G04 的原生引擎接入部分已有證據；Desktop 活躍對話、實際 coding 行為與其他未決控制不因此通過。完整過程及觀測限度見實作查核紀錄末節。

### 執行邊界及進入 smoke 的查核歷程

本小節保留當時進度；宿主選擇與 C 信任的後續處理見第 12 節。

已驗證獨立 command/exec 的有效邊界：必須從隔離 workspace 啟動 app-server，不能只改請求 cwd。該配置允許自身寫入、拒絕原 repo 新 canary 寫入及本機連線；首個反例與修正後原始結果皆保留。尚未證明所有工具路徑均受相同控制。

最新 lifecycle grader 加入另一存活 context 的清理回歸，parent/reference/shared-scheduler 的第 6、7 組結果各 13 tests，lifecycle 2 tests、0 skipped，parent 1 failure，其餘全過。第 7 組 receipt 綁定全部 47 個 POM／Java 輸入，前後與目前檔案指紋一致。三份共同 parent workspace 與輸入指紋已準備，尚未啟動模型。A/B/C 技能預檢發現 C 的 project-local config 被信任規則停用；此缺口必須解除，不能以已準備 bundle 作通過。

當時已詢問首輪是否改採內附 CLI，未收到決定前未啟動相依 trial。使用者後續選擇維持 Desktop，詳見第 12 節。原定每組一次／15 分鐘／不整次補跑／不購買額度保持；不得略過必要控制或把準備紀錄當成執行結果。

原生證據的持久取回另完成窄邊界查核：`native-persisted-read.json` 保存兩個依序啟動、終止的全新內附 app-server 對同一既有 command item 的 `thread/items/read` 請求／回應。兩者取回的 item 完全相同，命令、cwd、exitCode 及輸出與先前跨 turn 紀錄相符，user config hash 不變；沒有 resume、模型 turn 或重播原命令。這證明現有持久證據可跨程序取回，不代表活躍模型已恢復未完成任務，亦不使歷史驗收結果自動適用目前來源。

發佈依賴另以 `standalone-runtime-qualification.json` 查核：複製完整套件至獨立暫存目錄，18 個內部 Markdown 連結均落在套件內且存在；從該目錄執行已封裝 review helper 的 prepare／verify，核對兩份 fixture 快照內容，並執行 report hash checker 的有效／過期負向案例。Runtime 19 個檔案指紋未變。這補足入口與本地 import 的依賴查核，不是模型 review 品質或完整 migration 行為的證明。

原生取消的窄邊界也已驗證：`native-cancel-probe-2.json` 先確認隔離 fixture 寫入及 parent／child PID，再送出 command/exec/terminate，收到原 exec 最終 exit 137；兩次程序表查核均無該 PID，heartbeat 保留既有 tick 且觀察期間不再增加。這不代表取消會回滾副作用，也不泛推所有 process tree、模型 turn、MCP 或斷線恢復。首次 fixture 語法錯誤造成的無效觀測及診斷保留，不計成功；修正後證據已獨立唯讀複核。三組模型 smoke 次數仍為零。

首版整合 review：Standards 無新增 finding；Spec 發現兩項文件問題（前段仍使用實作前狀態、未說明單獨攜帶 task-harness 的按需相依），均已修正並獨立複核解除。未發現其餘可獨立修復的確定實作錯誤。Review 不解除尚欠缺的實際驗收；當時待決的宿主及 C 信任處理已更新於下節。

## 12. 維持 Desktop 後的準備查核（當時狀態）

使用者已明確決定維持 Desktop 主視窗，先完成其他查核；不再等待是否改用 CLI 的決定。下列已完成項均是案例或原生引擎的窄邊界資格，不是正式模型 smoke，也不宣稱 Desktop 活躍對話已採用相同配置。

| 項目 | 直接查核與結果 | 證據／限制 |
| --- | --- | --- |
| 案例資源所有權 | reference 的專屬 executor 經 Spring disposal 呼叫 shutdownNow；shared 替代只取消自身 ScheduledFuture，保留共用 scheduler；來源 hash 仍吻合第 7 組 receipt | 獨立 Spec review 未發現可見契約違反；不保證強制中止忽略中斷的 in-flight callback，未新增此驗收要求 |
| 三個受控目錄信任 | 逐檔核對輸入、拒絕未知檔案與 symlink 後，以原生 config/value/write 加入三組 canonical trust，逐次串接 expectedVersion | project-trust-preflight.json：設定語意只增加指定三項 trust；未停用必要控制或填寫 hook 信任 hash |
| C 來源與快取 | 官方 marketplace add 只註冊 personal-harness-trial-C；候選 user-level 啟用項不存在，既有 plugins 不變 | trial-marketplace-registration.json；來源註冊及三項 trust 是保留至試行的持久設定，結束／取消後需依實際工作清理，不能刪除其他設定 |
| 實際技能發現 | 第 3 次尚未刷新 catalog，C 為零；第 4 次原生 plugin/list 刷新後，本次比較的額外入口為 A 無、B 舊版 task-harness、C 四個候選快取技能，errors 均空 | trial-discovery-preflight-4.json；三組仍有共用全域 skills，不宣稱純淨配置或公平比較 |
| 固定輸入與內容 | A48／B51／C70 個記錄檔案未變，共同 48 個檔案一致；B 符合固定快照，C 完整快取通過內容核對且 manifest 符合原可信 cdd9… 指紋；三組均無 Git history／remote | trial-input-readiness.json；不等於已隔離其他可讀答案、副本或聊天 |

Smoke preparation 的宿主選擇已更新為 desktop_main_window，三組仍為 not_started，模型 trial 次數為零。此輪沒有改 runtime 或重跑不相關測試。

仍需在實際 Desktop 配置驗證：活躍對話使用的技能來源／模型設定、原工作及外部 grader 的寫入保護、實際可用工具的副作用邊界、取消與續作、15 分鐘上限的可執行處理及原始結果取回。Computer Use 仍禁止操作 Codex 自身；不繞過此限制。開始任何正式 trial 前，上述相依必要能力須具備直接證據。

下一個最小切片是在 Desktop 主視窗以 C 的已記錄隔離目錄做**純載入與執行邊界預檢**，不送出 bug 修復任務；取得原生配置／工具事件後再決定是否符合 smoke 門檻。介面若無法提供必要狀態，就保留該能力缺口，不用 config 檔案、CLI 清單或 agent 自述代替。

### Desktop 活躍對話的後續直接觀察

後續本對話的宿主 skills_instructions 已列出四個 personal-harness:* 入口，來源為 personal-harness-local 的 0.1.0 快取；主 agent 實際讀取並選用該 task-harness。原生工具核對完整快取，manifest 符合原可信 cdd9… 指紋。desktop-active-catalog.json 分列宿主目錄轉錄、實際讀檔及核對事件；轉錄本身不是獨立偵測器，原宿主訊息與工具事件才是依據。

這解除「本 repo 目前 Desktop 模型對話是否收到候選技能目錄」的窄缺口，不代表 C 隔離對話、GUI 顯示、完整 coding 或工具安全路徑已驗證。

當時原生 list_projects 沒有 C 隔離目錄，create_thread 只能選已登錄專案且沒有任意路徑參數，因此曾要求先加入以下目錄。後續已用官方 App Server API 保存指定 cwd 的任務，再由 Desktop 原生工具接手，解除這項建立前置阻礙（見第 13 節）。沒有改寫宿主內部資料或繞過 Computer Use 限制：

`/private/var/folders/76/hd61cw513zbdlr0y7_h27dx80000gn/T/harness-smoke-0vwf4lur/C`

使用者後續已明確要求建立 C 純預檢對話。以下是當時備妥的預檢任務內容；實際新對話沒有繼承本對話的答案，也未在原 demo-002 目錄執行：

> 僅做 Desktop harness 載入與可觀測性預檢，不開始 bug 修復或正式 smoke。確認本對話的實際工作目錄是指定 C 隔離目錄；如不符就停止。核對宿主提供的 personal-harness 技能目錄與實際採用的快取入口、內容版本，記錄可取得的模型／工具／權限資訊及原始工具結果參照；無直接資訊就標未知，不由 config 檔案存在推斷已載入或控制有效。只讀取必要的專案配置與技能，不修改檔案／設定，不執行 TASK.md、不讀研究／答案／其他組、不發訊息到其他對話。先交付已驗證、未驗證及下一個必要邊界測試的清單；此任務不算 A／B／C smoke。


## 13. C 純預檢的 Desktop 結果（當時狀態）

使用者已明確授權建立「C 純預檢」新對話，並再次確認 C 完整路徑。專案清單當時仍未同步，但建立工作已完成，不再要求使用者重複加入或確認路徑。

成功對話 ID：`01a16bf4-9fbb-7681-8d9e-ae1d1cf68edf`；Desktop 執行 turn：`01a16bf5-3b73-7e22-9d46-f5bde9a32914`，最終 completed。它是獨立的只讀預檢，不計 A／B／C smoke。

接入方式採官方 App Server API：先建立 read-only、C runtime root 的對話並保存已授權的初始任務文字及名稱，沒有呼叫 turn/start；確認 Desktop 原生 read_thread 能讀回後，再由 Desktop send_message_to_thread 啟動模型預檢，並用 wait_threads 取得完成狀態。原生 API 準備階段未執行模型；後續 Desktop 階段確實執行了模型。沒有直接修改宿主資料庫，也未將 CLI 模型執行替代 Desktop。

第一個空白 ID 沒有持久化，Desktop 無法取回；第二次只讀查核回傳 not loaded；第三次先經 thread/resume 確認舊 ID 無 rollout，才保存唯一可由 Desktop 取回的新對話。三份 desktop-C-thread-create*.json 完整保留過程，不將空白 ID 當成功交付。此為建立恢復，不是正式 trial 的補跑。

| 項目 | Owner 直接核對 | 限制 |
| --- | --- | --- |
| 實際執行位置 | 原始 pwd 命令成功，cwd 符合指定 C canonical 路徑 | 不從標題或提示文字推斷位置 |
| C 載入與內容 | 新對話讀取 C 的四個候選快取 SKILL；未截斷的 E14 原始結果為 19/19 source／cache 指紋相符，manifest 對上可信 cdd9… 指紋 | 不代表技能自動觸發、hook 執行或完整 coding 行為 |
| 產物保護 | 預檢後 C 全部 70 個輸入及檔案集合未變 | 只讀策略不等於正式 coding 的可寫隔離已合格 |
| 結果取回 | Owner 從另一個 Desktop 對話取回 completed turn、命令、cwd、退出碼及輸出，保存原始讀回資料 | 一筆較長技能輸出仍有截斷標記；開始幾次工具啟動失敗未全部呈現為 commandExecution 項目，未冒稱完整執行軌跡 |
| 宿主與模型 | 準備回應記錄原生版本 0.164.0-alpha.11.1、配置模型 gpt-6.1-sol／high、readOnly／networkAccess false | 與先前 0.163 引擎證據有版本差異；配置選擇不證明實際 serving build 或未發生路由 |

直接證據位於 desktop-C-preflight-readback.json，Owner 核對與明確限制位於 desktop-C-preflight-owner-check.json。Standards 獨立 review 未發現 Owner 聲明超出證據的重大問題。暫存及快取寫入遭拒是實際觀察，但不能擴張為所有工具、網路、升權或可寫 coding 邊界已驗證。

首輪正式 smoke 仍為零。下一個必要切片是 Desktop 可寫 coding 配置的邊界驗證，包括自身目錄可寫、原工作及外部 grader 受保護、實際工具路徑、取消／恢復及時間上限；不能把本只讀對話直接當作該配置已驗收，也不擴大本次只讀預檢任務的授權。


## 14. Desktop 控制預檢與 smoke 進入門檻

使用者已明確授權建立及續作最多一個控制預檢對話，必要控制合格後再建立 A／B／C 各一個 smoke 對話。每組一次、最多 15 分鐘、不整次補跑、不購買付費資源維持。此授權沒有降低控制門檻；正式 trial 仍為 0。

已建立唯一控制對話 `01a16c0c-7b36-73e3-8a16-209598391f8d`，實際由 Desktop 執行；App Server 只準備並持久化任務，未執行模型。三組加入共同的測試配置：workspace-write、approval never、網路關閉、排除共用 tmp 寫入、暫存指向各自 workspace；停用 apps、browser_use 及四個已知 MCP 入口，保留 plugins／hooks。C 的 plugin opt-in 區塊保留。這是試行 fixture，不是 runtime 發佈變更；全域 config hash 未變。

配置與輸入更新於 `desktop-control-fixture.json`／`smoke-preparation.json`；先前準備檔另保留。A49／B52／C70 個記錄輸入的 hash 核對無差異，包含共同業務來源、B 固定技能及 C bundle。新增的 canary 曾位於 C 的 `.harness-control`，已保存原檔與連結目標、確認 worker 結束後清除，該目錄目前為空。配置尚未凍結，不將這些紀錄冒稱正式 trial 的最終 file-set 驗收。

| 控制 | 直接證據及目前結論 |
| --- | --- |
| 有效設定 | 建立回應明示 workspaceWrite、networkAccess false、兩項 tmp exclusion true；實際 Desktop 宣告還有額外 visualization root，不宣稱只有 C 可寫 |
| 自身寫入／外部直接與 symlink 寫入 | C marker 寫入讀回成功；兩種外部寫入均遭 EPERM，guard 原值及 owner hash 未變。只對受測路徑成立 |
| apply_patch 外部寫入 | 同 call_id 的原始 call 明指 patch-guard.txt，結果拒絕越界寫入；owner hash 未變。證據為 desktop-control-patch-call-and-result.json |
| 本機網路 | 指定 127.0.0.1:51775 connect 遭 EPERM；實際 listener 最終 connections 0，owner 已停止它。不推論所有 first-party 連線路徑 |
| worker 取消 | 同 handle Ctrl-C 的最終結果為 signal 2、deadline 尚未到、child exit 0；owner 查核兩 PID 均缺席且 heartbeat 穩定。只證明該合作型父子 fixture 的取消 |
| 模型 turn 取消／15 分鐘上限 | **未合格**。外部獨立 app-server 的 turn/interrupt 回傳 thread not found；續作停止訊息僅使模型配合完成，status 是 completed，沒有 interrupted 證據 |
| 其他工具／跨組配置 | **未合格／未覆蓋**。first-party web、image、artifact、app、CUA 等仍可見；不能從 features.apps=false 推論所有外部影響被阻擋。A／B 尚無實際 Desktop coding turn 的同等有效邊界證據 |

原始事件見 desktop-control-readback-1.json；worker owner 查核、canary 封存、輸入與清理紀錄分別為 desktop-control-worker-owner.json、desktop-control-owner-reconciliation.json、desktop-control-canary-cleanup.json。Standards 獨立唯讀複核確認受測 exec 路徑的窄資格，但不支持整體必要控制已合格。

下一步先解決 Desktop 到時停止的操作方式，不能以模型自行計時、可接受停止訊息或殺掉整個 Desktop 代替已驗證的個別 turn 停止。若保留 Desktop 並改採使用者在場監看／手動 Stop，須先由使用者選擇這項人工負擔，在同一控制對話驗證 Stop 的原生最終狀態及 worker 存活，再納入人工成本；當時尚未核定；後續選擇與實測見第 15 節。這項選擇也不自動解除其他工具範圍與 A／B 配置的剩餘查核。沒有決定前保留 smoke 未開始，不重複試相同失敗的外部 interrupt 路徑。


## 15. 人工 Stop 首次驗證結果與下一個診斷

使用者已選擇人工監看與 Stop，並同意先驗證。現有控制對話內執行一個 120 秒自限的父子 canary，沒有新增控制對話；本次 turn 為 `01a16c29-3650-7b10-ab8e-49bcd72c4152`，由 controller 透過 Desktop send_message_to_thread 啟動。

使用者兩次回覆已按 Stop。第一次回覆後，原生查詢仍為 inProgress，兩 PID 存活且 heartbeat 增加。最終原生命令執行 120085ms、exit 0，回傳 parent_stop_signal=null、deadline_expired=true、child_exit_code=0；模型 turn 約 132726ms，最終 completed。這只能判定**本次沒有證明手動停止有效**，不能由點擊回覆推論取消成功，也不能斷定 UI Stop 普遍失效或使用者按錯。

Owner 後續核對 PID13812／13813 均缺席，heartbeat 穩定；原檔與 hash 已封存，確認模型 turn 結束後清除第一組 canary。原始證據：manual-stop-desktop-readback.json、manual-stop-start-observation.json、manual-stop-after-observation.json、manual-stop-after-second-observation.json、manual-stop-1-artifacts／manifest。Standards 獨立 review 同意不能判定 Stop 通過；child 收到的 SIGTERM 是 parent 自限到期後清理，不是 UI Stop 證據。

已準備下一個最小診斷：仍使用同一控制對話、相同 worker 內容，改由使用者直接在該對話送出任務，區分主視窗直接啟動與跨對話工具派送的回合路徑。此為待驗證假說，不認定前者一定有效或後者是根因；未自動重跑第一組，也未開始第二組。準備檔為 C/.harness-control/manual-stop-2/TASK.md 與 worker.py，收據 manual-stop-direct-ui-preparation.json。這是控制預檢的不同診斷，不是正式 trial 補跑。

成本目前只記錄兩次使用者回報的 Stop 操作；人工 active seconds 未量測、標 unavailable，不以 120 秒程序等待時間冒充人工投入。原生專案清單仍未列出 C，不能假設此因素是 Stop 未生效的原因，也不再重複要求加入專案。正式 smoke 為零，其他必要控制及 A／B 實際配置仍須通過。


## 16. 直接 UI 啟動的 Stop 診斷仍未通過

使用者已在同一控制對話直接送出第二項診斷，原始 userMessage 可由 Desktop 取回；turn `01a16c2e-88c4-7c61-b5d0-200d63ab11b7`。使用者回覆已按 Stop 後，owner 仍直接觀察到 inProgress、PID16708／16709 存活、heartbeat 在 0.7 秒內增加。因此「改由主視窗直接送出即可解決」的假說沒有得到支持，不把它再當成待執行的解法。

為尊重停止意圖，controller 隨後核對兩 PID 的命令、父子關係，僅向該 canary parent 發送 SIGTERM 清理；兩 PID 隨後缺席。最終 command 54730ms、exit0、signal15、deadline_expired=false、child_exit0；模型 turn 69478ms、completed。這個訊號有明確的 controller 來源，**不是 UI Stop 成功證據**。本次無法判定 UI 點擊作用於何處或根因，不歸咎使用者，也不推論所有 Desktop 版本／對話均有相同問題。

證據為 manual-stop-direct-ui-desktop-readback.json、manual-stop-direct-ui-after-observation.json、manual-stop-direct-ui-owner-cleanup.json、manual-stop-direct-ui-owner-reconciliation.json。第二組原檔已封存於 manual-stop-2-artifacts，heartbeat 穩定、模型 terminal 後已清除；C 控制目錄為空，三組記錄輸入 hash 無差異。累計三次使用者回報 Stop、一次直接 UI 任務輸入；人工 active seconds 仍 unavailable。正式 smoke 仍為 0，原 15 分鐘上限不變。

不再重複相同人工點擊測試，也不殺掉共享 Desktop／app-server 來替代個別回合停止。現有工具仍沒有可用的 Desktop 個別 turn 停止入口；外部 app-server 與兩種人工路徑均未取得合格證據。

**待決建議，而非已確認設計變更：**首輪 A／B／C 改以同一份 Desktop 內附 CLI、各自隔離 cwd 與共同政策執行，controller 維持對其自有 App Server 連線與 turn 的控制；結論限於原生引擎，Desktop 主視窗驗收保留未通過。此方案已因人工路徑的新增失敗證據而重新提出，不能視為使用者已撤回先前維持 Desktop 的決定。若採用，先驗證當前 0.164 版本的模型取消、worker 結束、必要工具邊界與 15 分鐘處置，再凍結配置開始各一次 smoke；0.163 的窄測試不能替代。若繼續維持 Desktop，保留宿主能力阻礙，等待可用能力或外部狀態改變，不自行降低上限。尚未啟動 CLI 模型、建立 smoke 對話或更改 host_choice。


## 17. 使用者核定內附 CLI 與控制資格

使用者已明確選擇「改用內附 CLI，先驗證控制」。共同宿主為 Desktop 內附 0.164.0-alpha.11.1 的獨立 App Server 程序／連線，配置模型 gpt-6.1-sol、high。使用同一套 CLI、專案政策與固定輸入，A→B→C 依序執行，避免模型 trial 互相爭用資源。每組仍只一次、整次最多 900 秒，不整次補跑、不購買資源；配置選擇不證明實際 serving build。Desktop 主視窗驗收沒有因此通過。

- `cli-control-1`：同一連線收到 interrupt 成功與 interrupted，terminal clean 後空，父子 PID 缺席、heartbeat 穩定；總約 6.25 秒。
- `cli-deadline-1`：將共同 wall limit 縮短為 40 秒，沿同一「截止前保留 20 秒」單調時鐘路徑觸發；約 20.69 秒收尾，模型 interrupted、writer 已停止。這是縮短時限的控制測試，沒有實際等待 15 分鐘。
- `cli-readiness-A-2`／B／C：各自從指定 cwd 啟動，直接 exec／symlink 外部 guard 寫入與 loopback connect 均遭拒；三組各 11 個局部基線 tests，failures/errors/skipped 均 0。Maven 真實路徑由 PATH 解析。A 首次預檢因寫死錯誤 Maven 路徑而未啟動 Maven，原失敗已保留，不算正式模型 trial。
- 實際比較入口：A 無候選／舊版額外入口，B 固定舊版 task-harness，C 四個候選快取技能，skills errors 均空；B／C 透過官方 skill input 明確指定來源。仍共用其他全域 skills，且答案讀取未完整隔離，因此只具流程 smoke 用途。
- 獨立 review 發現異常路徑可能略過 native clean，已修正：異常亦嘗試有界 clean，並按既有專案專屬 TMPDIR 標記、PID 與啟動時間核對 writer，必要時 TERM／KILL，最後僅關閉自己建立 session 的 server process group。`cli-fallback-selfcheck.json` 證明有標記程序被停止、無標記負向控制保留。
- `cli-fault-1`：實際 writer 啟動後模擬 interrupt／clean 通訊不可用，獨立收尾約 6.79 秒，owner 核對 server／父子 PID 均缺席、heartbeat 停止，跨程序讀回原 turn 亦為 interrupted。driver 仍保留 unverified／原注入錯誤，不把失效操作改稱成功或重試。

控制覆蓋限於已確認的 CLI 政策、正常及指定失效路徑、保留專屬環境標記的程序；不是任意惡意程式或所有外部工具的通用隔離保證。原生結果與 driver 當次來源保存在各 evidence 目錄。config/read 證據只留控制開關及必要暫存設定，略去服務參數與無關環境值。

`smoke-preparation.json` 已依本次決定更新 host_choice，原檔另存 smoke-preparation-before-cli.json。模型 trial 尚未開始；最終凍結清單與獨立收尾複核完成後才進入 P4。所有 canary 已封存並清理，原 workspace 記錄輸入未改。新增 driver 是本輪評測控制程式，不納入 runtime 發佈包。


## 18. 首輪執行與 grader bootstrap 修正

配置及 driver 已凍結於 frozen-trial-config.json，實際清單包含宿主產生的 Git metadata／objects；不再將較早「無 Git history」的觀察當成目前資格。這輪仍僅流程 smoke。A 的唯一 trial 約 236.74 秒完成，原始工具結果有全模組 90 tests、0 failures/errors/skipped；未對 A 續作模型。

首次外部驗收 cli-grade-A 出現一項失敗，獨立 Spec review 確認是 grader 過度限制：它直接以 addBeanFactoryPostProcessor 加入 internal PP，繞過公開 annotation／Registrar 將 PP 註冊為 bean 的生命週期。A 以 Spring 管理的 PP 擁有並釋放 scope，屬契約允許的解法。V1 結果保留為驗收方法缺陷，不據此宣告 A 產品失敗。

外部 grader 升版 public-entry-v2，只將 cleanupContext 改成公開 @EnableConcurrentRequestScope 啟用；兩個測試本體、TTL／等待與 assumption 不變。原檔保存 lifecycle-grader-v1.java.txt，修正版 hash／理由與政策補錄於 frozen-trial-grader-v2.json。獨立 review 已確認 diff 不弱化斷言。

V2 以唯讀來源／grader、僅 target 與獨立 tmp 可寫的原生 sandbox 驗證：parent 13 tests／1 failure；reference、shared-scheduler 與 A 固定產物各 13 tests／0 failure，全部 lifecycle 2 tests、0 skipped。來源前後 hash 相同。這是 checker 修正後的外部重評，不是模型 trial 補跑。B／C 使用相同 V2。

外部回饋政策為模型交付後驗收，不把結果回送受測 agent 或延長／重啟模型 trial。初始凍結檔漏了獨立的回饋政策欄位；A 實際沒有收到回饋，此項已明示補錄，後兩組維持相同方式。組內自行測試、診斷修復仍保留，A 的兩次測試失敗與最終通過皆保存。這項紀錄缺口不能包裝成事前完整預註冊或公平能力比較。

B 已在確認未變的凍結輸入與 driver 後開始唯一 trial；C 依相同門檻接續。後續各組結果以 smoke-preparation.json、cli-smoke-*、cli-grade-*-v2 為直接來源，不從 agent 最終文字推斷產品通過。


## 19. 首輪完成、品質結果與保留的限制

本輪 A／B／C 各一個原始 trial 已完成；沒有重建任務副本或整次補跑。A 236.74 秒、B 297.71 秒、C 657.25 秒，均在原900秒內。三組原生模組測試90／91／93項全過，凍結版 public-entry-v2 外部13項皆過、0 skipped。初始輸入與各組追加來源、原始RPC、外部唯讀驗收／XML及來源指紋均已保存。

C 的 controller 在 reviewer子回合完成時誤判主回合完成；確認實際主回合interrupted與writer停止後，修正歸屬，以同一thread／副本、原900秒剩餘預算續作，總時間包含修復與等待。原始錯誤state不覆寫，整次結果為cli-smoke-C/reconciled-state.json；controller-root-attribution-regression.json重放真實事件確認只接受指定thread／turn。C不是無干擾樣本，不能把657.25秒當候選流程固有速度。

交付後獨立review更正B漏報：持read lock的factory關閉context時升級write lock造成P1死鎖。有界公開API診斷在parent/reference/A/C通過、B失敗，0 skipped；保留B原交付，不再續作或修復此trial。這是事後診斷，不覆寫凍結版13/13，也不回溯為一般能力結論。C自身獨立review的兩項關閉競態已在同trial修正；外部固定產物review未發現新實質違反。完整結果見[交付報告](../research/codex-coding-harness-smoke-20261024.research.md)。

| 能力／首版項目 | 目前直接證據 | 完成範圍與限制 |
| --- | --- | --- |
| I01／I02 流程與導覽 | README、精簡task-harness、review內部模式；C原生實際讀取並執行 | 按風險review及有效證據修復有實際紀錄；不主張一般效益 |
| I03／G01／G04 發佈及採用 | final-runtime-verification.json；current-version-adoption-2 的啟用4／停用0、0.1.1更新及0.1.0回退 | 現行0.164重查只用程序內覆寫，0模型回合、全域設定未變；不代替Desktop GUI驗收 |
| I04 專案接入 | 三組凍結AGENTS／TASK／POM／政策、各11項離線基線 | 原demo-002不加永久採用設定，不覆蓋未提交內容 |
| I05／G02 控制 | cli-control-1、cli-deadline-1、cli-fault-1、負向所有權控制及三組readiness | 只涵蓋指定CLI路徑與保留標記的writer，不宣稱任意惡意process隔離 |
| I06／G03 證據與恢復 | 原生持久讀回；C同thread跨server續作、原始錯誤與整次截止保留 | 不是整次重播；主回合與子回合歸屬已補機械檢查 |
| I07／I08／G06 回歸與案例 | 26項維護測試（1 Windows skip）；V2資格與兩種合法解法；事後factory-close診斷 | checker修正與產品修正分開；回放素材持久保存，不依賴暫存目錄 |
| I09／G07 成本及結果 | flow-smoke-outcomes.json、各summary原生用量、全部嘗試與C復原成本 | 人工active time缺值，不填零、不宣稱省時；外部評估與trial內review用量分開 |
| G05 與後續採用 | 三組共享全域skills；C查閱共用記憶索引；未完整答案隔離 | 僅完成流程smoke，不完成公平能力比較、未見案例、真實效益或第二專案驗證 |

原demo-002的60個相關檔案hash與git status皆未變。三組固定交付hash仍相符、沒有剩餘trial writer。本輪新增的三個暫存trust與C來源註冊已移除，其他全域設定及本repo開發來源保留；A/B/C產品副本保留供檢視。持久輸入為frozen-input-common（48檔）、baseline-B、baseline-C及產品patches。

目前0.164採用重驗的第一次純metadata嘗試因CLI keyPath引號格式未載入候選，stderr及來源保留；修正後四階段均通過，沒有模型trial或全域寫入。不得把第一次未載入當成功。

首輪結束時 P5／P6 尚未執行，沒有越過每組一次上限。當時提出的人工 active time／返工觀察建議已被 R04 取消；最新安排為 Desktop 日常、CLI 開發評測及自動證據，見第 20 節。Desktop Stop 仍保留能力缺口。

## 20. Smoke 後修訂：Desktop 日常、CLI 開發評測

### 20.1 已確認決策與事實邊界

本節保留已確認的補強計畫與實作前提案；使用者後續已授權 N01–N03，本次落地結果見第 21 節，N04–N07 尚未實作。R01–R07 對應規格的同名決策；P0／P1／P2 是本輪優先序，與原 P0–P6 階段不同。

| 決策 | 落實方式 | 對應工作 |
| --- | --- | --- |
| R01 評測控制回歸 | 主／子回合精確歸屬、writer 停止核對、原期限續作；先限於評測工具，不抽通用 runtime | N02 |
| R02 Grader 資格 | 需求／fixture／依賴／環境相關變更按影響重驗；checker 升版重評全部受影響固定產物，不重跑 agent | N03 |
| R03 風險驗證 | 併發／生命週期按風險測試與獨立 review，共用原則與專案案例分離，不加人工核准 | N04 |
| R04 自動證據 | 不人工計時／填表／觀察；整理已有事件及產物，人工時間未知保留，失效不阻塞無關日常工作 | N04、N06 |
| R05 不干擾日常 | 開發測試獨立副本／設定／資源；不改日常全域設定、記憶、資料、既有對話或程序 | N01，全項前置邊界 |
| R06 少量代表回歸 | 簡單 bug／小功能／局部重構，按變更影響回放；正確性與不必要流程負擔皆保留證據 | N07 |
| R07 主要入口 | Desktop 日常、CLI 開發評測；先補 CLI，近期確認 Desktop 實際路徑，其他宿主／第二專案按需後置 | N02、N05 |

已確認問題：B 交付有 P1 死鎖但未證明由舊 skill 導致；C 評測 controller 曾錯判子回合，當輪已修正；V1 grader 曾誤拒合法解法，V2 已修正。後續工作是保留可重複回歸及補足驗證，不冒稱這些修正仍未完成。三組人工時間缺值、共享背景材料及單一熟悉案例，仍不能支持人工效益或能力排名。

四項複核調整已確認：N05 增加 Desktop 任務交付驗收；N01 納入宿主自動寫入與共用資源限制；N01／N02／N03／N06／N07 不再依賴先建整合工具；案例資格按 bug／功能／重構區分。三項主要邊界不變：Desktop 日常入口、開發測試不干擾日常、不要求人工觀察。

### 20.2 具體待改檔案、接入及完成條件

下列新增路徑是工程安排提案，尚未建立；實作時先確認沒有同名工作。先做最小回歸及可重用控制邏輯，原生工具或現有命令足夠就直接使用；只有重複操作形成需求時才增加薄的執行入口。`tests/harness/evaluate.py` 僅保留為可選落點，不是必建項，也不強制各項集中同一檔案。研究 evidence 目錄維持唯讀，不能直接覆寫原 probe 或 trial；新結果另建唯一 run 目錄。

| ID／優先序 | 具體位置與改動 | 重用與接入方式 | 最小完成證據 |
| --- | --- | --- | --- |
| N01／P0 測試邊界 | 先於 `tests/test_harness_evaluation.py` 保留必要邊界回歸；只在測試與實際執行需共用時於 `tests/harness/` 放最小控制邏輯，不先建整合入口 | 重用原生 sandbox、首輪指紋／所有權核對；程序內覆寫僅是候選手段。盤點實際涉及的設定、plugin cache、宿主持久狀態與自動生成資料；現有 `.codex/config.toml`、`.codex/hooks.json`、`.agents/plugins/marketplace.json` 只讀，不改日常設定 | 測試寫入與程序有明確專屬範圍，日常快取／狀態不被覆寫；CPU／記憶體、並行程序及共用帳號額度有可執行限制與停止條件；正常／失效收尾只處理測試資源。無法隔離或限制即停止相依測試，不以設定檔未變宣稱安全 |
| N02／P0 CLI 控制 | 在 `tests/test_harness_evaluation.py` 先加入歷史事件回放；必要共用邏輯放 `tests/harness/`，不以建立 `evaluate.py` 為前置 | 重用封存 `personal-harness-cli-session.py.txt`、`personal-harness-cli-resume-C.py.txt` 已修正的歸屬／期限／收尾邏輯，移除暫存路徑與特定 C ID 的硬綁定；不用整份 probe 充當通用工具，不擴充 `run_check.py` 為 controller | 子回合、錯誤 ID、快速完成可區分；未知結果先核對，writer 未確認停止不續作，期限不重設。取消／失聯只處理自有程序；靜態事件回歸可獨立完成，不等待其他評測功能 |
| N03／P0 Grader | 重用 `tests/fixtures/lifecycle/HarnessLifecycleTest.java`、`HarnessFactoryCloseRegressionTest.java` 與 `task.md`；需要可重複選取時才新增 `tests/fixtures/harness-cases.json`，記錄類型、需求、grader、fixture、相關依賴／環境及固定產物參照 | 沿用封存 `personal-harness-grade-smoke.py.txt` 的可用驗收方法與原生命令，先建立資格／重評的最小檢查；重複操作有需要才接薄入口。Java fixture 無需為了有 diff 而修改，原 B 交付不改 | 相關變更能選出受影響檢查；資格依第 5 節類型驗證，不強迫重構先失敗。checker 升版保留歷史，重評所有受影響固定產物且模型啟動次數為零 |
| N04／P1 共用規則 | 最小修改 `skills/task-harness/SKILL.md` 與 `skills/ai-code-review/SKILL.md` | 在既有風險驗證／review 段補鎖、callback、背景工作及關閉時序的判斷，引用現有內部 review 模式；同步 task-harness 交付段的自動證據、人工時間未知及無人工觀察原則；不複製整套規則，不新增固定角色或 hook。原 metadata／引用僅在內容介面確實受影響時同步 | 具體風險有相稱的驗證理由及必要獨立 review；簡單任務不固定增加文件／角色／人工核准，不要求計時或填表。具體 Java 測試仍在專案／評測 fixture |
| N05／P1 Desktop 採用 | 後續更新 `README.md` 的 Desktop 入口與分項支援狀態；重用 `packaging/codex/.codex-plugin/plugin.json`、`scripts/package_harness.py`、`tests/test_harness_package.py` 準備候選測試包，發佈內容改變才更新版本 | 在 N01 邊界成立後，於獨立 Desktop 測試情境呼叫候選流程，完成低風險修改、相稱驗證與可追溯交付。原生方式足夠就重用，不建 Desktop controller，不自動更新日常快取／啟用版本 | 分項記錄載入、任務交付、外部取消。前兩項與該任務必要控制均通過，才可標 N05 的最小日常路徑完成；僅載入成功為部分完成。外部取消未驗證獨立保留，不阻擋不依賴它的驗收，也不免除必要控制；不要求人工觀察或手動 Stop |
| N06／P1 自動證據 | 調整 `tests/fixtures/harness-run.template.json`；在 `tests/test_harness_evaluation.py` 核對歸屬、去重與缺值，重複使用才在 `tests/harness/` 保留最小整理函式 | 重用封存 `personal-harness-summarize-smoke.py.txt`、原生 RPC 與 outcome；可先由 agent 整理現有結果，不等待新執行器。原始參照、統計與判讀分開；評測工具不安裝到日常環境 | 可整理驗收、求助、重試、修復及全部交付狀態；錯誤歸屬、缺事件、人工時間不可得均明示，不要求使用者補填；統計失效可繼續，必要驗收缺失不可完成 |
| N07／P1 代表案例 | 必要最小素材放 `tests/fixtures/harness-cases/`；若已因重複選取建立 `tests/fixtures/harness-cases.json` 就共用，否則先沿用現有 fixture／命令與來源參照 | 少量簡單 bug、小功能與局部重構分別依第 5 節資格；優先重用適合素材，按變更影響選取。可直接執行現有命令，不依賴整合入口；新模型回放須有後續有界授權 | 對應類型的正確性、必要回歸與不必要流程負擔均有證據；重構允許修改前後測試都過，功能不需歷史 bug；依風險判讀，不用固定工具數或單一 LLM 分數判輸贏 |

共用套件繼續重用四個 skills 與既有封裝；`define-task`、`project-setting`、`run_check.py` 目前沒有已確認的必要改動。此次設計沒有新增 mandatory hook，也沒有已確認需要修改全域設定的項目。若後續能力查核發現新缺口，只提出最小必要調整，不為了完成表格而增加元件。

封存來源：[probe manifest](../research/codex-coding-harness-implementation-evidence/probe-sources/manifest.json)、[主回合回歸](../research/codex-coding-harness-implementation-evidence/controller-root-attribution-regression.json)、[grader V2](../research/codex-coding-harness-implementation-evidence/frozen-trial-grader-v2.json)、[品質診斷](../research/codex-coding-harness-implementation-evidence/post-smoke-quality-assessment.json)。封存程式含單次試驗假設，不能直接複製後宣稱通用或執行。

### 20.3 建議執行順序（未執行）

1. **N01：先確立不干擾邊界。**唯讀核對測試會涉及的設定、快取、宿主自動寫入及共用資源，確定專屬副本、寫入／程序所有權與可執行的資源限制。禁止以先修改再還原日常狀態替代隔離；限制未明就不啟動相依測試。
2. **N02＋N03：先補最小回歸。**用保存事件與固定產物驗證已知故障；原生命令與現有工具足夠就沿用，不等待整合入口。靜態回放不需先完成整個控制工具；原生取消／失聯實測依賴 N01，只用隔離 canary，不把舊紀錄當當前版本驗證。
3. **N04：補共用風險原則。**保留精簡核心與專案測試邊界，驗證有必要的高風險行為與小任務成本。
4. **N05：驗收 Desktop 任務交付。**唯讀盤點可提早進行；完成 N01 邊界與 N04 候選後，先準備測試包，再驗證載入及一個低風險任務的修改→驗證→交付。缺行為證據時 N05 保留部分完成；外部取消另列，不以 CLI 或載入成功替代，不要求人工觀察。
5. **N06＋N07：自動證據與少量案例回放。**欄位／來源核對可與 N02／N03 一起完成。新模型回放只依賴該操作適用的 N01 限制、N02 控制、N03 案例資格、受測候選及必要原生證據／有界授權；N06 完整統計工具不是啟動前提。只有重複操作有需要才補薄入口，各責任不必集中同檔。CLI 案例可在 Desktop 相依項受阻時獨立完成，兩者證據不得混用。
6. **交付核對：**若 runtime 有變，按既有方式建包、核對依賴／版本／啟停回退，更新 README 與這兩份文件的結果及限制；發佈包不含開發評測工具。安裝到日常使用環境另依明確採用授權，不隨測試自動進行。

P2 的第二專案、其他宿主與廣泛能力比較只在實際採用需求出現時安排，不納入這輪補強的完成條件。首輪 smoke 不補跑、不回寫新標準成原先成績；新增案例另立 run 與配置版本。

### 20.4 剩餘能力缺口與最小驗證方案

| 缺口／既有證據 | 最小後續驗證（本輪不執行） | 失敗時的限制 |
| --- | --- | --- |
| G01／G04 Desktop 有載入預檢，但沒有整條日常路徑驗收 | 獨立測試情境中核對候選版本與信任，再由 Desktop 呼叫流程完成低風險修改、相稱驗證及可追溯交付；記錄載入／交付／外部取消三項狀態 | 僅載入成功不能完成 N05；載入、任務交付與該操作必要控制通過才算最小日常路徑通過，不外推全面支援 |
| G02 Desktop Stop 未取得有效證據；CLI 取消及指定 fallback 曾通過 | 先查能否不動日常設定建立自有、可自行到期且可獨立收尾的 canary；條件成立才做原生控制驗證，核對 turn／PID／heartbeat | 不反覆要求手動 Stop；無可靠控制就不執行依賴取消的 Desktop trial，不推論所有 skills 不可用 |
| G02／R05 開發配置、宿主自動寫入及資源占用是否不干擾日常尚須確認 | 盤點實際接觸的設定、plugin cache、持久狀態／生成資料；驗證專屬寫入與收尾，放無關檔案／worker 作負向對照；執行前固定 CPU／記憶體、並行程序及共用帳號額度限制與停止條件，不蒐集無關私人內容 | 程序內覆寫或設定檔未變不等於隔離；不能限制或隔離就停止相依測試，不要求人工看守、不新增日常監控 |
| G03／R04 原生事件能否涵蓋需要的自動摘要尚未完整驗證 | 用已存 RPC／outcomes 檢查事件歸屬、去重、缺值與最終產物，再與一個獲准的新執行結果核對 | 揭露覆蓋範圍；輔助統計失效不影響日常，必要驗收缺失仍受阻 |
| G05 公平比較的配置／答案／記憶隔離不合格 | 在獨立開發環境核對共同材料、實際載入及禁止讀取的 canary；不能更動日常記憶或全域 skills | 只報流程診斷，不排名；不將現有受污染 smoke 升格 |
| G06／R02 Grader V2 有 bug 資格證據，其他類型及可重複重評仍待驗證 | 先用固定產物核對變更影響與重評範圍；新案例依 bug／功能／重構契約驗證，重構不要求失敗基線；checker 升版重評不啟動模型，不等待整合入口 | 保留原結果，資格未明不作產品成敗判定；已驗證的最小檢查不因整合工具尚未建立而失效 |
| G07／R06 新代表案例、模型回放數量／預算尚未核定 | 先資格檢查與靜態事件回放；新模型回放前依後續授權固定次數、資源與回饋政策 | 不沿用首輪配額擴樣、不要求人工量測、不宣稱人工省時 |

### 20.5 本輪文件一致性檢查

R01–R07、N01–N07 及優先序可互相對照；規格描述行為契約，計畫描述檔案與接入。現行要求不再包含人工觀察窗口、把 Desktop 後置為其他宿主或自動重跑 agent。第 11–19 節歷史事實保留，與本節新決策分開；舊研究報告及原 trial 產物本輪不改。所有新增路徑與驗證均標為提案／未執行。

四項複核調整已逐項核對：Desktop 載入／任務交付／外部取消分項判定；宿主自動寫入與共用資源納入不干擾邊界；最小回歸不依賴整合入口；bug／功能／重構分別驗收。R01–R07、N01–N07、執行順序及能力缺口一致，保留不要求人工觀察的規則。35 個本地相對連結可解析，Markdown 表格欄數及 diff 空白檢查通過；僅兩份文件有 tracked diff，提案工具尚未建立。本次只檢查文件，不代表 Desktop、隔離或資源控制已實測通過。

## 21. P0 實作與整合驗收（2026-10-24）

本次授權依 ask-matt → to-tickets → implement-spec 完成 N01–N03；三張本地票各自實作並合入 `codex/harness-p0`。測試 seam 沿用已確認的程序邊界、原生事件歸屬與 grader 固定產物，不另要求人工核准。票單依 project-setting 採單檔本地計畫，沒有外部 issue、PR 或 push。

| 項目 | 實際落點 | 驗收結果 |
| --- | --- | --- |
| N01 | `tests/harness/boundary.py`、`tests/test_harness_boundary.py` | 15項真實canary（含監測失效及threaded launcher），寫入／symlink／network拒絕、資源限制、父子程序收尾及無關worker保護通過 |
| N02 | `tests/harness/control.py`、`tests/test_harness_control.py` | 9項原生記錄回放；主／子回合、早到／衝突事件、未知結果、writer停止與原deadline通過 |
| N01＋N02 | `tests/test_harness_p0_integration.py` | 真實取消與程序收尾不代替native readback；重新核對後續作，期限維持原值 |
| N03 | `tests/harness/grader.py`、`tests/test_harness_grader.py` | 9項資格／重評與錯誤路徑；五次固定Java產物重評與已知結果一致，來源前後不變 |

修正後最終 unittest 60項：59通過、1項原生Windows cmd.exe略過；60項測試的受測Python來源前後指紋相同。551個受保護來源／設定／runtime快取／原trial證據未變，原demo-002狀態與無關未追蹤工作保留。只有開發測試程式與證據新增，未修改runtime skill、hook、發佈版本或Desktop日常採用設定。

P0未建立通用evaluate入口或案例框架，沒有新的模型trial、app-server回合、人工計時或Stop要求。記憶體／程序數限制為20ms抽樣，支援保留自有process group的後代，單工作互斥是一個Python interpreter；不宣稱任意惡意／detached程式的容器保證或Desktop原生控制已重新驗證。

本次P0完成判準：三張票的直接測試／固定產物結果可追溯，整合來源指紋與日常保護核對成立，Standards／Spec兩軸review無待處理問題。三項均已有證據，四項review發現已修正，兩軸複核通過且無待處理finding；不將P1或Desktop完整驗收納入本次完成聲明。完整證據、命令及限制見[P0報告](../research/codex-harness-p0-20261024.research.md)。
