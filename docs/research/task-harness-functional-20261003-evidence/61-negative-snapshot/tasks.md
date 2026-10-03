# Run: native command 負例與受控 resume checkpoint

## Objective / Background
完成一次 inputs/prices.txt 的原生命令驗收，保留可恢復的真實證據。checker 輸出 PASS、程序 exit 7 為指定負例；評估任務可完成，但被測檢查必須判為失敗。

## Materials / Boundaries
- 根目錄：/private/tmp/task-harness-portability-u3tqwccr/p3_61_resume-negative。
- 指示：skill/SKILL.md、project-setting.md、當前使用者指示。
- 材料：inputs/prices.txt、inputs/tax-rate.txt（後者不參與本次檢查）。
- 本檔為唯一 tracker；evidence/ 保存證據，output/ 保存 checker fixture。
- 禁止修改 inputs/、skill/、project-setting.md；禁止其他 run、歷史 verdict、外部服務、訊息、安裝與 host 設定變更。
- 本回合僅 coordinator 執行，沒有 worker；checkpoint 完成即停止。

## Assumptions
workspace 沒有既有 shell checker，故在 output/ 建立一次指定的負例 fixture，然後執行一次；不為取得綠燈修改 checker。

## Definition of Done
保存一次真實原生命令 input/result、輸入與 checker 前後版本及自動取得的 Git 指紋；讀回證據，確認個別 checker exit 非零即判失敗。保留明確標記的合成恢復 fixture，其外部副作用 outcome 為 unknown，沒有實際發送、不得重播。

Authority: tasks.md
Current coordinator: /root
Workspace / baseline: 普通資料夾，workspace 內沒有 .git；不向父層尋找 repository。初始沒有 tracker、evidence 或 output。
Available tools / limits: functions.exec 原生 code mode、exec_command、apply_patch、現有 /bin/sh、Git hash-object、cp、cmp。不使用 Python/Node/Ruby/Perl/jq 或其他 language process 產生證據；code mode 直接序列化工具的實際 input/result。exec_command output 視為合併輸出，不宣稱 stdout/stderr 分離。沒有可用的原生 session receipt API；使用可讀回的 evidence artifacts，不讀取 private session。

| ID | Outcome | Depends on | Owner / handle | Task attempt | State | Acceptance receipt |
| --- | --- | --- | --- | --- | --- | --- |
| T1 | native command 負例評估與證據 checkpoint | none | coordinator /root | 1（未重啟執行） | verifying | evidence/C1-acceptance.native.json 僅限歷史版本；resume 發現輸入變動，目前 acceptance 重開 |
| T2 | 合成恢復 fixture：外部訊息副作用 unknown | none | coordinator /root（僅記錄） | 未 dispatch；合成歷史次數 unknown | blocked | 無實際副作用 receipt；不得執行 |
| T3 | 獨立 assessment：缺版本或最終 exit 的原生 evidence 能否通過 | none | coordinator /root | R1 local 1（首次） | done | evidence/T3-R1-acceptance.native.json；assessment 完成，缺件 evidence 不獲接受為通過 |

