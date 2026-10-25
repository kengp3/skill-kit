# G04：strict 與 provider 強度負例補驗

日期：2026-10-25–26（Asia/Taipei）。**本次 V07 三個指定分支均取得直接證據並通過；整體 G00–G09 補驗狀態由中央報告另行彙整。** 依[補驗規格](../specs/harness-validation-gap-closure.spec.md)、[G04 ticket](../plans/harness-gap-closure-04-strict-effort.plan.md)及[可行性研究](unified-project-settings-gap-fixtures-feasibility.research.md)，只操作 G04 自有案例及證據。Windows 依核准範圍排除。

## 邊界與資格

- 凍結候選：`kengp3-harness-0.3.0`；runtime manifest SHA-256 `7e37d77315faee550e3f2e1edc4b3a621da490f50ce4a8d937c78f9d71fbfd9e`。控制器核對整份 manifest，再複製四技能，省略選配 scripts；每案另存 installed-files 指紋。
- 每案使用 repo 外全新 `/private/tmp/g04-*` project/state；以 demo-002 當前 `AGENTS.md` 與 `project-setting.md` 為輸入，再由控制器加入本案 `model.default`、metadata 與 preserve canary。這些是明示的初態配置，不是模型產物或實測結果。沒有修改 demo。
- 原生 binary CLI `0.164.0`，自有 `app-server --stdio`、`ephemeral=false`、`runtimeWorkspaceRoots=[case project]`、`workspace-write/on-request/auto_review`。`thread/start` 顯示唯一 instruction source 為 case 的 `AGENTS.md`。
- 四個 candidate skills 在 `skills/list(forceReload=true)` 為 enabled；HOME 的 archify、define-task、project-setting 三技能在專用 state 依明確路徑 disabled。hooks 關閉，這不是 hook 信任案例；未使用 bypass、未改全域設定或 trust database。
- auth 只複製至 repo 外 0700 state 中的 0600 檔；全域 auth/config 只保存前後 SHA-256，不輸出值。僅確認自有 native server 退出後移除認證複本；失敗或未知的非認證原始狀態保留。
- [本機產生的 protocol schema](harness-gap-closure-strict-effort-evidence/protocol-effort-schema.json) 將 `ReasoningEffort` 表達為非空 string。本次每案 `model/list` 皆未列 `gpt-6.1-sol`／`gpt-6-sol` 支援 `minimal`，且 `gpt-6-sol` 支援 `low`。這是 metadata 資格，沒有推論 provider 已接受或已拒絕。

## Expected → observed → raw → verdict

| 情境 | 預期 | 目前觀測與判定 |
| --- | --- | --- |
| A／首選 strict | 首選 `gpt-6.1-sol;minimal` 不可改強度；後續 `gpt-6-sol;low` 合格，須真派出一個 worker，核對 canary 後產出精確 `G04_STRICT_WORKER_OK` 加 LF；同一合約 T1 done | 同一 turn 在一次 429 退避後完成；真實 child `gpt-6-sol/low` 完成，唯一合約 T1 done，精確成果 21 bytes。原要求及專案設定保留，**通過** |
| B／所有子 agent strict | 全部派工只能 `minimal`，候選與專案預設均不合格；T1 blocked、零違規 spawn、無 T1 相依成果；不受限且不相依的主責 T2 寫精確 `G04_INDEPENDENT_READY` 加 LF | 同一 turn 在一次 429 退避後完成；唯一合約維持 blocked，T1 blocked／T2 done，原始 session 無 spawn 請求或 child start，T2 精確 22 bytes，T1 成果不存在，**通過** |
| 獨立 provider probe | 維護者只發一次 protocol 可表達但該模型 metadata 不支援的 `minimal` 原生 turn request；依原始 request/error/context/終態判別拒絕層 | 唯一 `turn/start` 與 host turn context 皆為 `gpt-6.1-sol/minimal`；同一回合經 429 退避後收到 upstream HTTP 400 `invalid_request_error`，`param=reasoning.effort`、`code=unsupported_value`、`willRetry=false`，turn 正確 failed。這是目標拒絕層，**負例通過** |

每案 controller 只送一次本案 `turn/start`。native 自行重試 sampling 與控制器再次發起案例不同；保留所有 retry 原始紀錄，觀測 timeout 不作終態，也未重啟或降低強度。額外的 `xcodebuildmcp` startup handshake failure 獨立保留，不影響本案必要資格判斷，沒有安裝或修復該服務。

## 原始身分與證據

| 案例 | PID／thread／turn | 原始證據 |
| --- | --- | --- |
| A | 已退出 PID `99528`；thread `01a173c8-5059-7792-b035-e717eb9d6040`；turn `01a173c8-5065-7d31-8bda-eca7ba5e5171` | [初態](harness-gap-closure-strict-effort-evidence/first-only/preconditions.json)、[model/list](harness-gap-closure-strict-effort-evidence/first-only/model-list.json)、[RPC](harness-gap-closure-strict-effort-evidence/first-only/rpc.jsonl)、[stderr](harness-gap-closure-strict-effort-evidence/first-only/server.stderr.log) |
| B | 已退出 PID `197`；thread `01a173c8-8696-7633-8666-36015434a869`；turn `01a173c8-869e-7f10-b35c-943619291567` | [初態](harness-gap-closure-strict-effort-evidence/all-agents/preconditions.json)、[model/list](harness-gap-closure-strict-effort-evidence/all-agents/model-list.json)、[RPC](harness-gap-closure-strict-effort-evidence/all-agents/rpc.jsonl)、[stderr](harness-gap-closure-strict-effort-evidence/all-agents/server.stderr.log) |
| Probe | 已退出 PID `1863`；thread `01a173c8-ae6a-7390-b66a-b4d309b29afc`；turn `01a173c8-ae76-7d73-9195-ea81539ab938` | [初態](harness-gap-closure-strict-effort-evidence/provider-probe/preconditions.json)、[model/list](harness-gap-closure-strict-effort-evidence/provider-probe/model-list.json)、[RPC](harness-gap-closure-strict-effort-evidence/provider-probe/rpc.jsonl)、[stderr](harness-gap-closure-strict-effort-evidence/provider-probe/server.stderr.log) |

