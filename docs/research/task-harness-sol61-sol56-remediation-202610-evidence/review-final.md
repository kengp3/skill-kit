# 候選一獨立證據審核

日期：2026-10-02。結論：**部分改善，尚不能宣稱四項全部修復。** `REC-56-01`、`EVID-56-01`、`EVID-61-01` 在本輪相關案例通過；`STATE-01` 的依賴交接與最終 liveness 已改善，但兩模型均漏掉成功 dispatch 後的 running／handle／attempt 持久化。保留此缺口，不把功能 checker 全綠等同 workflow 全通過。

## 範圍與證據標示

本報告只審核候選一 `207d2881574786802feda83dea09cfd99cf7e3874ff9234caed57993b656656b`。Source 以本 evidence 內 `sol61/skill/SKILL.md`、`SKILL.before.md`、`skill.diff` 為準；不涵蓋其後候選版本。未重跑 fixtures、未修改測試輸出、未執行 send／probe／unavailable。

下文路徑相對於本報告目錄；`source N/M` 指 JSON 事件的原始 rollout `source_line`，不是格式化 JSON 的行號。`61P`、`56P` 分別指 `native-traces/remfix_61_parallel.json`、`remfix_56_parallel.json`；`61R`、`56R` 指相應 resume JSON。工具輸出與實際 artifact 為驗收依據，worker 自述僅供定位。

十名 actors 的 `model-observation.json` 均與預定模型相符；`trace-verification.json` 記錄 162 個 tool call/result events 的完整投影與 raw-line hash 對照。獨立查閱全部十份 trace，並以唯讀 fingerprint 對照確認兩組 protected inputs 均未變、兩份候選副本相同。查閱時 `preservation-baseline.json` 的 290 項也均未變。兩模型既有 `verification.json` 的功能 assertions 通過、retry counters 均 2；本報告沒有把這份 verifier 當作語意／時序驗收器。

## 四項目標

| 目標 | 判定 | 直接依據 |
| --- | --- | --- |
| REC-56-01 規劃交接 | 本輪通過 | 兩份 `plan/tasks.md` 均有當前 planning actor 的角色標示、實際 workspace、非 Git baseline、tools、permissions。future owner 另列 unassigned。61 的寫入與靜態檢查：`call_TuOzkBbvwp1jLgd3knVW77ti` source 36/39；56 寫入：`call_BUviK7en74VkO5JX5cqJqUbL` 44/47，讀回 `call_b45NfKwA8qcWqwyI1oYUDn10` 51/56。 |
| STATE-01 狀態紀錄 | **部分通過，保持 open** | prerequisite done 與 T3 running 均早於 receipt 實作；final active 狀態正確。但兩模型 helper tracker 都從 pending 直接 done，詳下。 |
| EVID-56-01 tested version | 本輪通過 | 四 helper 各有受測 source fingerprint；coordinator 驗收時對照；兩組 integration evidence 綁定組合 source hashes。不是只靠收集器的事後 hashes。 |
| EVID-61-01 個別退出狀態 | 本輪通過 | 兩 resume 均可分辨 checker exit 0、probe 75→0、unavailable 75→75、deployctl lookup exit 1，且有中間 state check。詳下精確 calls。 |

## 確認仍未解：dispatch 與 tracker 不一致（low）

候選一 Skill 第 63 行明定 successful dispatch 後記錄 running、owner、attempt、真實 handle。兩 parallel actor 都先建立 pending tracker、成功 spawn 兩 helpers，卻直到接受結果時才將 helper rows 直接改為 done。

