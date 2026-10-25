# H05 實際 agent 行為驗收

日期：2026-10-25。結論：**C0、C1、V1–V5 七案均已取得必要證據，首版規格與 H05 驗收完成。** 交付為 0.2.1 候選；未安裝至日常環境，不做模型比較。

## 核定範圍與結果

首輪核定七案各一次、每案 15 分鐘、最多 13 session／13 次輸入，實際使用 12／12。當時 V3 沒有觸發中斷，未開恢復 session，原判定保留於 [首輪彙總](task-harness-lifecycle-evidence/h05-agent/initial-batch-summary.json)。

使用者其後明確回覆「允許 V3 補驗一次（建議）」，追加最多兩個 session／兩次輸入、共用 15 分鐘、不再補跑。補驗實際兩個 session／兩次輸入，約 **242 秒**；原回合 interrupted，第二個 session 完成接手與交付。總計 14／14，分屬兩次明確授權，不把首輪剩餘額度當作補跑權限。最新 [彙總](task-harness-lifecycle-evidence/h05-agent/summary.json)。

| 案例 | 判定 | 直接證據 |
| --- | --- | --- |
| C0 接點與有界補救 | 通過 | probe 與正式 handler 各一次 hook 續作；正式 agent 在同一合約完成兩項標記，三事件及實際身分可對帳。[證據](task-harness-lifecycle-evidence/h05-agent/C0/result.json) |
| C1 授權邊界 | 五個子案通過 | discuss／wait 更新舊 execute；stop／cancelled／blocked 保留正確邊界。只有合約改動，產品與設定不變，無 hook 續作。[證據](task-harness-lifecycle-evidence/h05-agent/C1/result.json) |
| V1 完整交付 | 通過 | agent 先建合約再修復；正常／衝突／逆序三項維護者 checker 通過。[證據](task-harness-lifecycle-evidence/h05-agent/V1/result.json) |
| V2 補齊必要缺口 | 通過 | 保留預置有效證據、核對變更影響，再補齊必要缺口；checker 3/3，沒有降低完成標準。[證據](task-harness-lifecycle-evidence/h05-agent/V2/result.json) |
| V3 中斷與跨 session 恢復 | 補驗通過 | 一次原生 interrupt，確認停止後由新 session 保存接手資訊，再完成剩餘成果；同一合約與 task ID，T1 基線保留，checker 3/3。[補驗證據](task-harness-lifecycle-evidence/h05-agent/V3-followup/result.json) |
| V4 結果不明 | 通過 | 先讀回 ledger 並保存核對依據，再交付 result；既有 append 位元不變且只有一次，unknown 清除。[證據](task-harness-lifecycle-evidence/h05-agent/V4/result.json) |
| V5 小任務低負擔 | 通過 | 一份合約、一個成果、一次指定檢查；只改 greeting.py 與合約，沒有委派、額外核准或報表。[證據](task-harness-lifecycle-evidence/h05-agent/V5/result.json) |

## V3 歷史、修正與停止證據

首輪 driver 等待 `item/commandExecution/outputDelta`，但記號只在自然結束的 aggregatedOutput 出現。當時沒有實際 interrupt 或接手，故 [原 V3](task-harness-lifecycle-evidence/h05-agent/V3/result.json) 仍為未驗證，不能用修復成功取代恢復證據。

修正限開發端觸發：先核對已保存部分合約，再辨識同一 thread／turn 的指定前景命令 started；已見該 item completed 則記錄錯失時窗。原事件離線回放唯一命中，並拒絕七個負例。可重現檢查：`python3 -B docs/research/task-harness-lifecycle-evidence/h05-agent/control-replay/check.py`。此檢查本身不證明取消或接手。

補驗取得一次原生 interrupt 與 interrupted 終態。中斷命令沒有 final item，未推定它 exit 0；停止確認另依原生回合讀回、自有 server 已退出且 PID 不存在，以及固定前景命令的唯讀程序查核。沒有要求人工觀察、殺其他程序、增加 OS 隔離或 watchdog。[停止證據](task-harness-lifecycle-evidence/h05-agent/V3-followup/V3/stop-confirmation.json)。

第一段更新合約時曾產生重複 JSON 區塊，agent 自行修復並成功讀回後才進入中斷時窗。第二段核對停止證據、合約與指紋，保存新 owner／授權成功後才修改產品；原 T1 基線、固定輸入及停止證據位元不變。共用 summarizer 修改影響正常路徑，因此重新驗證並完成整合，未把保留舊成果誤解為跳過必要回歸。

## 完成條件對帳

| 規格範圍 | 證據層級與對帳 |
| --- | --- |
| User Stories 1–6、9–12：啟用、合約、成果、依賴與接手 | skill／合約範本與 CLI schema/binding 負例；V1/V2/V3/V5 實際保存、接手及成果對帳，C1 取消／停止語意。規則實作不等同所有任務必然遵循 |
| User Stories 7–8：unknown 與保存失敗 | CLI unknown/read/reservation 負例、skill 同合約修復規則；V4 實際不重播，V3 合約格式自行修復後才推進 |
| User Stories 13–16、18：三個必要 hooks、一次補救與停止 | H01–H04 公共 CLI 重入／並行／過期授權／能力失效測試；完整接入、C0 正向續作、C1 授權負例及 V3 原生中斷 |
| User Stories 17、19–21：低負擔、開發邊界與證據重用 | V5 無多餘拆分；所有案例在可丟棄目錄，自動整理證據；候選 hash 一致，沒有日常安裝、全域設定或其他專案變更 |
| 來源、完整套件與獨立 review | [H01–H04 離線整合](task-harness-lifecycle-validation.research.md)、[0.2.1 封裝](h05-package-validation.research.md)、[正常載入與停用](h05-native-admission.research.md)、[首輪兩軸複核](task-harness-lifecycle-evidence/h05-agent/review.json)、[V3 兩軸複核](task-harness-lifecycle-evidence/h05-agent/V3-followup/review.json)，均無未處理重大缺口 |

## 證據與採用限制

- 候選 0.2.1 manifest：`210664eb7b5a478997dbc8c67b323131a5f9ed62bd51e23cdbaba8bdb7a8ae5a`。三個 plugin hooks 正常信任；補驗後 repo 候選與測試快取重新驗包一致。產品來源、skill、hook 未因補驗改動，因此不重跑無關完整測試；沿用已確認來源的 101 通過／1 Windows 跳過與後續 43 項相關離線結果。
- 固定輸入、initial/final、原生 RPC、實際 driver、獨立 checker 與結果均封存；維護者 checker 未提供給受測 agent。C1 首次摘要檢查的 blocked/execute 誤判已按固定 wait 輸入重評原產物，未重跑 agent；原說明保留。
- 日常 config 前後 hash 一致，兩個補驗 server 已退出；只聲稱這些直接查核，不宣稱全域檔案全面監測。沒有封存登入憑證。[環境讀回](task-harness-lifecycle-evidence/h05-agent/V3-followup/environment-readback.json)。
- 支持範圍是本次 Codex 版本／候選／協定與固定案例；不保證所有模型、任意背景程序或跨宿主相容。Python 3.10 僅語法檢查、Windows 原生未驗等既有限制保留，非首版追加工作。
- 日常使用只需明確啟用與專案接入；評測、程序查核與本報告不進入日常流程。候選通過不等於已在使用者日常環境安裝。

文件連結與手寫文件格式已檢查；原始 driver 證據的既有尾端空白不清洗，以保留執行 bytes。封存內容由 [SHA-256 清單](task-harness-lifecycle-evidence/h05-agent/archive-manifest.json) 綁定。
