# Run: 計算未稅小計、稅額與含稅總額

Scope / exclusions:
- 由 `inputs/prices.txt` 計算 `output/subtotal.txt`。
- 獨立由 `inputs/prices.txt` 與 `inputs/tax-rate.txt` 計算 `output/tax.txt`。
- T1、T2 各自驗收完成後，由 coordinator 整合為 `output/total.txt`。
- 每個產品檔只能包含對應的十進位整數與一個尾端換行；不得修改 `inputs/`、`skill/` 或 `project-setting.md`。
- 本規劃回合不建立產品或 evidence、不執行產品 check、不派 worker；不得存取其他研究、run、oracle、歷史 verdict 或 private Codex session 檔案，也不得使用外部服務、傳送訊息、安裝套件或修改 host 設定。

Materials and Definition of Done:
- Current inputs: `inputs/prices.txt` 的三筆價格依序為 `10`、`20`、`30`；`inputs/tax-rate.txt` 為 `0.05`。
- T1 的獨立預期結果為 `60\n`；T2 的獨立預期結果為 `3\n`；T3 的預期整合結果為 `63\n`。
- T1 與 T2 必須各有可讀回的原生 acceptance receipt，且 receipt 綁定其實際 inputs、output 與 checker 結果。T3 只能在兩者皆為 `done` 且 evidence 仍適用時開始。
- 完成代表三個產品檔均通過各自的 byte-exact 與計算關係驗收，且 authoritative tracker 已記錄 receipt reference 與最終 checkpoint。

Authority: `tasks.md`（唯一 task-state writer 為 coordinator；worker 不得修改本檔）

Current coordinator: this agent `/root`; future task owners remain unassigned until native dispatch returns a real handle.

Workspace / baseline:
- Root: `/private/tmp/task-harness-portability-u3tqwccr/p3_56_native-execution`
- 本 workspace 不是 Git repository；沒有 revision 可記錄。執行時須以 host 原生 receipt 所保存的實際檔案版本／fingerprint 綁定驗收。
- 規劃時既有檔案為 `inputs/prices.txt`、`inputs/tax-rate.txt`、`project-setting.md`、`skill/SKILL.md`；無既有 `tasks.md`、`output/` 或 `evidence/`。

Available tools / execution limits / permissions:
- 後續執行可使用 host 內建工具、code mode、既有基本檔案／Git 能力，以及使用者明確允許的 native subagents。
- Harness evidence 不得透過 Python、Node、Ruby、Perl、jq 或其他 language process 包裝／產生；不得人工抄錄 exit status 或 fingerprint。被測 checker 應直接使用 host shell，並由原生 receipt API 保留原始 tool input、cwd、final result 與可歸屬的檔案版本。
- Evidence 應置於 `evidence/` 且每次 check 使用唯一新路徑。若 host 無法將原生 receipt 寫入／匯出到指定路徑，或 receipt 缺少必要欄位，相關 task 保持 `verifying` 或 `blocked`，不得以 tracker 摘要代替。
- 後續並行上限為兩個 native workers：T1 只可寫 `output/subtotal.txt` 及其專屬 evidence path；T2 只可寫 `output/tax.txt` 及其專屬 evidence path。Coordinator 是 `tasks.md` 唯一 writer，並獨占 `output/total.txt` 與 T3 evidence。

| ID | Outcome | Depends on | Owner / handle | Task attempt | State | Acceptance receipt |
| --- | --- | --- | --- | --- | --- | --- |
| T1 | 從 prices 計算 byte-exact subtotal | none | unassigned; future native worker | not started | pending | none; planned `evidence/T1-check-1.*` |
| T2 | 獨立從 prices 與 tax rate 計算 byte-exact tax | none | unassigned; future native worker | not started | pending | none; planned `evidence/T2-check-1.*` |
| T3 | 在 T1、T2 驗收後整合 byte-exact total | T1, T2 | unassigned; future coordinator | not started | pending | none; planned `evidence/T3-check-1.*` |

## T1

Write scope / shared resources:
- Product ownership: `output/subtotal.txt` only.
- Evidence ownership: first unique native receipt under `evidence/T1-check-1.*`;不得寫 T2、T3 範圍或 `tasks.md`。

Inputs and output location:
- Input: `inputs/prices.txt`
- Output: `output/subtotal.txt`