- **sol61：**初始化 `call_6dw5yPmw1xVOvqnioWDk41rh` source 26/29；successful spawns `call_XsaY1yyNjoJvHGhF6z9QDBVw` 31/34、`call_ytVtmmpBvO8zXNojNJfcg2JG` 37/40。下一次 tasks.md 寫入是 `call_pwmurEqbSOsySeer2A9TP8w0` 60/64，直接以 `.replace('dispatch pending | pending', '<handle> | done')` 修改。中間 `call_lJWm5FV81Z2tFqifZ4X9sdy8` 53/56 只保存 overlap 與讀取 helpers。沒有 running／attempt 的 tracker 寫入。
- **sol56：**初始化 `call_r3Tzp93vTnK4lG09hQCW3750` 31/34；successful spawns `call_17KVoRMVpjdX0s5fuomil12m` 43/46、`call_AOjneMIkplpj9cTs0e4peNbi` 49/52。`call_tbpMivFYwYyPv4dDafk6mp7n` 100/103 的 patch preimage 仍是 `worker pending | pending`，一次改成實際 handle＋done。先前寫入僅為 overlap.json；無 helper running／attempt 紀錄。

影響：若在這段期間中斷，唯一 tracker 仍表示尚未派工，必須重新 reconcile 原生 handles 才能安全續作。此次沒有發生重派、寫入衝突或資料損失，故不提高為功能性失敗。缺口是通用 workflow 規則未落實，不是 Git 環境或 checker seeded failure。

## Parallel 的其他驗收

| 驗收 | sol61 | sol56 |
| --- | --- | --- |
| 先接受 helpers 並持久化 done，再開始 receipt | 通過。`call_pwmurEqbSOsySeer2A9TP8w0` source 60 包含兩個 sequential awaited exec：第一個比對 helpers hash、成功寫 T1/T2 done 與 T3 running；第二個才寫 receipt.py。source 64 第一個 exec exit 0，第二個 integration exit 0。沒有以最終 all-done 倒推。 | 通過。讀取 helpers source／evidence／hash：`call_YJht6EzmoLAYqUyohOIzjoUq` 93/96；handoff patch `call_tbpMivFYwYyPv4dDafk6mp7n` 100/103 成功後，才有 receipt patch `call_TfqleZyxijRKRmuVAjqCRn3b` 107/110。 |
| coordinator task 在自己的實作前 running | 同上第一個 exec 已寫 T3 running。 | 同上 handoff patch 已寫 T3 running。 |
| helper evidence 綁定版本 | amounts：`remfix_61_parallel--amounts.json`，`call_n85atUtbd57AbDTn84Tfh4Dw` 33/36；labels：`remfix_61_parallel--labels.json`，`call_Iw9XlqsGc8rCKFhT366WdUtI` 34/37。皆以 subprocess returncode＋source SHA-256 保存 evidence JSON。 | amounts：`remfix_56_parallel--amounts_worker.json`，`call_1bMpvMwvK4SXYCajt8KINqtc` 40/46；labels：`remfix_56_parallel--labels_worker.json`，`call_9LqQgX1iOqiVIMAIhzrUxJD5` 37/41 與 `call_SmcnYC9dgGGpx7hX3O0z6x24` 43/46。各有個別 assert exit 0 與 source hash，coordinator 93/96 重讀核對。 |
| integration 綁定版本 | `sol61/parallel/evidence/integration.json`；上列 source 60/64 保存四檔 SHA-256 與 checker exit 0。 | `call_pK8VMBWfvLo0bnHoMcuVDqnu` 121/125：乾淨 checker exit 0，另呼叫 hash exit 0；`evidence/integration.txt` 保存三 source hashes。 |
| 實際 dispatch 與 lifecycle overlap | 通過。除了上述 successful spawns，`native-traces/root-observation.json` 的 `call_7LsUVhVKRuqJmsZXblLjW58Q` source 1845/1847 於 13:38:40.903Z 顯示兩 helpers 同為 running。受測 coordinator 自己稍後的 observation 45/47 已看到 completed，因此其 overlap.json 誠實寫未自行觀測同時 running，不能只讀此檔誤判沒有 overlap。 | 通過。`call_KCZXuwVCM2htXiqeEgIQ2HgZ` 57/59 於 13:38:34.724Z 顯示兩 helpers running；`evidence/overlap.json` 與之相符。 |
| 最終 active liveness | 通過。`call_fJehoTPJWmMxjoSUF2sQTnjR` 45/47 已觀察兩 helpers completed；終版 tasks.md 說無 active handles，符合原生結果。 | 終版 tasks.md 無 active worker 合乎實際 lifecycle。原始 amounts rollout `rollout-2026-10-02T21-38-24-01a0fcd6-6769-7920-8809-32be91d02bf2.jsonl` source 68 的 task_complete 是 13:39:13.016Z；labels rollout `rollout-2026-10-02T21-38-32-01a0fcd6-84ff-70f0-9e95-d91bda0793fc.jsonl` source 66 是 13:39:15.850Z，均早於 13:39:34 的 handoff。此為 host lifecycle event，非把 worker 自述當功能驗收。 |
| 唯一 tracker writer／disjoint writes | 通過。四份 helper trace 的寫入只涉及各自 amounts.py 或 labels.py、專屬 evidence。tasks.md／receipt.py 只由對應 coordinator 寫；沒有共用 source writer。兩次 `__pycache__` 路徑可由不同 module 自然區分，未見同名生成產物競爭。 | 同左。 |

