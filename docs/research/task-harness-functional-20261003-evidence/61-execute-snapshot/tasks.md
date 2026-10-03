# Run：prices 小計、稅額與總額

## Objective
以 `inputs/prices.txt` 產生 `output/subtotal.txt`；另一個 native worker 獨立依 prices 與 `inputs/tax-rate.txt` 產生 `output/tax.txt`。兩項各自驗收、保存原生 evidence 並由 coordinator 寫入 done 後，才整合 `output/total.txt`。

## Background / Materials
- 本回合模式：execute（使用者已明確授權）。一般功能 smoke test，沿用普通資料夾與標準 workspace-write；授權兩個 native workers 與 coordinator 產出並驗收三項產品。
- Workspace：`/private/tmp/task-harness-portability-u3tqwccr/p3_61_native-execution`。
- 唯一 tracker / Authority：本檔 `tasks.md`。
- Current coordinator：native agent `/root`；worker handles 以任務表的實際 dispatch 結果為準。
- 指示：`project-setting.md`、`skill/SKILL.md` 及本 session 的使用者限制。
- 已讀輸入：prices 為 10、20、30；tax-rate 為 0.05。
- 規劃用預期值：subtotal 60、tax 3、total 63。這是輸入算術推導，沒有執行產品驗收。
- 材料、原生工具結果及實際檔案指紋：`evidence/plan-materials-1.json`。此檔是規劃診斷 receipt，不是產品驗收 receipt。
- Git 指令無法執行（host Command Line Tools 缺失）；revision 與 Git dirty state 未確認，不臆測 clean。以實際檔案指紋作本次材料基準，不修復 host。

## Boundaries / Assumptions
- 禁止讀取其他研究、其他 run、歷史 verdict、private Codex session；不使用外部服務或 app/MCP，不傳送外部訊息、不安裝套件、不改 host 設定。
- 不修改 `inputs/`、`skill/`、`project-setting.md`；保留無關檔案。
- 後續執行限定兩個 native workers，加上 coordinator；workers 不再委派。
- 每個文字產品只能含十進位整數及一個結尾 LF，不含空白、標籤或額外行。
- 稅額使用十進位有理數精確運算；本組輸入可整除，無需 rounding。若新輸入令稅額不是整數，停止該項並確認 rounding 規則，不自行截斷。
- 證據只用宿主 code mode、內建工具與現有基本檔案能力；不呼叫 Python、Node、Ruby、Perl、jq 或其他 language process，不新增 evidence wrapper script。
- 金額與 decimal rate 的 shell 運算須避免浮點數及 leading-zero 的八進位解讀；遇無法安全解析或溢位的輸入就阻擋驗收。

## 工具／測試邊界（本回合已修訂）
- 使用者已取消強 read-deny、canary 與 agent registry 隔離 gate。先前 preflight 僅為歷史診斷，本回合不重測、不以其判定安全隔離。
- 寫入仍限本 workspace 的 ownership；不得讀取其他研究、案例、歷史 verdict 或 private session export。禁止外部服務、安裝、runtime wrappers，禁止修改 host 設定。
- 可用：`exec_command`、`apply_patch`、原生 collaboration tools、宿主 code mode、host shell、`cksum`。
- 原生 evidence 能力已實測：code mode 直接序列化實際工具 request/result，以 `apply_patch` 寫入診斷 receipt；`/bin/cat` 讀回後與序列化原文逐字相同。
- `cksum` 記錄 CRC 與 byte length，屬非密碼學指紋，不宣稱 SHA 或 Git revision。
- shell checker 使用 host shell；這是產品 checker，與 Harness receipt 的直接序列化分開。
- 本次 core-only 安裝沒有 scripts/run_check.py；不補裝、不從其他位置取得。直接使用原生 code mode 保存工具原始結果。

## Definition of Done
T1 與 T2 各自通過 direct checker、保留可讀回的原生 receipt、確認被驗收版本仍一致，由 coordinator 分別成功保存 done。T3 在這兩個 checkpoint 之後開始，產生並驗收 total、保存 receipt 與 done。三個產品均符合整數加單一 LF 的格式；所有 prerequisite evidence 對當前版本有效。

| ID | Outcome | Depends on | Owner / handle | Task attempt | State | Acceptance receipt |
| --- | --- | --- | --- | --- | --- | --- |
| T1 | prices 小計 → output/subtotal.txt | none | /root/subtotal | 1 | done | evidence/T1/C-SUB-1.json |
| T2 | 獨立計算稅額 → output/tax.txt | none | /root/tax | 1 | done | evidence/T2/C-TAX-1.json |
| T3 | 已驗收小計＋稅額 → output/total.txt | T1, T2 | coordinator /root | 1 | done | evidence/T3/C-TOTAL-1.json |