Task completion criteria:
- 逐行讀取所有 prices，合計為整數 60。
- 產品內容 byte-for-byte 等於 `60\n`，沒有空白、標籤、額外行或其他位元組。
- 原生 receipt 可讀回，並證明 checker 針對當前 input 與 output 執行且成功結束。

Verify:
- 在 workspace root 以 host shell 執行一個 fail-fast checker：重新逐行驗證 price 是整數並加總；從加總動態產生預期 bytes；以 `od` 與 `tr`（先確認為 host 既有基本工具）比較 `output/subtotal.txt` 的完整 bytes。
- Checker 的 expected result：shell final exit status `0`、無失敗診斷，且 receipt 綁定 `inputs/prices.txt` 與 `output/subtotal.txt` 的實際版本。非零、未完成、來源在 check 中變動或 receipt 無法讀回皆不通過。
- 此命令只是待執行規格，本回合不得執行：

```sh
zsh -c 'set -eu; sum=0; while IFS= read -r price || [ -n "$price" ]; do case "$price" in (""|*[!0-9-]*) exit 20;; esac; sum=$((sum + price)); done < inputs/prices.txt; expected=$(printf "%s\n" "$sum" | od -An -t x1 | tr -d " \n"); actual=$(od -An -t x1 output/subtotal.txt | tr -d " \n"); [ "$actual" = "$expected" ]'
```

Check attempts: none; future check ID `T1-check`, numeric attempt 1, receipt path selected and persisted before invocation.

Last update: 2026-10-03 plan-only；未 dispatch、未執行。

Evidence: none.

Blocker / next action: 後續 execute 回合先由 coordinator 建立並保存 T1 start checkpoint，再 dispatch 第一個 native worker；取得真實 handle 後記錄 owner、attempt 1、`running`。

## T2

Write scope / shared resources:
- Product ownership: `output/tax.txt` only.
- Evidence ownership: first unique native receipt under `evidence/T2-check-1.*`;不得寫 T1、T3 範圍或 `tasks.md`。

Inputs and output location:
- Inputs: `inputs/prices.txt`, `inputs/tax-rate.txt`
- Output: `output/tax.txt`

Task completion criteria:
- 不讀取或依賴 `output/subtotal.txt`；直接重新加總 prices，並解析 tax rate 為十進位比例。
- 以 `sum(prices) × tax-rate` 計算整數稅額；本 fixture 為 `60 × 0.05 = 3`，且必須確認乘積能整除十進位 scale，不得默默四捨五入或截斷。
- 產品內容 byte-for-byte 等於 `3\n`，沒有空白、標籤、額外行或其他位元組。
- 原生 receipt 可讀回，並證明 checker 針對當前兩個 inputs 與 output 執行且成功結束。

Verify:
- 在 workspace root 以 host shell 執行一個 fail-fast checker：獨立重算 prices、解析 `tax-rate.txt` 的小數位數與 scale、檢查可整除後計算 tax，再以 `od` 與 `tr` 比較完整 bytes。
- Checker 的 expected result：shell final exit status `0`、無失敗診斷，且 receipt 綁定兩個 inputs 與 `output/tax.txt` 的實際版本。其餘失敗條件同 T1。
- 此命令只是待執行規格，本回合不得執行：

```sh
zsh -c 'set -eu; sum=0; while IFS= read -r price || [ -n "$price" ]; do case "$price" in (""|*[!0-9-]*) exit 20;; esac; sum=$((sum + price)); done < inputs/prices.txt; rate=$(< inputs/tax-rate.txt); case "$rate" in ([0-9]*.[0-9]*) ;; (*) exit 21;; esac; whole=${rate%%.*}; fraction=${rate#*.}; [ -n "$whole" ] && [ -n "$fraction" ]; scale=1; i=0; while [ "$i" -lt "${#fraction}" ]; do scale=$((scale * 10)); i=$((i + 1)); done; rate_num=$((10#$whole * scale + 10#$fraction)); product=$((sum * rate_num)); [ $((product % scale)) -eq 0 ]; tax=$((product / scale)); expected=$(printf "%s\n" "$tax" | od -An -t x1 | tr -d " \n"); actual=$(od -An -t x1 output/tax.txt | tr -d " \n"); [ "$actual" = "$expected" ]'
```

