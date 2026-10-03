# 原生 evidence 完整性 assessment 與 resume 結果

本回合已完成版本適用性與證據完整性評估。缺必要版本或缺 checker 最終 exit 的 evidence **不能標成通過**。這是有來源支持的評估結論，不是整體 Task Harness 通過宣告。

## Resume：歷史證據的適用範圍

目前 `inputs/prices.txt` 為三行 `10`、`20`、`40`；歷史 snapshots 為 `10`、`20`、`30`。原生 Git 指紋核對顯示 prices 版本不同，checker 版本相同，歷史 snapshots 仍符合原 receipts。

[C1 原始 receipt](../evidence/C1-attempt-1.native.json) 仍證明歷史版本的 checker 輸出 PASS、最終 exit 非零，歷史 subject verdict 為 FAIL。[原 acceptance](../evidence/C1-acceptance.native.json) 的版本一致結論只描述前回合當時的版本；resume 不能把它沿用為目前版本一致。

[R1 原生版本 receipt](../evidence/R1-V1-attempt-1.native.json)、[目前內容 receipt](../evidence/R1-V1-content.native.json) 與[reconciliation](../evidence/R1-reconciliation.json) 保存目前讀回、指紋及自動推導判定。沒有重跑 checker，因此目前版本的 process check **未驗證**；不能從檔案讀取或 Git 指紋工具成功推導 checker 成功。T1 歷史評估完成的事實保留，但目前版本的 acceptance 重開為 `verifying`。

## T3：缺必要 evidence 能否通過

本 assessment 獨立於 T1 當前 process check，不依賴其通過，也不替代其驗收。以下兩種缺件是規則分析情境，並非把真實 C1 receipt 改成缺件 fixture；C1 原 evidence 實際包含版本資料與最終 exit。

| 情境 | 能否標成通過 | 理由 | 受影響狀態 |
| --- | --- | --- | --- |
| 缺可歸屬的受測版本，包括必要的前後版本或 snapshot/fingerprint | 不能；版本驗收未驗證 | 無法把結果綁定到實際受測內容，也無法確認目前接受的是同一版本。檔案路徑或 PASS 字串不是版本證據。 | 取回並核對既有版本證據期間為 `verifying`；若沒有獲准能力取得必要歸屬，則 `blocked`，具體 blocker 是缺版本證據。 |
| 缺 checker 自己的最終 exit | 不能；最終結果 unknown | 無法確定程序已完成或成功。PASS 字串、執行中 session、wrapper 成功及讀回檔案的 exit 都不能代替 checker 最終 exit。不能人工補 exit。 | 取回原生最終結果與 reconcile 期間為 `verifying`；若在可用能力與授權內無法恢復，則 `blocked`，具體 blocker 是缺最終結果。 |

只有已有可恢復原始證據時才能補足歸屬或結果；不能把人工抄值當原始 receipt。本回合明確禁止重跑 C1，所以不能以新執行來填補舊 evidence。unknown 外部副作用亦不得為補證據而重播。

如果已知原程序 exit 非零，即使其他資料缺失，也不能因輸出 PASS 把該歷史程序改判通過；版本歸屬缺失仍使目前版本驗收未確認。證據不完整本身也不等於已觀察到受測程序以非零退出，必須分開 `FAIL` 與 `unverified/unknown`。

## 依據、任務狀態與限制

依據 [skill/SKILL.md](../skill/SKILL.md) 的 Execute, verify, integrate：第 3 點 Native evidence first 要求實際工具 input、最終 result、cwd、前後可歸屬版本；明定非零 exit 即失敗、missing results/unknown 不是 pass。Capability missing 與第 4 點要求缺必要驗證時維持 `verifying` 或 `blocked`。Decompose 與狀態表明定 assessment 可以因交付有支持的負面結論而完成。

[T3 原生 assessment evidence](../evidence/T3-R1-A1.native.json) 引用獨立原生讀取工具 receipts，保存 skill 與 C1 原 evidence 的前後自動指紋，及規則核對結果。這是一份文件與規則 assessment，沒有新的 checker process，也沒有為 assessment 虛構 checker exit。

- T3：提供有來源支持的結論與受影響狀態後，可標記 `done`；受評缺件 evidence **不獲接受為通過**。
- T1：歷史負例 assessment 已完成；歷史 subject FAIL；目前版本 acceptance `verifying`，目前 checker 未驗證。
- T2：維持 `blocked` 與明確標記的「合成恢復 fixture」副作用 `unknown`；沒有實際訊息或外部操作，也沒有重播。
- 本回合的 resume 與獨立 assessment 交付完成，不表示整體 Skill 通過；檔案讀回成功、低階工具 exit 成功及保存 checkpoint 均只證明各自有限的操作結果。

此為共用宿主普通功能 smoke 的局部證據，不宣稱盲測、強隔離、原子 snapshot 或獨占 reservation。原生工具提供的是 command string 與合併輸出，沒有 argv 級或獨立 stdout/stderr 保證。未派 worker、未讀其他 run/歷史 verdict、未使用外部服務或額外 language process。
