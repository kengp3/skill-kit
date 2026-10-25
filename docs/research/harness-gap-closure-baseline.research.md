# Harness 補驗：G00 唯讀初態基準

日期：2026-10-25（Asia/Taipei）。**G00 文件與唯讀基準完成；整體補驗未完成。** 本報告只保存初態資格，不是第二份持續 tracker；後續狀態唯一來源為[中央細分表](unified-project-settings-acceptance.research.md)。依[補驗規格](../specs/harness-validation-gap-closure.spec.md)、[G00 ticket](../plans/harness-gap-closure-00-baseline.plan.md)、[總計畫](../plans/harness-validation-gap-closure.plan.md)與[可行性研究](unified-project-settings-gap-fixtures-feasibility.research.md)執行。

## 候選與工作區初態

預期：鎖定指定 0.3.0、辨認真正根目錄及既有修改，避免將候選存在當成已接入。實際觀察與 raw 如下；未安裝技能、啟動模型、授信 hooks、注入故障、操作 UI 或修改 demo。

- 產品根 `/Users/kengp3/Workspaces/mine/simple-skills`，HEAD `ebc901e407760e7adf6cda368232e9a8ebdecb4d`。既有 `.codex/config.toml` 修改及全部原 untracked 路徑保留於[baseline.json](harness-gap-closure-baseline-evidence/baseline.json)的完整 porcelain status；未代為提交或清理。G00 自有 worktree 為 `/private/tmp/simple-skills-gap-g00`、branch `codex/gap-g00`，由同一 HEAD 開始。
- demo 根 `/Users/kengp3/Workspaces/mine/demo-002`，HEAD `fdc13d69334235c9edd3e61a69710c5d7a5fab78`／`main`。原修改為 ` M .gitignore`、` M AGENTS.md`、`?? .planning/README.md`。根目錄尚無 `project-setting.md`、`harness-project.json` 或 `.codex/`；`.agents/` 僅有 `workflows/`。這是磁碟初態，不代表宿主沒有全域來源。
- 已讀現行 demo `AGENTS.md`；source／tests／pom／README／架構文件為 truth，`.planning/` 是歷史封存。只保存歷史 README 的指紋，未讀取或執行其中 workflow。後續 G01 須先初始化 demo 自身文件規範，不借用產品 repo 的分類。
- [demo-files.json](harness-gap-closure-baseline-evidence/demo-files.json)保存 `git ls-files --cached --others --exclude-standard -z` 的 705 個唯一檔案路徑、SHA-256／大小／mode 及 symlink 資訊。未遍歷 `.git`、未讀 ignored 檔案或憑證、未 follow symlink。此檔是後續保留驗證的 authoritative 初態；G00 的[保存核對](harness-gap-closure-baseline-evidence/preservation-check.json)確認原檔與兩個 repo 的 HEAD／完整 status 未變。
- 指定候選 `/Users/kengp3/Workspaces/mine/simple-skills/dist/candidates/kengp3-harness-0.3.0` 的 manifest SHA-256 為 `7e37d77315faee550e3f2e1edc4b3a621da490f50ce4a8d937c78f9d71fbfd9e`，與授權值相符。實際執行既有 `scripts/package_harness.py --verify`，exit 0 且逐檔符合 manifest：[候選核對原始輸出](harness-gap-closure-baseline-evidence/candidate-verification.json)、[原 manifest bytes](harness-gap-closure-baseline-evidence/candidate-manifest.json)。沒有重建或覆寫候選。
- 日常 `.agents/plugins/marketplace.json` 仍指向 `./dist/kengp3-harness`，該 plugin metadata 為 0.2.1。候選核對通過只證明固定來源完整，**不代表 demo 或日常入口已安裝、載入、升級或授信**。

重要原檔 SHA-256（完整檔案基準見上述 JSON）：

