# 統一設定：原生模型與 agent 生命週期補充驗收

2026-10-25，以最終候選 0.3.0 在隔離暫存專案執行三組真實原生對話。三案通過：同任務模型覆寫跨回合保留、新任務不繼承；主責模型切換後僅後續未指定派工跟隨；候選耗盡只阻塞受影響成果。這是 T08 的補充證據，不代表其他平台或所有宿主能力均已驗證。

## 材料與方法

- 受測來源：`/private/tmp/unified-review-final-0.3.0`；`runtime-manifest.json` SHA-256 為 `7e37d77315faee550e3f2e1edc4b3a621da490f50ce4a8d937c78f9d71fbfd9e`。driver 在複製前逐一核對 manifest 中所有檔案的 SHA-256。
- 規則：專案統一設定 spec D6/D7/D8 及隨技能提供的 `task-harness/references/model-selection.md`。
- 宿主：本機 Codex CLI 0.164.0 的 `app-server --stdio`。每案使用獨立 `CODEX_HOME`、持續存在的 thread，以及同一 app-server 程序內的多次 `turn/start`；worker 由原生 `collaboration.spawn_agent` 建立，使用 `fork_turns=none` 與自足輸入。
- 主責初始 `gpt-6.1-sol / low`。隔離專案包含候選四個技能且不複製 `scripts/`；hooks 刻意停用，模型依共享規則接手。不增加產品 dispatcher、服務或強制 runtime。
- [native-lifecycle.py](unified-project-settings-model-lifecycle-evidence/native-lifecycle.py) 是維護者驗收 driver，使用 Python 僅為驅動宿主、保存證據；不是 task-harness 的安裝或執行依賴。
- 每案 raw RPC 保存實際 host 事件；`session-contexts.json` 只擷取原始 session 的來源、thread/turn ID、模型與推理強度。`subAgentActivity` 的啟動與完成事件用來核對 worker 身分及次數；guardian 的 `codex-auto-review` 不是任務 worker，未算進派工數。

## M1：任務覆寫跨實際回合保留，新任務使用專案預設

**預期：** 第一回合將 `gpt-6-sol / low` 的單次 worker 指定寫入任務合約。第二回合明確續作同任務且沒有新模型指定，從合約恢復。第三回合在新 thread 建立新任務，使用長期專案預設 `gpt-6.1-sol / low`。長期設定完全不變。

**實際：** 第一、二回合的 root thread 相同：`01a172c7-9b29-72f1-8f1f-ed8ef5dbe37a`；第三回合為新 thread `01a172ca-7759-7091-ad3f-4ce1204a0a8b`。

| 階段 | 原生 worker handle | worker session ID | 宿主 session context |
| --- | --- | --- | --- |
| 第一次只完成 T1 | `/root/t1_readonly_check` | `01a172c8-99c0-7bb3-be0f-bfba84d226d3` | `gpt-6-sol / low` |
| 同任務後續回合完成 T2 | `/root/t2_readonly_check` | `01a172c9-cb9b-7c21-b03d-5dae176f134e` | `gpt-6-sol / low` |
| 全新任務 | `/root/preserve_check` | `01a172cb-6491-79f0-9902-ae12207fdb05` | `gpt-6.1-sol / low` |

原合約 `model_overrides` 在前兩回合內容一致；第一回合 T2 為 `pending`，第二回合原任務 `done`。新合約沒有舊任務覆寫。三個 worker 各只有一次啟動與完成；三份設定快照 byte-identical，仍為原專案預設。

**直接證據：** [RPC](unified-project-settings-model-lifecycle-evidence/override/rpc.jsonl)、[session contexts](unified-project-settings-model-lifecycle-evidence/override/session-contexts.json)、[第一回合合約](unified-project-settings-model-lifecycle-evidence/override/artifacts-phase1/docs/plans/scoped-model.task-contract.md)、[恢復後合約](unified-project-settings-model-lifecycle-evidence/override/artifacts-phase2/docs/plans/scoped-model.task-contract.md)、[新任務合約](unified-project-settings-model-lifecycle-evidence/override/artifacts-phase3/docs/plans/new-model-task.task-contract.md)。RPC 第 200、744、1573 行為三個模型啟動事件；不是把請求參數或模型自述當成執行證據。

## M2：同一對話切換主責模型，舊 worker 保留原設定

**預期：** 原 worker 已在執行時改變主責選擇。舊 handle 不變且持續原工作；新派工省略模型與推理強度參數，原生繼承最新主責選擇。

**實際：** root thread `01a172c7-b6b7-7363-bde3-9641b7e1713e` 的第一回合為 `gpt-6.1-sol / low`。第一回合建立 old_worker 並保存 handle、`in_progress` 合約後結束；worker 持續等待尚不存在的 gate。第二回合由測試控制器實際呼叫 `turn/start`，明確傳入 `model=gpt-6-sol`、`effort=medium`。root 的兩筆 session context 確認選擇改變。