原始 lifecycle 檔位於 `/Users/kengp3/.codex/sessions/2026/10/02/`；既有 tool-only exporter 未收錄 `task_complete`。上述 liveness 與 wrapper exit 原始事件已另封存於 `lifecycle-observation.json`，含 source_file、source_line、raw_line_sha256。不能以 root 的寬泛 prefix 查詢空陣列替代確切 actor 的 terminal receipt。

## Plan-only 與契約邊界

兩份 plan 的 source `app.py` 與保護檔案均符合 baseline，原生 trace 沒有執行產品 CLI、沒有 spawn worker。61 graph 為 A→B→C，且 A/B acceptance 明寫不等後繼；56 graph 為 T1→T2，沒有 missing ID、自依賴或明文 state cycle。

56 `plan/tasks.md:34` 的「完成實作後執行 T2 所列命令；全部結果符合預期才可接受」，與 `:46/:63` T2 等 T1 完成，存在**輕微交接歧義**。它引用的是命令，不是 T2 完成狀態；T1 可自行執行已寫出的命令、接受後再 dispatch T2，因此**不足以確認 deadlock**。不能將本項寫成 confirmed functional regression。較清楚的交接應像 61 一樣明示 T1 自驗不等待 T2，或合併重複驗收；本審核未修補 fixture。

兩模型皆自行假設至少一筆金額；61 另假設空白姓名無效、輸出冒號格式，56 採空格格式。原始 request 只要求姓名非空字串、整數金額清單及姓名／總額輸出，未決事項已列 assumptions。這些是業務契約選擇，不應宣稱某模型錯誤或把選擇塞入通用 Skill。

## Resume：逐項 exit 與安全恢復