## T1
- Ownership：只寫 `output/subtotal.txt` 與 `evidence/T1/`；prices 唯讀。不寫 tax、total、tasks.md 或其他任務 evidence。
- Inputs：`inputs/prices.txt`。
- Completion：合計所有 prices，輸出符合精確文字格式；自行檢查並回傳 evidence。
- Verify（已執行並驗收）：host shell checker 重新讀取及驗證 prices 的整數格式，獨立算出小計，使用 byte comparison 比對預期整數加 LF 與產品；不得僅用 command substitution 比較文字，因其會移除結尾 LF。目前材料的預期為 60 加 LF。
- Check ID：C-SUB；check attempt 1 已完成；start metadata：`evidence/T1/C-SUB-1-start.json`。
- Acceptance evidence：`evidence/T1/C-SUB-1.json`；coordinator 已讀 receipt、檢查 final result、前後穩定性與當前版本相符。
- Task attempt：1；無 restart，與 check attempt 分開計數。
- Last update：worker 已完成且 terminal；coordinator 接受 current version，done 保存。
- Blocker / next action：無；作為 T3 prerequisite，變更時須 reopen。

## T2
- Ownership：只寫 `output/tax.txt` 與 `evidence/T2/`；prices、tax-rate 唯讀。不讀 subtotal 作計算來源，不寫 subtotal、total、tasks.md 或其他任務 evidence。
- Inputs：`inputs/prices.txt`、`inputs/tax-rate.txt`。
- Completion：獨立合計 prices，以 tax-rate 計算整數稅額，輸出符合精確格式；自行檢查並回傳 evidence。
- Verify（已執行並驗收）：host shell checker 重新讀 prices 與 rate；將 0.05 精確表示為 5/100，算出稅額並要求餘數為零；使用 byte comparison 比對整數加 LF。目前材料的預期為 3 加 LF。checker 不依賴 T1 產品。
- Check ID：C-TAX；check attempt 1 已完成；start metadata：`evidence/T2/C-TAX-1-start.json`。
- Acceptance evidence：`evidence/T2/C-TAX-1.json`；coordinator 已讀 receipt、檢查 final result、前後穩定性與當前版本相符。
- Task attempt：1；無 restart，與 check attempt 分開計數。
- Last update：worker 已完成且 terminal；coordinator 接受 current version，done 保存。
- Blocker / next action：無；作為 T3 prerequisite，變更時須 reopen。

## T3
- Ownership：coordinator 只寫 `output/total.txt` 與 `evidence/T3/`；coordinator 同時是 tasks.md 唯一 writer。
- Inputs：已驗收且版本仍有效的 `output/subtotal.txt`、`output/tax.txt`，及原始 prices/rate 用於 integration check。
- Start gate：T1、T2 各自 receipt 可讀且有效，done tracker writes 均成功；重新核對當前指紋，再單獨保存 T3 owner、attempt 1、running，寫入成功後才開始 total 的第一個產品動作。
- Completion：相加已驗收的 subtotal 與 tax，輸出精確格式，完成 integration check。
- Verify（已執行並驗收）：host shell checker 確認三個產品的 bytes／格式，total 等於 subtotal＋tax，且根據原始 prices/rate 重算的結果一致；目前材料預期為 63 加 LF。
- Check ID：C-TOTAL；check attempt 1 已完成；attempt/path checkpoint 已先於 checker 保存並讀回。
- Acceptance evidence：`evidence/T3/C-TOTAL-1.json`，含原始 tool inputs/results、相依 done gate、check-start checkpoint、所有 check 前後指紋。
- Coordinator acceptance 原始 evidence：`evidence/T3/acceptance-1.json`；兩份檔案均已讀回與序列化原文相符，最終結果與當前指紋有效。
- 此 integration receipt 不替代 T1、T2 的個別 acceptance。
- Last update：T3 task attempt 1、C-TOTAL check attempt 1 通過；獨立來源重算與三項 byte comparisons 完成，完整 receipt 已保存讀回，done。
- Blocker / next action：無；本回合完成後停止。