| worker | 原生 session ID | 宿主 context | 啟動／完成相對順序 |
| --- | --- | --- | --- |
| `/root/old_worker` | `01a172c8-9f28-7490-8bcc-7848b9477585` | `gpt-6.1-sol / low` | 改變主責前啟動，改變後才完成；同一 ID，沒有重啟 |
| `/root/new_worker` | `01a172c9-8dae-76f3-849d-4da519591060` | `gpt-6-sol / medium` | 主責切換後新建，核對完成 |

RPC 第 199 行為 old_worker 啟動，第 391 行為第二次實際 `turn/start` 控制，第 604 行為 new_worker 啟動，第 978 行為原 old_worker 完成。原合約前後均保留 `/root/old_worker`；gate 只出現在第二回合快照。兩項成果均完成，沒有重複派工。

**直接證據：** [RPC](unified-project-settings-model-lifecycle-evidence/switch/rpc.jsonl)、[session contexts](unified-project-settings-model-lifecycle-evidence/switch/session-contexts.json)、[第一回合合約](unified-project-settings-model-lifecycle-evidence/switch/artifacts-phase1/docs/plans/manual-switch.task-contract.md)、[完成合約](unified-project-settings-model-lifecycle-evidence/switch/artifacts-phase2/docs/plans/manual-switch.task-contract.md)、[agent 產物](unified-project-settings-model-lifecycle-evidence/switch/artifacts-phase2/docs/research/manual-switch.research.md)。

本案使用原生 host API 的實際 user-turn 模型控制，未操作 Desktop 的模型選單；不能據此宣稱 Desktop UI 本身已驗收。受測模型在對話內未看到外部 session metadata，合約誠實留下 observed model/effort 未知；本報告另由宿主事件與 session context 核對，不回寫或美化受測產物。

## M3：候選連同專案預設耗盡，其他成果繼續

**預期：** 相同模型去重；末段自動 default 不遞迴。在角色候選與專案預設均不可用時，獨立 worker 成果 T1 保留未完成並詢問，獨立的主責成果 T2 繼續，不改寫模型設定。

**實際：** 隔離設定的候選為 `[not-a-real-model-unified-primary;low, not-a-real-model-unified-primary;high]`；專案預設為 `[not-a-real-model-unified-default;low, default]`。相應原生 fixed roles 刻意綁定不存在的模型，未覆寫其模型或讓主責冒充獨立審查。

- primary worker `01a172c8-92e7-7881-ab13-6b8636a50937` 只有一次啟動，真實 `turn/completed.status=failed`、provider `model_not_found`。
- default worker `01a172c8-d98e-7110-aa5e-b26862f93c4d` 也只有一次啟動，同樣真實失敗。沒有重試 primary 的 high 版本、遞迴 default，或偷偷加入主責模型。
- 合約 T1 為 `blocked`、T2 為 `done`。T2 實際檔案 byte 精確為 `READY_WORK_DONE` 加 LF，主責最終訊息詢問 T1 的所需決定。`blocked` 是這份任務合約的單項結果，與外部對話 goal status 無關。

**直接證據：** [RPC](unified-project-settings-model-lifecycle-evidence/exhausted/rpc.jsonl) 第 190／217 行為兩次啟動，第 203／230 行為兩次原生 provider 失敗；[session contexts](unified-project-settings-model-lifecycle-evidence/exhausted/session-contexts.json)、[合約](unified-project-settings-model-lifecycle-evidence/exhausted/artifacts/docs/plans/exhausted.task-contract.md)、[不受影響的真實產物](unified-project-settings-model-lifecycle-evidence/exhausted/artifacts/docs/research/independent-ready.research.md)。

## 獨立驗證與限制

[check-evidence.py](unified-project-settings-model-lifecycle-evidence/check-evidence.py) 只讀保存下來的 RPC、session metadata、合約與產物，驗證實際身分／模型、跨回合順序、啟動次數、精確 bytes 與資產保留；不以 fixture 的 `observed_*` 欄位取代宿主證據。[60 項 assertions 結果](unified-project-settings-model-lifecycle-evidence/assertions.json) 全數 PASS。可在同一已授權驗收環境執行：

```sh
python3 docs/research/unified-project-settings-model-lifecycle-evidence/check-evidence.py
```

三案 `summary.json` 均記錄 server 正常 exit 0，原本全域 `auth.json`／`config.toml` 的執行前後 SHA-256 相等，專案設定及 `preserve.txt` 未改。每個臨時 state 是 0700、auth 副本是 0600；程序結束後整個暫存根目錄已刪除，checker 再次獨立確認不存在。歸檔中沒有 auth 檔；checker 以原 auth 的實際長字串值逐檔比對，未發現憑證內容，且不輸出任何值。無全域安裝、既有專案或 remote 變更。

宿主 `turn_context` 與 native start 事件證明本機實際 session 的選擇／繼承，不宣稱能獨立辨識供應商內部模型權重。此補充未驗證 Desktop UI 點選、Windows、真實 hooks 開關恢復、網路中斷或 provider 內部路由；這些不能由本三案推論。測試模型的原生檔案工具屬可用宿主能力，過程中的 inline 命令並非 task-harness 強制安裝的 helper/runtime。無腳本依賴的產品保證仍由隨附 Markdown 流程與完整 T08 其他證據共同驗收。