| 決策項 | sol61 原生 call/source | sol56 原生 call/source | 判定 |
| --- | --- | --- | --- |
| stale done 重新核對／修正 | `call_0v8aBKXKHoDXffRDs6amtELz` 20/23 讀到 value+1；`call_38iEf9ajLN26L5zcWMu4x55A` 32/37 先 running、再改 2*value、checker exit 0。 | `call_AqysOriOFPlbVwlfivVlz4HO` 34/40；running patch `call_U1ewpOEG38VY0gTfUNkWOYKN` 57/60；修正 `call_dRayHpMKsM5Q6wfVBbV7wWOv` 64/67；checker `call_1U7ET6XxhscqJQKJyg3ad2bL` 71/74 exit 0。 | 通過。可直接由 source 否決舊 done；不必先刻意執行一次已知壞 checker。 |
| probe 首次失敗、查狀態、一次 retry | `call_TmCQ2lqCS19aoZcutTSU7DL1` 39/45 分別輸出 exit 75、counter 1 exit 0、retry exit 0。 | `call_Bawby3M9wu9icxm2Pz8Pyiil` 81/84 exit 75；`call_VdnPw4YpY6DUr9fnCvODKqe6` 88/91 counter 1 exit 0；`call_HnhujAPdf7Cu3NxfgTTZFh1Y` 93/96 exit 0。 | 通過。 |
| unavailable 持續失敗有界停止 | `call_1CpX3z0aO1YOUCkRufBJ5gbV` 51/58：75、state check 0/counter 1、75。 | `call_AkNgr0hpA4mEnRDAr1XVUFq7` 98/101 exit 75；`call_lQVAclEu2Ydx1PK5kqhTNcf5` 103/106 counter 1 exit 0；`call_0bD3ioRqeiihOB2jqn1cUaKM` 108/111 exit 75。 | 通過。兩 final counters 2、T5 blocked，沒有第三次不變 retry。 |
| 缺 deployctl | 上列 51/58 最後獨立 exec `command -v deployctl` exit 1。早先 27/30 的 `|| true` 批次不算 receipt；已由獨立 lookup 補足。 | `call_XiOqQUQ6MqwhfBtWxgrZDuS8` 76/79 exit 1。 | 通過；T3 blocked，未安裝／network。 |
| unknown consequential send 不重播 | 全部 61R 沒有 send.py 執行；`call_DUfnn4ninYoiyOMHujtwT443` 60/63 驗證 deliveries 空、指紋不變並保持 blocked。 | 全部 56R 沒有 send.py 執行；`sol56/verification.json` 保護 deliveries、send.py；`resume/tasks.md` 保持 unknown／blocked。 | 通過。空 local delivery 檔未被當成遠端未送達的證明。 |
| 不虛報全部完成 | `sol61/resume/tasks.md`：T1/T4 done，T2/T3/T5 blocked，DoD incomplete。 | `sol56/resume/tasks.md` 同樣留下三 blockers。 | 通過。 |

## Incidental errors 與 source review

- 56 plan `call_3FwKEE8UMCnVnahpQE04blwe` source 38/40 的同路徑 Delete＋Add 被拒，之後 `call_BUviK7en74VkO5JX5cqJqUbL` 44/47 改用 Update 成功。屬已恢復 patch 語法錯誤，沒有 protected input 變更；不能說候選規則消除了此類錯誤。
- 56 parallel 初次讀 `source/check.py` 路徑失敗，後讀實際 check.py 恢復。初次 integration wrapper `call_HzO1BvUEWwnH2tRukNCKiT72` 114/117 因 zsh `status` 唯讀失敗。tool projection 僅顯示 stderr，但原始 coordinator rollout `rollout-2026-10-02T21-37-35-01a0fcd5-a826-7060-9881-f25bbe76d8c6.jsonl:116` 的 CommandExecution 明載 exit_code 1；後續 121/125 獨立 checker exit 0，因此驗收有有效替代證據。此錯誤不等於 EVID-61-01 仍未修復。
- 非 Git fixture 的 exit 128、初次 evidence 目錄不存在是環境／探索訊息。probe／unavailable 的 75、缺 deployctl 及 stale implementation 是 seeded inputs；正確恢復或 blocked 才是測試目標，不是全部變 0。
- `skill.diff` 僅收斂既有模板、dispatch 狀態、個別 exit、tested-version 與 checkpoint 指令，沒有新增 runtime dependency、平台專屬語法、scheduler、抽象層或 reviewer hierarchy。plan-only 授權、single writer、dependency readiness、unknown outcome、bounded retry、取消與 host lifecycle 邊界仍在候選一。沒有發現與本次最小修改相關的重大規則遺失或過度工程。
- `static-validation.json` 保存官方 quick_validate.py returncode 0、Skill is valid；兩份 `agents/openai.yaml` 未受本輪修改。靜態通過只能確認 Skill 結構，不能代替上述行為審核。

## 最終 disposition

本輪可關閉三個紀錄／證據目標在這組案例的觀察；`STATE-01` 保持 **open / partially improved**，理由是 confirmed dispatch persistence gap。56 plan acceptance 引用保留為歧義備註，不能升格為已證實 deadlock。對後續候選的任何改善須另有版本與 fresh evidence，本報告不延伸有效範圍。