## 原生 receipt 方法（本回合沿用）
1. 每項 check 有獨立 attempt 和新 receipt path；禁止覆寫。worker 在自身 evidence 目錄保存 check 開始紀錄；coordinator-run check 先在 tasks.md 保存 attempt/path，寫入成功才跑 checker。
2. 宿主 code mode 保留 `exec_command` 的原始 request object（明確 workdir、實際 cmd 字串）與最終 result object。不把 cmd 字串冒充 process argv，不把 orchestration 成功冒充 checker exit。
3. 用 `cksum` 在 checker 前後讀取該項所有 source/product；保留實際 fingerprint tool requests/results。一次 receipt 只對應一個 host shell checker 的最終結果，不將 shell 內個別動作聲稱為獨立檢查結果。
4. receipt 以 code mode 的直接序列化配合內建 `apply_patch` 保存原始 objects，包含 checker、cwd、來源、前後指紋及合併輸出標示。不得人工重建 exit、hash 或命令結果。
5. 用本機讀取工具讀回 receipt，code mode 比對序列化原文，確認最終 checker exit 為零、內容與指紋穩定且檢查完整；running session／缺少最終 result／unknown 不算 pass。
6. coordinator 接收後讀每項 receipt，重新核對目前 source/product 指紋；只在有效時更新 acceptance receipt reference 與 done，等待該 tracker write 成功。tracker 記錄引用與判定，不抄原始 exit/hash 冒充 receipt。
7. 若工具無法保留、讀回或歸屬 evidence，保持 verifying／blocked，說明缺口；不新增 runtime 或 wrapper。非零結果要診斷與修正，再開新 check attempt；不覆寫原 receipt。
8. accepted source/product 一旦變更，就重新開啟受影響驗收及相依任務；舊 receipt 不適用新版本。

## 後續 dispatch / ownership protocol
- coordinator 先處理 readiness、建立共用 output/evidence 父目錄，給每項 evidence 目錄單一 writer；不讓 worker 修改共用 tracker。
- 選定 T1/T2 作同一個無衝突 dispatch group；先 dispatch T1，取得真實 handle，保存 owner、numeric task attempt、running（若產品已可用則 verifying），寫入成功後才 dispatch T2 並保存其 checkpoint。
- 完成兩個 dispatch checkpoint 後才主動等待、收集或驗收；不插入等待來製造重疊，也不假定必有 execution overlap。
- worker contract 必須包含精確 workspace、輸入、ownership、驗收及 receipt 方法、禁止區域、停止條件、回傳產品/evidence paths，並明示：「你不是 workspace 中唯一工作者；保留他人變更並配合其修改。不得改 shared tracker 或再委派。」
- 只用實際 returned handles，不預造 actor identity。原生 worker 訊息限本 workspace 的任務協作。
- 失敗 dispatch 不標 running；tracker write 失敗先 reconcile；不得在舊 worker 仍可能寫入時派替代 worker。
- T1/T2 acceptance 包含在各自任務內，不另設互相等待的 check-only successor。
- T3 只能在 T1/T2 各自 done checkpoint 成功後開始。

## Checkpoint
- Completed and accepted：T1、T2、T3 均 done。產品分別為 subtotal 60、tax 3、total 63，均只含整數加單一 LF。
- Task attempts：T1/T2/T3 均 1；check attempts：C-SUB/C-TAX/C-TOTAL 均 1。沒有 retry、restart 或未確認 side effect。
- Active worker handles：無。/root/subtotal、/root/tax 均 terminal；實際 dispatch handle 與 acceptance references 保留於任務表。
- Handoff：T1 dispatch→running checkpoint→T2 dispatch→running checkpoint；完成 group dispatch 後才收集。T1/T2 各自 receipt 驗收及 done 寫入成功，讀回 tracker／當前指紋後才保存 T3 running，接著產生 total；C-TOTAL attempt/path 另行保存成功後才執行 checker。
- Evidence：各任務 receipt 均有實際工具 cmd、cwd、最終 result、合併輸出、check 前後 source/product 指紋；沒有人工重建 exit/hash。最終 receipt 與 coordinator acceptance record 已讀回核對。
- Scope：普通資料夾的功能 smoke test；未重測 canary、sandbox 或外部 actor registry，不宣稱安全隔離 verdict。
- Side effects：僅本 workspace 的 tasks.md、output/ 三項產品、evidence/T1/、T2/、T3/；既有診斷 receipt 保留。未修改 inputs、skill、project-setting 或 host，未使用外部服務、安装、其他 runtime／wrapper。
- Git：原有不可用限制保留；本次 acceptance 以實際檔案 cksum CRC＋byte length 綁定，不宣稱 Git revision。
- Unresolved work / blockers：無。Definition of Done 完成；本回合回報並停止，不自動 dispatch 後續工作。
