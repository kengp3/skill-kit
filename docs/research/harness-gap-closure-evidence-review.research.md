# Harness 補驗衍生證據輸出審查

日期：2026-10-26（Asia/Taipei）。範圍：本地 G01／G04 的五份 `session-contexts.json`、兩個維護者 driver 與既有證據讀回；沒有新模型 trial、remote 發布、全域設定或 demo 變更。

## 問題與證據

原 export 直接保存完整 `session_meta`／`turn_context`，因此五份衍生 JSON 含非必要 `creator_account_id`／`creator_user_id`。帳號識別 metadata 不是 bearer token；不能由這個發現推論憑證外洩。原生 RPC 未因本修正改寫。

在 `f15338e...c774d30` 的 291 份新增／修改 regular 檔案上，比對當下本機 auth 中四個符合 token／api_key／account_id 路徑、長度至少 20 的字串。[真 red](harness-gap-closure-evidence-review-evidence/audit-red.json) 只有這五份 JSON 命中 `tokens.account_id`，其他 token 未命中。輸出只保存欄位路徑、相對檔名及來源 SHA，不保存識別值或 token。這是 current auth 值的有限比對，不證明不存在所有歷史／未知敏感值。auth 是可能合法更新的日常狀態；精確 as-of 與 hash 均在 audit，沒有修改它。

## 最小修正

兩個 driver 使用相同欄位白名單，保留 envelope type／timestamp、session／turn 身分、cwd、runtime roots、來源、版本、model／effort 與 parent／child 關係。巢狀 `source.subagent.thread_spawn` 也只保留關係欄位，不遞迴複製未知欄位。其他不必要的完整指示、安全設定及帳號 metadata 均不輸出。

新離線 `--export-contexts INPUT OUTPUT` 只從既有事件重衍生 JSON，與原生模型啟動分支分開；既有 trial 的採集路徑亦使用同一投影。五份檔案重衍生後保留事件數、順序及每個 retained value，沒有補造 observed 值。[衍生索引](harness-gap-closure-evidence-review-evidence/derivation-index.json) 記錄逐檔 before／after SHA、移除欄位名稱及五份原生 RPC 不變的 SHA。舊版本只存在本地歷史，未做 destructive history rewrite。

## 驗證

- 已核准 seam：產物輸出 → JSON 讀回。先保存既有欄位的 [field red](harness-gap-closure-evidence-review-evidence/field-audit-red.json)；合成輸入的 [export red](harness-gap-closure-evidence-review-evidence/export-check-red.log) 顯示舊 CLI 沒有可離線驗證的 export 入口，非模型失敗。
- [合成 export/readback self-check](harness-gap-closure-evidence-review-evidence/check-context-export.py) 對兩個 driver 以真 CLI 驗證 literal 期望：未知／帳號／token 欄位排除，nested source 的 parent／child 與 model／effort 保留，非 context 事件排除。[green](harness-gap-closure-evidence-review-evidence/export-check-green.log)。
- 相同唯讀 audit [green](harness-gap-closure-evidence-review-evidence/audit-green.json)：291 檔零 current-auth literal 命中，五份 derived metadata 零帳號／user_id／token／api_key 欄位。
- [G01 既有成果 checker](harness-gap-closure-evidence-review-evidence/g01-check-green.json) 通過精確成果 bytes、唯一 done 合約及 705 原檔保存；此 checker 只讀 demo，未重做副作用。[G04 既有 checker](harness-gap-closure-evidence-review-evidence/g04-check-green.json) 三分支均通過，包括原生 child ID／context 的核對。

未重跑 full suite、真模型、Desktop、其他案例或全域安裝；本輪修正只支持衍生輸出的資料最小化與既有證據仍可核對，不改變其他受阻驗收狀態。
