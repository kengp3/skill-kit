# Harness 補驗：獨立 Standards／Spec 審查

日期：2026-10-26（Asia/Taipei）。**兩軸 actionable findings 均為 0；G03 核准後增量驗證及審查已通過，其他必要驗收仍受阻，整體補驗未完成。** 本文保留各固定版本審查；初次受查版本中 G03 待核准的敘述屬歷史，核准後結果見末節。不另建持續缺口表，目前狀態仍以[中央細分表](unified-project-settings-acceptance.research.md#g00g09-補驗唯一細分狀態表)為準。

## 受查範圍

- 固定 base：`f15338eba416abaec42abb5414dd6ea770c9f1cf`；受查 head：`0ec9812e0d5ecc3685385c0692f90368b812c0f8`。
- 比較命令：`git diff f15338eba416abaec42abb5414dd6ea770c9f1cf...0ec9812e0d5ecc3685385c0692f90368b812c0f8`；提交清單命令：`git log f15338e..0ec9812 --oneline`。本範圍 506 檔，主要是直接證據、維護用控制器與文件，另有 macOS maintenance CI；產品 skills／scripts／tests／dist 沒有改動。
- 規格：[補驗規格](../specs/harness-validation-gap-closure.spec.md)、[核准工作圖](../plans/harness-validation-gap-closure.plan.md)與 G00–G09 本地 tickets。Windows 經使用者明確排除，G08 cancelled，沒有計為通過。
- 兩個唯讀 agent 分別執行 Standards 與 Spec，不互相代審；結果身分與父層核對記於[審查證據](harness-gap-closure-review-evidence/review-results.json)。以下為其回報，僅整理格式。

初次審查後，父層最後讀回另發現總計畫仍留一條 Windows 執行步驟；同一修正 agent 已於 `097e04caa25c415b39ebfb7468820b86750aa605` 改成明確排除，不執行資格探查、接入、commandWindows、最小任務或 VM。兩名原 reviewer 再檢查 `0ec9812...097e04c` 的六檔文件差異，均無 required findings；確認本報告轉述準確、G09 done 僅指收尾，必要缺口及整體未完成仍保留。integration `eb74624888e4be2fbb4b9000f4d64f0077431c5e` 的 tree 與該 target 相同。這是增量文件審查，不是重新執行驗收。

續作補記：父層讀回 G06 原始 stderr，發現個案報告「此次三回合沒有 429」不符[resume stderr 第 2 行](harness-gap-closure-hook-sources-evidence/resume/server.stderr.log)。同一修正 agent 已於 `2fc674b5d742d658636d90200432ff59b703db4a` 更正為原生 retry 1/5、約 17 秒及[同一 turn completed](harness-gap-closure-hook-sources-evidence/resume/resume-terminal.json)，未另開 turn、重派或改寫 raw／原判定。原兩名 reviewer 分別重查此單句及證據，均無 required findings；整合 commit 為 `1d7dfae2295bdb36837017b1398734cd80846a3e`。此次修正不關閉任何受阻驗收分支，也未重跑模型。

## Standards

**無 actionable findings。** 受查 head 為上述 `0ec9812`。

- 已確認無 tracked `CODING_STANDARDS.md`／`CONTRIBUTING`；依 root `project-setting.md`、README checklist、使用者 AGENTS 與 writing-for-agents 核對。
- 文件位置與用途一致；maintainer drivers、CI 與 evidence 未變成技能 runtime 前提。CI 使用唯讀 permissions、固定 checkout SHA，README 清楚揭露未跑 hosted CI。
- metadata 白名單投影附離線 self-check；G05／G06 清楚區分私有完整原件與公開 excerpts，保留省略索引及 hash，cleanup receipts 未宣稱刪除完整 state。
- Heuristic，非違規：G01／G04／G06 的 `Native` transport 與 exporter 有複製，但屬凍結個案取證；抽成共享依賴會削弱歷史可重現性，本輪不要求重構。未發現因此造成的實際錯誤。

此結論不代表整體驗收通過。Standards reviewer 未執行 driver、模型、測試或 remote 操作；敏感資料掃描與私有原件一致性以已交付 receipts 為限，未重新讀取認證。

## Spec

**Actionable findings：0。** 未發現本 diff 新增的需求誤實作、未要求範圍或虛假完成宣稱；已知缺口如實列為部分／受阻，不能算通過。

直接抽核確認：

- G01：目前 demo 的 705 原檔與 26 新檔均符合保存指紋；原生 RPC 第 891 行真正寫入／驗證 19 bytes，clean-readback 第 82 行 `cmp_exit=0`。
- G02：原 RPC 第 369／371 行為同命令開始及 exit 143；續作 RPC 第 196／205／207 行具來源讀回、三門檻後唯一刪舊檔與保存結果。
- G04：first-only RPC 第 216／376 行支持 `gpt-6-sol/low` child 開始／完成；provider-probe 第 35／37 行支持真 HTTP400 `reasoning.effort` 拒絕及 failed 終態。
- G05／G06 公開 excerpts 與私有 full raw 的 hash、保留行逐 byte 相符，僅省 `session_meta`；沒有拿 checker 自述替代原生證據。

尚未完成的必要驗收，並非新增缺陷：

- G03 正常信任仍待人工；規格第 66 行要求「正常人工介面審閱精確 hook 定義……新 invocation再驗證」。raw 五 hooks 仍 untrusted。
- G05 跨 root 查回、真正 spawn 結果遺失及 provider sampling 未通過；第 78 行：「client通知遺失或換連線不能替代」。network 原 turn 實為 routing discovery failed。
- G06 raw stdin source／native redelivery 未通過；第 84 行：「完整native re-entry必須有可關聯原邏輯事件的redelivery證據」。
- G07 UI 未執行；第 88 行要求「實際點停止與選擇模型」。原始 CUA 拒絕與報告一致。

受查中央表、README 與 G09 ticket 一致保持整體未完成；G08 正確 cancelled。Spec reviewer 未重跑模型、信任、Desktop、Windows 或測試；這是來源與既存直接證據審查。

## 父層直接核對與驗證界線

父層另以既有 checker 核對 G01 的 19 bytes／done 合約／705 原檔，G02 原始開始與 exit 143／續作三門檻／唯一刪檔，G04 三分支，G05 同一 child／turn／字面成果及 G06 最終產品合約，均符合個案報告。G02 checker 只在記憶體移除其最後寫 verification 的語句後執行，避免覆寫已提交證據；驗收 assertions 未改。這些是既存證據讀回，沒有新模型試跑。

父層對 G05 五份公開 excerpt、G06 兩份公開 excerpt 重新逐 byte 比對所有非 metadata 行；G06 六份私有原件的 full hash 也相符。公開資料保留原件 hash、行號及省略理由，不把 excerpts 稱完整 raw。受查 506 檔對當前 auth 的 4 個相關 leaf 實值掃描為零匹配，未輸出或保存認證實值。G05 兩份已無運行需求的認證複本已[限定清除](harness-gap-closure-unknown-child-evidence/credential-copy-cleanup.json)；其餘 case／state／private raw 保留。G03 尚待人工的同案 state 不在此次清除範圍。

維護 full suite 的直接結果為 **112 tests，OK，1 個既有 Windows skip**，詳見[原始 log](harness-gap-closure-review-evidence/full-tests.log)及[命令／受測 head](harness-gap-closure-review-evidence/full-tests.json)。原執行 head 為 `11233ce`；父層確認至本次受查 head 的產品與維護測試來源未變，不因後續證據／文件更新重跑全套。G05／G06 等新增維護控制器另有個案 red／green／封存 self-check。候選 manifest 再核對仍為 `7e37d77315faee550e3f2e1edc4b3a621da490f50ce4a8d937c78f9d71fbfd9e`。以上不是 hosted CI、正常 hook trust 或 Desktop UI 通過證據。

## 收尾與待解鎖

本輪沒有尚待修正的 review findings；G09 可完成證據對帳與審查收尾，但不得把其他票的受阻條件改為 done。初次受查版本的 G03 解鎖條件為先取得[五項精確定義的人工核准](harness-gap-closure-persisted-trust-evidence/human-review.md)，再於正常介面重新核對定義、信任並執行兩次 invocation；這項後續已完成，詳見末節。其餘條件仍沿用各案：G05 需主責可用的跨 root 查詢與真結果交付／sampling 故障控制；G06 需可觀測的原始來源及同邏輯事件 redelivery；G07 需允許的 Desktop 操作環境及實際畫面／宿主證據。

未修改全域或日常 marketplace；demo 接入 0.3.0 不表示日常 0.2.1 入口已升級。未 push、建立 PR、執行 hosted CI 或 Windows。來源工作區原有 `.codex/config.toml` 修改、其他 untracked 及 demo 原有 dirty 內容保留。已清除合併後不再需要的 implementer worktrees，branch refs 保留；各案需留存的 state／private raw 保留，實際增量驗收與審查所需工作樹在收尾前暫留。

兩軸各 0 actionable findings；兩軸均未見需攔截的新增問題。必要驗收受阻仍使整體目標未完成。

## G03 核准後增量審查

使用者已直接回覆「已審閱，同意正常信任這五項精確定義」。增量 base 為 `4014a65f2c298bf22c247f282a637532ec85955e`，受查 target 為 `0f29d11ed457adb258f9ea7e1b4936fa06bd1e9e`，整合為 `5249774943130c342da3b9c6fe39e1e5bece807b`；53 檔只屬 G03 ticket／報告／證據，沒有產品修改。原兩名 reviewer 分別審查此固定差異，未啟動新模型或操作信任。完整驗收與原始來源見 [G03 報告](harness-gap-closure-persisted-trust.research.md)及[正常操作配對](harness-gap-closure-persisted-trust-evidence/normal-trust-operation.json)。

### Standards：G03 增量

**0 actionable findings；無 hard violations 或需處理的 heuristic。** 新控制器僅供維護取證；正常信任操作有授權、輸入／結果來源配對。公開 excerpts 保留省略索引與原件 hash，cleanup 限定 owned auth，沒有擴稱刪除 state。原人工審閱包及 exact hooks 未改。

Reviewer 親跑兩個明確離線入口：`verify-observed.py --self-check` 拒絕缺少 developer 提醒及 failed hook；`native-persistence.py --check` 確認兩個不同程序／thread、精確成果、done 合約與 exit 0。未操作 live／trust、未啟動模型或讀取認證值；cleanup 依已交付收據核對。

### Spec：G03 增量

**0 actionable findings。** 符合規格第 66 行要求的來源、hash、信任狀態、實際注入及退出後同 state 新 invocation 驗證：

- 正常 TUI 操作／chunk 與原文 hash 配對相符；前五項 untrusted，兩次新程序前後及清 auth 後皆同 hash trusted。
- PID `32723`／`33015` 各一次 turn completed、20 bytes 成果與唯一 done 合約；各 RPC 第 27／28／30 行及第 513／452 行支持 hook completed，私有 session 第 12／13／16 行有 developer 提醒。
- 兩份公開 excerpt 與私有完整 raw 逐 byte 相符，僅省 session_meta；公開 RPC 亦符合私有原件。

**G03 限定通過成立。** 不外推 SubagentStart 已執行、Desktop、Windows、demo 或日常安裝已信任；G05／G06／G07 仍未通過，整體未完成。Spec reviewer 僅讀既存證據，沒有執行模型、信任或測試。

父層另親跑同兩個離線入口並核對兩份 excerpt 的私有來源 bytes，均通過；對本次 53 檔以 8 個實際 credential／creator identity 值做精確比對，零匹配，沒有輸出值。已確認專用 auth 副本不存在；正常信任 state 與私有 raw 留存供覆核。
