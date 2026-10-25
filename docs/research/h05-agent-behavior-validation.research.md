# H05 實際 agent 行為驗收

日期：2026-10-25。結論：**6 案通過，V3 中斷與跨 session 恢復未驗證，H05 保留未完成。** 沒有發現需更換模型的證據；剩餘問題在開發端控制觸發，不擴充產品架構。

## 固定範圍與結果

使用者已核定 C0、C1、V1–V5 各一次、每案 15 分鐘，共最多 13 session／13 次輸入。本次實際 12／12；V3 未取得原生中斷證據，因此沒有開續作 session，沒有造停止證明或整案重跑。當前原生預設 agent 只用於驗行為，不做模型比較。各案均在原期限內，實測時間及計數見 [彙總](task-harness-lifecycle-evidence/h05-agent/summary.json)。

| 案例 | 判定 | 直接證據 |
| --- | --- | --- |
| C0 接點與有界補救 | 通過 | probe 與正式 handler 各一次 hook 續作；正式 agent 在同一合約完成兩項標記，三事件及實際身分可對帳。[證據](task-harness-lifecycle-evidence/h05-agent/C0/result.json) |
| C1 授權邊界 | 五個子案通過 | discuss／wait 更新舊 execute；stop／cancelled／blocked 保留正確邊界。只有合約改動，產品與設定不變，無 hook 續作。[證據](task-harness-lifecycle-evidence/h05-agent/C1/result.json) |
| V1 完整交付 | 通過 | agent 先建合約再修復，正常／衝突／逆序三項維護者 checker 通過後獨立對帳。[證據](task-harness-lifecycle-evidence/h05-agent/V1/result.json) |
| V2 補齊必要缺口 | 通過 | 保留預置有效證據、核對變更影響，再完成必要缺口；checker 3/3，沒有把缺口降為建議。[證據](task-harness-lifecycle-evidence/h05-agent/V2/result.json) |
| V3 中斷與跨 session 恢復 | 未驗證 | 固定前景命令自然結束，沒有實際 interrupt 或接手；修復 checker 3/3 不替代恢復證據。[證據](task-harness-lifecycle-evidence/h05-agent/V3/result.json) |
| V4 結果不明 | 通過 | 先讀回 ledger 並保存核對依據，再交付 result；既有 append 位元不變且只有一次，unknown 清除。[證據](task-harness-lifecycle-evidence/h05-agent/V4/result.json) |
| V5 小任務低負擔 | 通過 | 一份合約、一個成果、一次指定檢查；只改 greeting.py 與合約，沒有委派、額外核准或報表。[證據](task-harness-lifecycle-evidence/h05-agent/V5/result.json) |

## 唯一剩餘項

V3 driver 原先等待 `item/commandExecution/outputDelta` 的文字記號；本次記錄沒有該事件。已保存部分合約後，原生 `item/started` 可見指定等待命令進入 inProgress，約 29.9 秒後 `item/completed` 才以 aggregatedOutput 回報記號、exit 0。agent 依固定輸入的自然結束分支完成修復，沒有抵抗停止，也沒有證據可判產品失敗。

最小開發端觸發修正已離線完成：**核對部分合約已保存，加上同一 thread／turn 的指定命令 started，觸發一次原生 interrupt**；已見該 item completed 則保留錯失時窗。已以本次事件離線回放驗證：唯一命中指定 started，確認其前有部分合約讀回，並拒絕 7 個身分／事件／命令負例。可重現檢查為 `python3 -B docs/research/task-harness-lifecycle-evidence/h05-agent/control-replay/check.py`；[結果](task-harness-lifecycle-evidence/h05-agent/control-replay/result.json)只證明觸發識別，不證明實際取消或接手。剩下僅需一次 V3 補驗的明確額度。原授權禁止整案補跑，本輪不自行追加；不用換模型、不重跑六個已通過案例、不加 OS/watchdog 或通用 runner。原始 driver 凍結在各案證據中；修正版另存 control-replay，沒有啟動它或把舊 V3 改寫成通過。

## 證據與限制

- 指定產品：0.2.1，manifest `210664eb7b5a478997dbc8c67b323131a5f9ed62bd51e23cdbaba8bdb7a8ae5a`。原生載入為三個 trusted plugin hooks；試行後快取內容重新驗證一致。沒有產品來源變更或新候選。
- 固定輸入、initial/final、原生 RPC、控制 driver、直接 checker 輸出均保存於 [證據目錄](task-harness-lifecycle-evidence/h05-agent/summary.json)。維護者 checker 不放入受測工作副本；V1/V2/V3 各獨立執行三項判準，沒有因 checker 誤判重跑 agent。C1 初次摘要檢查把 blocked 授權誤寫 execute，按固定輸入修正為 wait 後重評原產物，保留說明。
- Standards 與 Spec 獨立審查沒有需修正的產品問題，均確認 V3 保留未驗證；[審查摘要](task-harness-lifecycle-evidence/h05-agent/review.json)。回合 completed、產品 done 與整體驗收分開判定。
- 接入使用可丟棄 CODEX_HOME 與各案工作目錄；沒有安裝至日常環境。原生日常 config 僅做前後 hash 比對，不宣稱全面監測全域檔案；未封存登入憑證，不要求人工監看。
- 這些是明確提示的固定案例與指定版本證據，不證明普遍成功率、省時幅度、任意宿主或模型相容性。Python 最低版本／Windows 等既有未測限制沿用原報告。

文件相對連結檢查通過；手寫文件 `git diff --check` 通過。完整 archive 的 check 僅指出 11 份 driver 證據複本第 16 行既有尾端空白，為保留實際執行 bytes 未清洗；不影響執行結果。封存內容由 [SHA-256 清單](task-harness-lifecycle-evidence/h05-agent/archive-manifest.json) 綁定。最終獨立文件複核確認狀態與計數一致。