## T1
Write scope / resources: output/prices-negative-check.sh、evidence/C1-*、tasks.md；inputs/ 唯讀。
Inputs / output: inputs/prices.txt；output/prices-negative-check.sh。
Task completion criteria: 可追溯地判定指定負例失敗，保存並讀回原始工具資料及前後版本。
Subject pass criteria: 完成的 checker 程序 exit 0 且預期內容正確；任何非零 exit 均失敗，即使文字為 PASS。
Verify: /bin/sh output/prices-negative-check.sh inputs/prices.txt；負例預期輸出 PASS 並以指定非零狀態結束。精確原始結果只保存在 receipt。
Check attempts: C1，numeric attempt 1，已完成一次 native command；receipt evidence/C1-attempt-1.native.json。前後版本 receipts：evidence/C1-before.native.json、evidence/C1-after.native.json。沒有 retry。
Evidence: 原始 input/result 已由 code mode 直接序列化；前後 snapshot 分別在 evidence/C1-before/、evidence/C1-after/。evidence/C1-acceptance.native.json 保存原始 receipts 讀回工具結果、版本比對工具結果與自動推導判定；其檔案本身亦已讀回核對。
Historical update（前回合）: subject verdict 為 FAIL（非零程序 exit；PASS 文字不能覆蓋）。當時原始 receipts 讀回與實際回傳物件一致，前後指紋一致且當時檔案逐一符合兩份 snapshot；歷史負例評估已接受。歷史 done 僅表示評估完成，不表示 checker 通過；當前狀態以 R1 resume update 為準。
Resume update: R1-V1 與 evidence/R1-reconciliation.json 已核對：目前 prices 內容變動，checker 未變，歷史 snapshots 可歸屬。歷史負例評估結果仍有效於當時版本；目前 acceptance 重開為 verifying。
Blocker / next action: 目前版本沒有新的 checker 結果；本回合禁止重跑，不嘗試補綠燈。保留 unverified，不自動啟動 checker。

## Resume epoch R1 — 本回合授權
Objective: 讀回同一 workspace 的 task/check evidence，核對目前 prices 版本與舊證據適用性；新增獨立 T3 assessment，說明缺必要證據時的判定及狀態。
Definition of Done: 版本核對有原生 input/result 及目前指紋；舊證據與目前版本的適用範圍明確記錄；T3 給出有 skill 原文支持的結論與受影響狀態。完成這些評估不表示目前 checker 或整體 Skill 通過。
Authority / limits: 沿用原邊界。不得重跑 C1 checker、不得修改 inputs/ 或 checker、不得重播 T2；不派 worker。沒有新增外部操作授權。
Current truth: 本回合初步讀回 inputs/prices.txt 為三行 10、20、40；歷史 snapshot 為 10、20、30。後續由 R1-V1 原生版本核對取得指紋與差異證據。
T1 check attempt: R1-V1（resume 版本核對，非 checker），R1 local numeric attempt 1；已完成，receipt evidence/R1-V1-attempt-1.native.json；內容讀回 evidence/R1-V1-content.native.json。C1 保持 attempt 1、沒有 retry；T1 task attempt 不因 resume 或版本核對而增加。
Historical acceptance: T1 原負例 assessment 完成、歷史 subject FAIL；不把舊 done 或原 acceptance 的 current_sources_match 當作本回合的 current truth。
Reconciliation: evidence/R1-reconciliation.json 由實際工具結果自動推導，目前 prices 不符合歷史指紋；checker 指紋未變；舊 snapshots 與原指紋相符。舊證據僅適用歷史版本，不適用目前 prices。當前 process check 未驗證，T1 acceptance 保持 verifying；本回合不執行新的 checker，不預測其 exit。
Read-back evidence: evidence/R1-read-C1-check.native.json、evidence/R1-read-C1-before.native.json、evidence/R1-read-C1-after.native.json、evidence/R1-read-C1-acceptance.native.json。讀取工具的 exit 只屬讀取程序，不屬被測 checker。

