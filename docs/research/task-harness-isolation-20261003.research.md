# Task Harness 隔離續作與驗收紀錄

日期：2026-10-03。狀態：隔離診斷與原模型 plan-only 續作已完成；沒有啟動產品執行或其他矩陣案例。候選不變，尚未取得 portable Core 發布許可。

## 已確認的診斷

原 profile 已生效，但沒有阻止 `/private/tmp` 的 scope 外讀取。這不是僅靠 `test -r` 得到的假陽性：同一 canary 在 `codex sandbox` 下實際 `/bin/cat` 成功。前輪比較同時改變了入口、profile 與目標位置，因此不能將差異歸因 `codex exec`。

| 對照 | 實際觀察 | 意義 |
| --- | --- | --- |
| 原 session 的有效 metadata | `portability_p3`、root deny、minimal read 及案例 allow 都存在 | 不支持 profile 未載入的假設 |
| 同一 canary、原 profile、直接 sandbox | 實際取得測試字串，cat exit 0 | 真正的 scope 外讀取，非 metadata-only 誤判 |
| 增加 fixture parent explicit deny | own input exit 0；canary exit 1／Operation not permitted | 目標路徑的明確 deny 可修正這個測試設定 |
| 明確 deny `/private/tmp` 與 `/private/var/tmp`，只 allow 本案例 | own input exit 0；canary exit 1 | 也封住其他暫存案例的廣域 scratch 存取 |
| 原 session resume，使用修正 profile | cat canary exit 1；view_image 同路徑被拒；list_agents 僅 `/root` | 模型實際工具路徑的有限 preflight 成立 |

原始結果：[有效設定](task-harness-isolation-20261003-evidence/effective-context.json)、[原 profile actual read](task-harness-isolation-20261003-evidence/direct-sandbox-actual-read.json)、[parent deny](task-harness-isolation-20261003-evidence/direct-explicit-parent-deny.json)、[tmp deny](task-harness-isolation-20261003-evidence/direct-tmp-deny.json)、[resume 啟動參數](task-harness-isolation-20261003-evidence/resume-preflight-launch.json)。

## 根因與修正邊界

本機是 codex-cli 0.160.0。對應 release tag 的 [seatbelt.rs](https://github.com/openai/codex/blob/rust-v0.160.0/codex-rs/sandboxing/src/seatbelt.rs#L846) 在 process platform defaults 下加入 scratch roots；[seatbelt_scratch.rs](https://github.com/openai/codex/blob/rust-v0.160.0/codex-rs/sandboxing/src/seatbelt_scratch.rs#L31) 涵蓋 `/private/tmp` 與 `/private/var/tmp`，並把明確 unreadable paths 加入 exclusions。上述實測與這個機制一致。

修正只有 CLI 單次 profile 的 explicit deny；沒有修改全域 config、sandbox 程式、hooks 或 Skill。未繼續執行先前提出的非 tmp 搬移對照，因為原位置的明確 deny 已直接解決問題，避免再引入 workspace 變因。

這不是所有工具與平台的安全認證。已測 command、view_image 的檔案拒絕及當次 agent registry；未宣稱其他宿主、任意 MCP 或攻擊性繞過都已驗證。code mode 的 under-development 警告仍保留，沒有證據將本次問題歸因於它。

## 後續驗收邊界

沿用原 coordinator session `01a101fd-fb50-7c41-9bda-7d64a282e847`，不是新建一筆模型樣本。候選 SKILL.md SHA-256 仍為 `970a338e499945b21d8ac045f1ed34fdda25e8d6c431735a3fb5d71a3c89d182`。原矩陣与歷史 Inconclusive 保留，本次以新 evidence 記錄基礎設施設定修正後的續作。

Git 在受限 session 回傳 xcrun developer path 錯誤，但外層宿主 `git --version` 可成功；因此只能記為受限環境的工具能力問題，不能据此斷言宿主未安裝 Git／CLT。模型已找到可用的 `cksum`。其指紋適用本次來源變更檢查，不作抗碰撞或抗竄改保證。

原 C1–C8 與固定停止條件不變；沒有新增 candidate、reviewer 階層或 retry-for-green。隔離 preflight 通過不等於 Skill 功能通過；真正 plan-only、執行、resume 與安全 gates 仍須各自取得直接證據。

## 本次收尾與使用者最新方向

原 session 已正常结束，CLI events 含 turn.completed。已產生 tasks.md 與規劃材料 receipt；T1/T2/T3 均 pending，沒有 output 產品或 worker dispatch。保存[plan-only 快照](task-harness-isolation-20261003-evidence/plan-only-snapshot/tasks.md)、[原生工具 evidence](task-harness-isolation-20261003-evidence/selected-native-evidence.json)及[稽核](task-harness-isolation-20261003-evidence/diagnostic-audit.json)。研究端讀取 session 只供本次稽核，受測 Skill 沒有依賴 private session export。tracker 對 CLT 缺失的說法過強，正確限制見上文；保留原樣，不替模型改寫結果。

使用者隨後詢問是否直接建立測試資料夾／專案即可。建議下一輪改為一般功能 smoke test：獨立測試資料夾、固定 fixture、明確 ownership、原始結果及版本證據即可作為工作界線；共享宿主的存取限制必須如實揭露，不宣稱是盲測、因果比較或強隔離驗證。這是用途與保證範圍的調整，不把舊的隔離失敗改判 pass，也不減弱真正的功能、安全與 evidence correctness gates。

本次到此收尾，不再擴大 sandbox 工程。正式三檔、spec、hooks、既有 README 內容與候選 hash 都維持基準；沒有安裝、commit/push 或全域設定變更。
