# G01：demo-002 正常接入與最小原生模型任務

日期：2026-10-25（Asia/Taipei）。**G01 通過，限正常接入、原生模型核心流程與讀回；hooks 仍未信任，V01 持久信任不在本案通過範圍。** 依[補驗規格](../specs/harness-validation-gap-closure.spec.md)、[G01 ticket](../plans/harness-gap-closure-01-demo-setup.plan.md)及[G00 初態](harness-gap-closure-baseline.research.md)執行；中央狀態由整合主責維護。

## 實際接入與成果

確認專案根為 `/Users/kengp3/Workspaces/mine/demo-002`。先讀現行 `AGENTS.md`，沒有讀取／恢復 `.planning/` 歷史 workflow，沒有修改 Java、pom、測試或其他原有內容。

從固定候選 `/Users/kengp3/Workspaces/mine/simple-skills/dist/candidates/kengp3-harness-0.3.0` 複製 define-task、project-setting、task-harness、ai-code-review 共 21 個技能／assets／references／agent metadata 檔案到 demo `.agents/skills/`；不是 symlink，也不依賴 live 來源。manifest SHA-256 為 `7e37d77315faee550e3f2e1edc4b3a621da490f50ce4a8d937c78f9d71fbfd9e`；選配 scripts 未安裝，逐檔 hash 與 candidate 相符，見[preconditions.json](harness-gap-closure-demo-setup-evidence/preconditions.json)。沒有安裝 plugin、改 marketplace 或全域入口。

真正原生 Codex 模型依明確 skill input 的 demo 來源完成：

- project-setting 初始化 demo 自身 [project-setting.md 快照](harness-gap-closure-demo-setup-evidence/final-artifacts/project-setting.md)，採其預設五類，再依 task-harness 的 Markdown provider 規格加入 task-contract、hook-receipt 分類與唯一 `schema_version=1`；模型列省略，沒有建立 harness-project.json。
- 模型新增 `.codex/config.toml` 的 `features.hooks=true`，合併 project-setting 與 task-harness 的完整標準 hooks；[設定](harness-gap-closure-demo-setup-evidence/final-artifacts/.codex/config.toml)與[hooks](harness-gap-closure-demo-setup-evidence/final-artifacts/.codex/hooks.json)已讀回。獨立核對完整結構精確等於兩份候選 assets 合併，沒有重複或 matcher 縮限。
- task-harness 先保存並讀回[唯一合約](harness-gap-closure-demo-setup-evidence/final-artifacts/docs/plans/harness-g01-smoke.task-contract.md)，才建立[最小成果](harness-gap-closure-demo-setup-evidence/final-artifacts/docs/research/harness-g01-smoke.research.md)。成果精確為 `G01_NATIVE_DEMO_OK` 加一個 LF，共 19 bytes，SHA-256 `ca833e26cc7c39f3c69a5f7ecf3a2a09d44ea2a73194ce26c4e6386dd2503a4f`。模型以 cmp／wc／od／SHA-256 驗證，再保存唯一 T1 與整體 done，完整重讀。初始保存、成果寫入及最終讀回均可在 [RPC 原文](harness-gap-closure-demo-setup-evidence/rpc.jsonl)定位；不是控制器預填成果。

新增共 26 個檔案：上述 21 個技能檔、project-setting.md、兩個 .codex 設定、唯一合約與最小成果。完整實際路徑／mode／bytes／hash 見[added-files.json](harness-gap-closure-demo-setup-evidence/added-files.json)。demo 新增內容仍未 stage／commit；原有 `.gitignore`、`AGENTS.md` 修改與 `.planning/README.md` 未 stage／commit。

## 宿主、來源與隔離資格

[當版 help／schema 核對](harness-gap-closure-demo-setup-evidence/host-schema-qualification.json)為 codex-cli 0.164.0。兩個自有 `app-server --stdio`，不是共享 daemon；`ephemeral=false`、workspace-write、on-request、auto_review，runtimeWorkspaceRoots 僅 demo。[初始化 thread/start](harness-gap-closure-demo-setup-evidence/thread-start.json)與[任務 thread/start](harness-gap-closure-demo-setup-evidence/thread-start-task.json)的 instructionSources 僅 demo AGENTS.md，host observed model=`gpt-6.1-sol`、reasoningEffort=`low`，與本輪 requested 相符；[session contexts](harness-gap-closure-demo-setup-evidence/session-contexts.json)保存以欄位白名單衍生的 session_meta／turn_context（保留原生身分、來源、時間與模型／強度；不含帳號欄位）。這是宿主觀測，不代表可查 provider weights。模型在合約把無法自行觀測的 session／user-turn ID 留 null，沒有用控制器的可見值偽裝模型知道。

第一試發現：獨立 CODEX_HOME **仍掃描**三個 `~/.agents/skills` user skills，包含舊 project-setting；[初始 skills/list forceReload](harness-gap-closure-demo-setup-evidence/skills-list.json)原文保留，不把第一試描述為完全隔離。實際初始化與任務均用 skill input 明確 pin demo 候選路徑，RPC 的技能輸入與檔案讀取可直接核對。未改全域 user skills。