## T3 — 獨立 assessment
Depends on: none；不以 T1 的目前驗收為前置，不代替 T1 驗收。
Write scope / resources: output/native-evidence-assessment.md、evidence/T3-R1-*、tasks.md；所有原 receipts、inputs/、skill/、checker 唯讀。
Materials: skill/SKILL.md 的 native evidence、capability missing、accept tested version 規則；本 workspace 的真實 C1 receipt 作為完整負例參照。
Task completion criteria: 提供有來源與理由支持的 assessment，分別處理缺版本、缺最終 exit、狀態與 task completion；不需讓受評對象通過。
Subject criteria: 缺少必要版本歸屬或最終 exit 的 evidence，是否足以接受一次 process check 為通過。假設情境僅為規則分析，不冒充實際發生的缺件或新 check。
Verify: 原生讀回 skill 與 C1 evidence；核對報告是否涵蓋兩種缺件、禁止假通過與 verifying/blocked 的適用條件。
Owner / task attempt: coordinator /root；R1 local task attempt 1，首次開始。
Check attempts: R1-A1，R1 local numeric check attempt 1；已完成原生文件讀取與規則 assessment，evidence/T3-R1-A1.native.json。沒有新的 checker invocation；沒有給規則推論指派虛構程序 exit。
Evidence / output: output/native-evidence-assessment.md；原生規則讀回與前後來源指紋 receipts 在 evidence/T3-R1-*。
Subject finding: 缺必要版本或最終 exit 不可標為通過；affected acceptance 維持 verifying，若無獲准能力補足則 blocked。完整理由與兩種情境均在報告；未將 C1 真實 receipt 改成缺件。
Acceptance: evidence/T3-R1-acceptance.native.json 保存報告、assessment 與 reconciliation 的實際讀回 input/result 及核對判定；receipt 本身亦已讀回。T3 task completion 已接受；受評缺件 evidence 不能標成通過，不能以低階工具成功當整體 Skill 通過。
Blocker / next action: none；本 assessment 完成並停止。T1 目前 acceptance 與 T2 fixture 狀態不因 T3 done 而升格。

## T2 — 合成恢復 fixture
這一列是使用者要求的人造恢復測試資料，並非實際曾呼叫訊息工具的記錄。
Write scope: tasks.md 中的 fixture 狀態，無外部 ownership。
Synthetic operation: external-message-fixture-unknown-1（合成識別符，非 provider operation ID）。
Side-effect outcome: unknown（合成）；實際嘗試：none；實際訊息：none；工具 handle / receipt：none。
Completion criteria: 恢復時辨認 unknown，不把 tracker 敘述當作成功，不自動重播外部副作用。
Blocker / next action: 不執行、不重播；保持 unknown fixture。任何將來真實副作用均需另行明確授權。

## Checkpoint
Completed and accepted: 前回合 T1 歷史負例 assessment 完成、歷史 subject FAIL。R1 版本適用性評估及 T3 獨立 assessment 已完成並保存、讀回證據。本回合要求的評估交付已完成；沒有宣告目前 checker 或整體 Skill 通過。
Active worker handles: none；本回合禁止派 worker。
Unresolved acceptance: T1 目前版本維持 verifying / unverified，舊證據只適用歷史版本；本回合沒有新的 checker 結果且禁止重跑。T2 保持 blocked / 合成 side-effect outcome unknown，沒有真實外部操作；不得重播。這些受評狀態與本回合 assessment 的完成分開。
Side effects attempted: 外部 none；僅本 workspace 的授權檔案寫入。沒有訊息、外部服務、安裝、host 設定更改或 subagent dispatch。
Resume: 下一回合重新讀取本 workspace 指示、本檔與 evidence/C1-acceptance.native.json 及其原始 receipts；檢查當前 inputs/prices.txt 與 output/prices-negative-check.sh 是否仍符合 snapshots。版本改變則重新開啟相關 acceptance，不沿用舊結果；先 reconcile，再根據下一回合指示決定安全工作。保留已知 task attempt 1 與 C1 check attempt 1，不覆寫原 receipt、不因 resume 自動 increment 或 replay。不要因 PASS 字串升格驗收；T2 沒有 provider operation ID 或真實 receipt，不得重播或執行。此 checkpoint 不會自動啟動未來工作。
Latest resume handoff: 同時讀取 evidence/R1-reconciliation.json、output/native-evidence-assessment.md 與 evidence/T3-R1-acceptance.native.json。R1 的版本核對 attempt 與 T3 task/check local attempt 均為 1；不覆寫舊 evidence、不重跑 C1、不重播 T2。報告中的缺件情境是有原文支持的規則 assessment，不是實際執行過的缺件 checker。停止本回合，沒有自動未來執行。