## 維護驗證

[獨立 checker](harness-gap-closure-strict-effort-evidence/check-evidence.py) 以字面規格核對實際產物、唯一合約、native child start/context及設定保留；[最初真實 red](harness-gap-closure-strict-effort-evidence/check-red.log) 是尚無實測產物的 missing-file failure。[第二個真實 red](harness-gap-closure-strict-effort-evidence/check-schema-red.log) 是 checker 對 spawn event 形狀的誤判：本宿主以 `subAgentActivity.kind=started` 記錄，而不是 `collabAgentToolCall.tool=spawnAgent`；此失敗不是產品失敗。依原始事件修正後，[green](harness-gap-closure-strict-effort-evidence/check-green.json) 同時核對真實 session 的 `spawn_agent` 請求、child context 與產物，不把 checker、控制器或 fixture 自述當通過。

[控制器](harness-gap-closure-strict-effort-evidence/native-strict.py) 僅為維護者可選驗收工具，不是產品 runtime。產品模型未被要求使用 Python／Node／helper；未改產品、歷史證據、central tracker 或 README，未跑 full suite／push／PR。三個原 native server 均 exit 0 後才移除 auth 複本；保留 case 非認證 state 與原始失敗記錄。三案 summary 均顯示設定、canary 與全域 auth/config hashes 不變。


## 讀回結果與限制

- A：實際 child ID `01a173cb-7e18-7c31-8bc7-576d85d6dac1`，path `/root/strict_worker`；native started event 與該 child 的 session turn context 均為 `gpt-6-sol/low`，完成事件保留。合約中的 observed 仍保留模型當時無法觀測的 `null`，沒有由控制器回填。見 [session contexts](harness-gap-closure-strict-effort-evidence/first-only/session-contexts.json)、[原始工具請求](harness-gap-closure-strict-effort-evidence/first-only/session-tool-records.json)、[唯一合約](harness-gap-closure-strict-effort-evidence/first-only/artifacts/docs/plans/g04-first-only.task-contract.md)、[summary](harness-gap-closure-strict-effort-evidence/first-only/summary.json)。
- B：零 `spawn_agent` 請求與零 child start，不把「沒有模型執行」誤當 strict 成功；實際主責已讀 metadata、保存 blocked 原因並完成 T2。見 [工具請求](harness-gap-closure-strict-effort-evidence/all-agents/session-tool-records.json)、[唯一合約](harness-gap-closure-strict-effort-evidence/all-agents/artifacts/docs/plans/g04-all-agents.task-contract.md)、[T2](harness-gap-closure-strict-effort-evidence/all-agents/artifacts/docs/research/independent-ready.research.md)、[summary](harness-gap-closure-strict-effort-evidence/all-agents/summary.json)。
- Provider：原始 upstream JSON 同時保存在 RPC error、turn 終態及 [thread/read](harness-gap-closure-strict-effort-evidence/provider-probe/thread-final.json)；[負例判定](harness-gap-closure-strict-effort-evidence/provider-probe/provider-verdict.json)、[context](harness-gap-closure-strict-effort-evidence/provider-probe/session-contexts.json)、[summary](harness-gap-closure-strict-effort-evidence/provider-probe/summary.json)。只支持該模型與 `minimal` 的這次拒絕，不推論其他模型、強度或帳號。429 是先行共用限制，schema／host／認證失敗沒有被混算。
- 一般 sandbox 原生命令最初遭 `sandbox-exec` 的 `Operation not permitted` 啟動前拒絕，模型依本案明確授權改用僅限 case 命令的 `require_escalated` 並成功讀寫；完整失敗與 auto-review 核准均保留。沒有修改權限規則或全機網路。
- [資格與敏感值檢查](harness-gap-closure-strict-effort-evidence/final-check.json) 核對四技能、停用 HOME skills、空 plugin catalog、隔離來源、auth/config 前後及無 token 值進入 evidence。此機讀檢查是原始證據的補充，沒有替代原生試驗。

未重跑整個產品 suite、未測 Desktop／Windows、未驗證 provider 內部權重。這些未計入本案三項通過。

## 衍生證據輸出修正（2026-10-26）

三個 `session-contexts.json` 已改為最小 metadata 白名單衍生輸出，保留真實 parent／child、時間、模型與強度；移除本地歷史衍生版非必要 `creator_account_id`／`creator_user_id` 及其他不屬驗收欄位。帳號識別不是 bearer token；原生 RPC、工具紀錄、合約 observed 與試驗結果均未修改，也沒有新模型 trial。詳見[輸出審查](harness-gap-closure-evidence-review.research.md)；原「credential_tokens_absent」只代表當次已檢查 token 未命中，不能推論當時未保存帳號 metadata。「全域未改」亦只描述原試驗時段。