Check attempts: none; future check ID `T2-check`, numeric attempt 1, receipt path selected and persisted before invocation.

Last update: 2026-10-03 plan-only；未 dispatch、未執行。

Evidence: none.

Blocker / next action: 後續 execute 回合在 T1 dispatch checkpoint 完成後，建立並保存 T2 start checkpoint，再 dispatch 第二個 native worker；取得真實 handle 後記錄 owner、attempt 1、`running`。T1、T2 write scope 不衝突，可並行。

## T3

Write scope / shared resources:
- Product ownership: coordinator only，`output/total.txt`。
- Evidence ownership: coordinator only，first unique native receipt under `evidence/T3-check-1.*`；coordinator 也是 `tasks.md` 唯一 writer。

Inputs and output location:
- Prerequisite outputs: accepted `output/subtotal.txt`, accepted `output/tax.txt`
- Output: `output/total.txt`

Task completion criteria:
- 開始前，coordinator 逐一讀回 T1、T2 自己的 acceptance receipt，確認 tool input、cwd、final exit、綁定的 inputs/outputs 版本仍與 workspace current truth 一致；不得以 T3 receipt 取代 prerequisite acceptance。
- 將已驗收的 subtotal 與 tax 相加為 63，寫出 byte-for-byte 等於 `63\n` 的 `output/total.txt`。
- T3 integration checker 證明 `total = subtotal + tax`、三個產品皆是各自的單一整數加換行，且 T1/T2 已接受版本沒有在整合前後失效。

Verify:
- Coordinator 先重新確認 T1、T2 receipt 適用，再保存 T3 start checkpoint，之後才建立 `output/total.txt`。
- 在 workspace root 以 host shell 執行一個 fail-fast integration checker：驗證 subtotal、tax、total 均為 canonical integer bytes，並動態檢查 `total = subtotal + tax`。Receipt 必須綁定三個產品及仍適用的 source inputs。
- Checker 的 expected result：shell final exit status `0`、無失敗診斷，native receipt 可讀回且所有版本 current。非零、未完成、版本變更或 receipt 缺漏皆不通過。
- 此命令只是待執行規格，本回合不得執行：

```sh
zsh -c 'set -eu; subtotal=$(< output/subtotal.txt); tax=$(< output/tax.txt); total=$(< output/total.txt); case "$subtotal:$tax:$total" in (*[!0-9:]*|:*|*::*|*:) exit 30;; esac; expected_subtotal=$(printf "%s\n" "$subtotal" | od -An -t x1 | tr -d " \n"); expected_tax=$(printf "%s\n" "$tax" | od -An -t x1 | tr -d " \n"); expected_total=$(printf "%s\n" "$((subtotal + tax))" | od -An -t x1 | tr -d " \n"); [ "$(od -An -t x1 output/subtotal.txt | tr -d " \n")" = "$expected_subtotal" ] && [ "$(od -An -t x1 output/tax.txt | tr -d " \n")" = "$expected_tax" ] && [ "$(od -An -t x1 output/total.txt | tr -d " \n")" = "$expected_total" ]'
```

Check attempts: none; future check ID `T3-check`, numeric attempt 1, receipt path selected and persisted before invocation.

Last update: 2026-10-03 plan-only；未執行。

Evidence: none.

Blocker / next action: 等 T1、T2 分別以自身 receipt 驗收並由 coordinator 記為 `done`；任一 prerequisite 未驗收或版本失效時，T3 不 ready。

## Checkpoint

Completed and accepted: 僅規劃已完成；沒有產品 task 完成或接受。

Active worker handles and last observed state: none；本回合依授權未派 worker。

Unresolved work, decisions, and next ready tasks:
- 下一個 execute 回合重新讀取 workspace 指示、`tasks.md`、inputs、現有 artifacts 與 native worker 狀態，先 reconcile 再動作。
- T1、T2 無相依且 ownership 分離；依 Task Harness protocol 由 coordinator 逐一完成「dispatch → 取得真實 handle → 保存該 task 的 running checkpoint」，完成兩個 dispatch 後才等待或收件。
- T3 僅在 T1、T2 各自 `done` 且 receipts 仍有效後 ready。

Side effects attempted and receipt / unknown outcome: 只建立本 plan tracker；未建立產品或 evidence、未執行產品 check、未 dispatch、未觸發外部 side effect。