| demo 檔案 | SHA-256 |
| --- | --- |
| `.gitignore` | `6bdb1dcaf7d6976a56fad178c8796a2661220cdc3dc77b7fcea1e569171385ca` |
| `AGENTS.md` | `ad76c4104fd4aaa44dd3392b315cd4eb479aa980b38da20076680e1e4acbc3dd` |
| `pom.xml` | `497634028a0b120200a85c23fb90994175b78f9b3e99207688af072933999d37` |
| `.planning/README.md`（僅 hash） | `e950d8c6196e80d4cae2e2d292457b04f33d5dea238bfff1e940434daa2efe5b` |

## 宿主與資格界線

預期：記錄可直接確認的資格，不以 help、過去成功或 API 能力推斷其他能力通過。

- 直接唯讀觀察為 **Darwin arm64、codex-cli 0.164.0**；`codex --version` 與 `codex app-server --help` exit 0，完整 stdout／stderr 存於 baseline。兩者均回報無法建立 PATH aliases 的權限警告，未忽略該 raw；沒有因此更改 PATH 或日常設定。help 列出 transport 只證介面存在，不證重連生命週期或普通模型工具可啟動。
- 全域 `/Users/kengp3/.codex/config.toml` 與 `auth.json` 只計算 SHA-256／檔案 metadata；未輸出內容、未複製 auth、未建立試跑 state。G00 讀回核對 hash 未變；這不是整台機器／keychain 的全面差異稽核。
- effective config、instructionSources、skills／hooks／plugins 來源 allowlist、每案 writable roots、自有 daemon endpoint、普通模型／工具啟動與當下模型強度 metadata **尚未做本輪原生核對**。各案仍須自己的 preflight；G00 不宣稱隔離或所有能力已成立。
- 主責本輪實際呼叫 `mcp__cua_repl.js` 的 `cua.getApp('com.openai.codex')` 得到原文：`Computer Use is not allowed to use the app 'com.openai.codex' for safety reasons.` [精確 call pair 原始 JSONL](harness-gap-closure-baseline-evidence/desktop-getapp.raw.jsonl)只從本次 session 擷取該 request／response 兩筆；[來源行號、call_id 與 hash](harness-gap-closure-baseline-evidence/desktop-qualification-note.json)可追溯。未歸檔全 session 或含無關私人 app／tab 的 inventory。**Desktop UI 控制目前受工具 app allowlist 阻擋**；未做停止／選單操作，不繞過改用 AppleScript。模型 API 可行不代表 Desktop 可控制；專用 Desktop state／模型資格也尚未核對。
- 真正主責 spawn 回應交付遺失、同一邏輯事件 native redelivery、僅影響自有 provider 連線的故障控制尚無已確認資格；先保持相應分支受阻。client／observer transport 遺失、shell replay 或新 prompt 均不能替代。provider 強度 probe 亦須按實際拒絕層判定。
- Windows 依使用者最新明確指示排除：**V06 排除、G08 cancelled，不是 passed**。不再調查或佈建，歷史 Windows skip／限制保留。

## 本次判定與保留證據

expected → observed → raw → verdict：指定候選完整且原有內容保留 → manifest verifier 成功、705 個 demo 原檔及兩 repo status／HEAD 讀回一致、全域 hash 不變 → [候選核對](harness-gap-closure-baseline-evidence/candidate-verification.json)、[保存核對](harness-gap-closure-baseline-evidence/preservation-check.json) → **G00 通過，限文件及唯讀基準**。中央表的已實作／未執行／受阻／排除與安裝狀態分開；本輪未新增任何 V 行為通過，不把舊 A–G／native API case 當新試跑。

只修改本 G00 報告／證據、中央報告及 G00 ticket。所有原始歷史驗收證據保持原位與 bytes；本次沒有新增產品程式、控制器、runtime 依賴或鏡像測試。完成前讀回 JSON／文件、核對本次連結、狀態與 staged diff；文件檢查結果存於[document-check.json](harness-gap-closure-baseline-evidence/document-check.json)。後續 G01 開始變更 demo 後，應以這份凍結初態核對其已授權新增內容，不改寫 G00 初態冒充新證據。