原始任務終態後，第一 server 正常退出、state 清除；因此補驗用**新的**專用 state/server/thread，沒有冒稱同 state 或跨 invocation 信任測試。在[隔離 config](harness-gap-closure-demo-setup-evidence/clean-readback/isolated-config.toml)停用上述三個 user paths，再取得 [skills/list forceReload](harness-gap-closure-demo-setup-evidence/clean-readback/skills-list.json)：repo 四技能 enabled=true、三 user skills enabled=false；system skills 保留宿主預設。[local plugin/list](harness-gap-closure-demo-setup-evidence/clean-readback/plugins-list.json)為空，沒有產品 repo、錯候選或其他 plugin 來源。新 [thread/start](harness-gap-closure-demo-setup-evidence/clean-readback/thread-start.json)再核對 demo instructionSources／roots 與相同 host 模型強度；原生模型在明確**唯讀**授權下核對同一已 done 合約／provider／設定／19 bytes 成果，[原文](harness-gap-closure-demo-setup-evidence/clean-readback/rpc.jsonl)及[終態](harness-gap-closure-demo-setup-evidence/clean-readback/readback-terminal.json)可查。沒有重寫合約或重做成果；26 個新增檔案前後指紋也一致。

兩個 state 均在 repo 外專用 0700 目錄，auth 僅其中 0600 複本，server 退出後連 state 刪除。認證內容沒有進 evidence 或 Git；全域 auth/config 只保存 hash／metadata。所有觀測窗口逾時保持原 handle 等待，沒有因 timeout 重啟模型或重送寫入。無 child 派工，也沒有宣稱 `multi_agent=false` 關閉能力。

## Expected → observed → raw → verdict

| 預期 | 實際觀察與原始證據 | 判定 |
| --- | --- | --- |
| 普通原生工具可啟動 | [probe 終態](harness-gap-closure-demo-setup-evidence/probe-terminal.json)、RPC 的 pwd／head 直接輸出；completed，沒有 sandbox-exec 啟動錯誤 | 通過 |
| 由模型按 provider 初始化自身規範／hooks | [phase1 終態](harness-gap-closure-demo-setup-evidence/phase1-init-terminal.json)、[初始化快照](harness-gap-closure-demo-setup-evidence/phase1-artifacts/project-setting.md)、RPC 實際 shell 寫入／讀回；不是控制器生成 | 通過 |
| 最小核心任務不依賴 helper | [phase2 終態](harness-gap-closure-demo-setup-evidence/phase2-task-terminal.json)、RPC、[唯一合約與成果 checker](harness-gap-closure-demo-setup-evidence/green-check.json) | 通過；模型沒有執行 Python／Node/helper／Java／Maven |
| 載入來源可追溯並排除舊 user 能力 | 第一試可見舊 user paths，明確 pin repo input；新 state 停用 user paths後原生模型唯讀核對同一成果，[clean summary](harness-gap-closure-demo-setup-evidence/clean-readback/summary.json) | 通過來源 pin 與清潔讀回；保留第一試 qualification 發現，不回寫初態 |
| 正常 hooks 接入、不以信任 gap 阻擋任務 | [hooks/list](harness-gap-closure-demo-setup-evidence/hooks-final.json)的五個 project 定義有精確 sourcePath/currentHash，全部 untrusted；模型在同一合約記主動接手 | 已寫入／宿主列出通過；信任／事件觸發未通過，沒有 bypass／寫 trust db |
| 原檔及新成果保存 | [final reconciliation](harness-gap-closure-demo-setup-evidence/final-reconciliation.json)：G00 705 個檔案 bytes/modes/symlinks 無差異；26 新檔唯讀前後無差異；demo HEAD 仍 `fdc13d69334235c9edd3e61a69710c5d7a5fab78`，原 dirty entries 保留 | 通過 |
| 全域不變、owned 程序及認證清理 | [第一試 summary](harness-gap-closure-demo-setup-evidence/summary.json)、clean summary、final reconciliation：兩 server exit0、兩 state 不存在，全域 auth/config 前後 hash／mode／size 一致 | 通過本案範圍；不是整機全檔案稽核 |

## 最小維護驗證與限制

[native-demo.py](harness-gap-closure-demo-setup-evidence/native-demo.py)只供維護者驗收，沿用既有 stdio/RPC 設計，不是產品 runtime。已核准 seam 是「啟用技能 → 原生宿主／模型 → 設定、合約、成果 → 讀回」。控制器先檢查根目錄、manifest、21 份候選來源、705 原檔，錯誤會 raise 而非靠 exit0 當成功；成果 checker 核對精確 bytes、唯一合約、done／空 unknown 操作與保留結果。

red → green 是實際成果生命週期：[red stderr](harness-gap-closure-demo-setup-evidence/red-check.stderr)在模型寫入前因成果不存在而 exit1；模型完成後同 `--check-products` 成功並保存 green JSON。沒有製造假的產品失敗或改歷史 driver。收尾另修正控制器的重跑保護：已有 RPC／合約時在任何寫入或模型啟動前拒絕；[實際重跑拒絕](harness-gap-closure-demo-setup-evidence/replay-refusal.json)為 exit1，原 RPC／合約指紋未變。最後 compile(source) 語法檢查與完整 hooks／檔案／HEAD／global reconcile 通過。未為低風險純文字接入跑 Java/Maven；未測 Windows（本輪明確排除）、子代理事件、正常持久 hook trust 或 Desktop。G01 通過不替代其他 tickets 的必要分支。

## 衍生證據輸出修正（2026-10-26）

本地歷史衍生版曾帶入非必要 `creator_account_id`／`creator_user_id`；它們是帳號識別 metadata，非 bearer token。現已在兩個 G01 contexts 檔移除，driver 後續輸出採最小欄位白名單；原生 RPC、原試驗結果及 retained values 不變。這是既有證據重衍生，沒有重跑模型。詳見[輸出審查與紅綠核對](harness-gap-closure-evidence-review.research.md)及 before／after SHA 索引。既有「全域未改」敘述限當次試驗觀測，不代表日常 auth 此後不會合法更新。
