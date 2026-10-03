# Task Harness：降低 runtime 依賴與 Hook 可行性計畫

後續狀態：使用者要求改以普通測試資料夾繼續後，已完成[固定候選功能驗收與正式採用](../research/task-harness-functional-20261003.research.md)。下文保留原強隔離研究輪次的 Inconclusive 與歷史 gates，不代表後續工作仍未執行。

日期：2026-10-03。狀態：**本輪執行結束，P4 = Inconclusive。P1 工具 PoC、P2 候選完成；P3 首個模型 preflight 未達隔離 gate，按固定條件停止。正式版未修改，候選未採用。**

## Objective

把 Core 的目標定為：**不因使用 Task Harness 而強制額外安裝 Python、Node、Bash、jq 或其他 executable runtime。** 先證明宿主原生工具能提供哪些驗收證據，再決定把現有 Python runner 改為選配；不先刪除 runner，也不把 Hook 預設成新必要依賴。

這是可攜性研究與遷移計畫，不是重新開啟上一輪交接 A/B 修正實驗。最終可以得到 Go、No-Go 或 Inconclusive；後兩者同樣能完成研究，但不能宣告可攜化或歷史錯誤已修復。

## Background：目前到底做到哪裡

| 項目 | 目前事實 | 本計畫處置 |
| --- | --- | --- |
| 正式 Skill | 三個 runtime 檔案；流程主要由 LLM 依 SKILL.md 操作原生工具 | 保留目前版本作基準 |
| Python 依賴 | 本地 acceptance/retry 必須經 run_check.py；缺 Python 時該驗證會 blocked | 確認可替代責任，不能只把一句「必須」改成「可選」 |
| 研究工具 | offline_poc.py、collect_matrix.py、receipt/trace inspectors 等屬研究驗收工具 | 留在開發端，不納入安裝與執行依賴 |
| 交接研究 | R1–R4 完成，結論 Inconclusive；B1 未採用，R5 未觸發 | 不補樣、不建立 B2；結果原樣保留 |
| 交接 finding | REVAL2-HANDOFF-ORDER-56 仍 open；歷史上 done/start 同一次 patch，不符兩次保存契約 | 本計畫不直接關閉，也不把它當作必須建 workflow engine 的證據 |
| 三項 low observations | coordinator handle、人工轉抄證據、worker-local check attempt | 維持 backlog；只處理本次 evidence 路徑直接涉及的部分 |
| 實驗污染 | hpoc_56_2 無範圍 list_agents 取得其他 actors／歷史 verdict | 新模型測試前須先驗證隔離，不能只換 prompt |
| 本專案 hooks | .codex/hooks.json 只有 SessionStart/SubagentStart 文件規範提醒 | 沒有 task-state enforcement；不在本輪修改 |

上一輪八筆功能及交接時序均通過，其中一筆比較受污染；基準 B0 本身也全數通過，因此不能歸因為候選改善。這是小樣本觀察，不能由此估計失敗率或稱問題「低頻」。詳見[研究決策](../research/task-harness-handoff-research-poc-20261003.research.md)。

## Materials 與查證邊界

- 使用者提供的[交接保存順序說明](chatgpt-conversation://6ac0ee12-28f4-83ee-856e-09ec367da7c7)：已讀取完整可用回覆，作為需求與提案，不當成宿主能力證明。
- [現行 SKILL.md](../../skills/task-harness/SKILL.md)、[run_check.py](../../skills/task-harness/scripts/run_check.py)、[openai.yaml](../../skills/task-harness/agents/openai.yaml)、[既有 spec](../specs/task-harness.spec.md)。
- [前輪計畫](task-harness-handoff-research-poc-20261003.plan.md)、[前輪研究](../research/task-harness-handoff-research-poc-20261003.research.md)、[原 findings](../research/task-harness-revalidation2-20261003-evidence/findings.json)。
- 本機 CLI 為 codex-cli 0.160.0，features 顯示 hooks stable/true。這不證明桌面宿主、每一個 collaboration tool 或目前 hook trust 狀態具備同等行為。
- 本次工具介面提供 command output、exit_code 或尚在執行的 session_id；未因此證明它自動提供完整 argv、分離 stdout/stderr、版本 fingerprint、跨 resume 可讀的 durable receipt。

查證日期為 2026-10-03。一手來源與可用結論：

| 來源 | 本計畫採用的結論 |
| --- | --- |
| [Agent Skills specification](https://agentskills.io/specification) | SKILL.md 為必要入口；scripts 為選配；可執行語言支援取決於實作。規格本身不承諾 task-state enforcement。 |
| [OpenAI Build skills](https://learn.chatgpt.com/docs/build-skills) | instruction-only 是建立 Skill 的預設方向；確有 deterministic 行為或外部工具需求才加入 scripts。這不代表每個 workflow 都可等價去除 executable logic。 |
| [OpenAI Hooks](https://learn.chatgpt.com/docs/hooks) | 支援 PreToolUse 的特定拒絕格式，但部分路徑例外、回呼錯誤／逾時或不支援的回覆可能放行；非 managed hooks 需信任目前定義。PostToolUse 無法撤銷已發生副作用。官方亦不把 tool hooks 視為完整 enforcement boundary。 |

以上是規格與官方契約查證，**不是在此桌面環境完成的 hook PoC**。`before_state_commit`、`before_task_start`、`transition_task()` 是對話中的架構提案，不是已確認可呼叫的原生 API。

## Boundaries

規劃階段只新增這份計畫。後續「執行任務」已授權按下列 gates 執行：先做 P1，通過才進候選與驗收。正式檔案、hooks、host 設定、歷史 evidence、README 及無關工作在研究期間保持不變；不安裝依賴、不 commit/push。執行目標由目前 thread goal 管理，不另建 goal。

後續執行亦採最小範圍：先驗證 native evidence 替代性；需要時只做一個隔離候選。預設不新增 event store、event-per-file protocol、資料庫、MCP server、binary/WASM、workflow engine 或另一套 validator。研究用 script 可留在開發端，但不可由正式 Skill 的執行路徑隱性呼叫。

不承諾所有宿主相容、完全零依賴、crash durability、exactly-once、抗竄改證明，或靠 Markdown 就能強制阻止違規工具操作。這些都需要額外機制及相應驗證。

## Assumptions：把依賴分成三種

| 類型 | 例子 | 是否違反 Core 目標 |
| --- | --- | --- |
| 宿主既有能力 | LLM、讀寫檔案、原生命令工具、可用時的 native agents | 否，但須揭露最低能力；缺 delegation 時可序列執行 |
| 被執行專案的需求 | 專案本來要使用 Java、npm、cargo 或 Python tests | 否；不得把專案依賴包裝成 Harness 安裝前提 |
| Harness 自己新增的需求 | 為記錄 check 而必須安裝 Python；必須啟用 command hook 或另架 MCP | 是；Core 不應強制需要，增強功能可明確選配 |

inline Python/JavaScript、shell one-liner 或改用 jq 並未消除 runtime 依賴。宿主內建的執行能力不等於使用者需另裝語言，但其宿主綁定仍須明列。遠端 MCP 可以免本機 Python，代價則是服務、網路、授權及維運需求。

## 建議設計與取捨

| 方案 | 優點 | 代價／缺口 | 建議 |
| --- | --- | --- | --- |
| A. 原樣保留 mandatory Python | receipt 行為已存在，變更最少 | 無 Python 的環境不能完成本地命令驗收 | 遷移前的安全基準 |
| B. native-first Core，Python evidence helper 選配 | 有機會免額外安裝；沿用宿主工具；保留需要時的嚴格證據路徑 | 不同宿主證據能力不同；缺必要能力仍須明確限制驗收 | **優先研究與驗證** |
| C. Hooks／MCP／專用 runtime 強制所有狀態操作 | 在完整控制工具與權限時可增加 deterministic 約束 | 新安裝與維運依賴；覆蓋與繞過問題；架構擴張 | 延後，不能作為 B 的預設前提 |

B 的 native 路徑只能在證據足夠時接受結果；不是拿自然語言摘要替代缺失證據。沒有必要證據時，仍可規劃及進行其他安全工作，但相關 task 保持 verifying/blocked。若只能做到規劃，不能宣稱該宿主已支援完整 scriptless execution。

### run_check.py 的責任逐項去向

| 現有責任 | native-first 候選方式 | 必須證明／不可省略 |
| --- | --- | --- |
| 保存實際 argv、cwd | 引用原生 tool call 與結果 | shell command 字串不是 argv list；保留實際表示方式，不自行拆字串冒稱 process argv |
| 真實 process returncode | 讀取個別 command 的最終結果 | 不拿 PASS 文字、外層 batch 成功或 running session 當 child 成功 |
| stdout/stderr | 使用原生輸出 | 合併輸出需標示 merged；若驗收需要區分而宿主不提供，該 criterion 未驗證 |
| before/after fingerprints | 宿主版本／快照能力，或能力允許時使用選配 helper | 綁定受測 artifact；dirty tree 不能只引用 HEAD；無 hash 工具不可編造 digest |
| source stability | 比較與該次執行關聯的前後版本 | 端點相同不證明過程絕無修改；不得擴張為抗競態或抗竄改保證 |
| receipt 保存與恢復 | 可重新取得的 native result reference，必要時原生檔案工具保存索引 | 真正跨 resume 可解析；人工摘要不是原始 evidence；不得依賴作者的私人 session export |
| 先 exclusive-create，既有 receipt 不覆寫且不重跑 | 保留 helper；或宿主提供等價原語時才替代 | 單一 coordinator＋唯一 ID 只是協定，沒有 exclusive-create 不能宣稱等價原子保留 |
| not_started／started／unknown | 依原生 launch/終止狀態記錄 | 缺結果不可當失敗後直接重播；先 reconcile，尤其有副作用時 |
| retries 與 acceptance reference | 既有 task/check attempt 與 receipt 索引 | 分開 task attempt/check attempt；不得覆寫舊證據或人工重抄成另一個 truth source |

現行 runner 也不負責強制交接、阻止外部檔案修改或保證 crash transaction；將其保留並不自動解決這些問題。

### Hook 放在哪裡，才能有用

先把能力標成「提醒」「可觀察」「已驗證可阻止某工具」「完整強制邊界」四種；前三者不能直接宣稱第四種。

| 目的 | 可研究的掛點 | 採用條件與限制 |
| --- | --- | --- |
| 提醒先讀規範／保存交接 | SessionStart 等生命週期 context | 本專案已是這一類；提示可能改善遵循，但不等於攔截 |
| actor identity | 原生 agent handle／生命週期 metadata | 使用實際可取得的 ID；parent session ID 不可冒充 child handle；取不到則明記 unknown |
| 拒絕同次 done/start mutation | 若宿主能攔截且理解所有 tracker 寫入 | 先驗證 apply_patch、shell、MCP、child agent 等路徑與 failure behavior；只攔一個 wrapper 仍可繞過 |
| 自動收集 command 結果 | 原生 tool result 或 PostToolUse | 結果欄位、版本綁定、保存位置均需核對；不能把事後 hook 當事前阻擋 |
| 防止測試讀取其他 run | 獨立 agent registry／工具能力限制／檔案存取隔離 | path_prefix 是查詢參數，不是 ACL；「請不要讀」不是隔離證據 |

**可攜 Core 不依賴上述 hooks。** 如日後要求 hard enforcement，必須先設計受控狀態寫入權限，確認其他可用工具不能直接修改它；否則只能稱 guardrail。不能以 regex 對任意 shell 命令的比對宣稱完整 mediation。

## 執行順序與任務清單

P0 為規劃成果；P1 工具級結果見[研究紀錄](../research/task-harness-portability-hooks-20261003.research.md)。單一 coordinator 為本 thread 的 /root，thread ID 為 01a0fb69-8abc-7660-9bdc-e9e39fbde9b5。由本 coordinator 維護此表；研究、候選、驗收角色可依序完成，不預設增加 reviewer 階層或平行 agents。

| ID | 交付結果／驗證方式 | 依賴 | 責任範圍 | 狀態 |
| --- | --- | --- | --- | --- |
| P0 | 現況、責任拆解、來源、固定驗收與停止條件形成此計畫；讀回並核對保留檔案 | 無 | 本次 coordinator；只寫本計畫 | 完成 |
| P1 | 在一個指定宿主確認 native evidence 能力；逐項填 pass/fail/unverified，先回答能否免 helper 完成一個命令驗收及恢復 | P0、執行授權已取得 | /root；隔離 fixture／研究 evidence；attempt 1 | 工具級完成；原始結果與限制見研究紀錄，模型行為不計為通過 |
| P2 | P1 可行才製作一個隔離候選：native-first、helper 選配、能力不足時的行為；列出相對正式版 diff | P1 通過必要工具能力 | /root；候選副本，不改正式 Skill；attempt 1 | 完成；candidate-freeze.json 固定版本，官方 validator 通過 |
| P3 | 固定案例驗收；判定 portability 與舊安全契約，分開報告 | P2、測試隔離成立 | /root；只讀候選，寫當輪 evidence；attempt 1 | 停止：首個模型 preflight 可讀 scope 外 canary；Skill 行為測試未開始，其他三筆未啟動 |
| P4 | 一次 Go／No-Go／Inconclusive 決策；Go 才提出最小正式套用範圍 | P3 或任一 gate 不成立 | /root；[研究決策](../research/task-harness-portability-hooks-20261003.research.md) | 完成：Inconclusive，不採用候選、不補樣 |

P1 不需要先跑八筆模型 A/B。先做工具級能力查證與小型 PoC，保留實際 call/result；模擬回傳只能校準 oracle，不能證明 live host 支援。先選當前 Codex 宿主作 feasibility，不把它外推為 Windows、Web 或所有 Skills 宿主通用。

Hook 子題在 P1 只作能力與缺口記錄；若不能在隔離設定中安全驗證，就標 unverified，延後，**不為 Hook 未完成阻塞 portable Core**。不得自行繞過 trust review、改全域設定或啟用有外部影響的 hook。

### P1／P3 固定驗收案例

| 案例 | 要回答的問題與通過條件 |
| --- | --- |
| C1：無 helper 的正常驗收 | 在不允許 Harness 執行額外語言 runtime 的配置下，以原生工具完成小型 task/check，結果和版本可追溯；不能只做到 plan-only |
| C2：誤導成功訊息 | 已知 fixture 輸出 PASS 但程序非零；仍判 check failure，原始結果保留 |
| C3：來源改變 | check 後受測內容改變，舊 receipt 不得接受新內容；缺版本證據亦不得 pass |
| C4：缺必要能力 | 無 Python、無合格原生證據時，能交付規劃／續做獨立安全工作；受影響驗收明確 blocked/unverified，不自動安裝、不捏造 hash/exit |
| C5：resume 與 unknown | 新 resume context 可取得原先 result；若不可取得，保持未驗證。有副作用的結果 unknown 不得重送；僅使用無外部影響 fixture |
| C6：attempt／既有 evidence | 安全的新 check 使用新 check attempt/reference；舊 receipt 不被覆寫；是否具原子 reservation 另列能力，不冒稱等價 |
| C7：既有工作流 | plan-only 不實作；交接仍是已接受 done 保存成功後才存 successor start、再做產品動作；並行先完成 eligible group dispatch/checkpoint 才主動 collect |
| C8：選配相容性 | 啟用 Python helper 的既有路徑仍可用；Core 不必安裝或執行它。未提供 helper 的 Core 安裝不讀不存在的必要檔案 |

測試依賴與產品依賴分開登錄：研究端可用 Python 產生 oracle 或檢查輸出；受測 agent 的 Harness 路徑不可藉 inline code、絕對路徑 interpreter、研究目錄或 helper 偷用被排除的 runtime。只把 Python 從 PATH 移走不足以證明 C1。原生 code mode 是否屬宿主最低能力也要明列，不能宣稱在沒有該能力的宿主同樣通過。

P1 先確認 C1–C6 所需 primitive。P2 只能在必要證據有實際可用路徑後開始；其餘案例在 P3 檢查候選行為。工具 PoC 的通過不等於模型遵循通過。

### 模型測試的上限與隔離前提

如 P1/P2 通過並進入 P3，固定 **2 個模型 × 2 個 profile＝最多 4 個 coordinator runs**：沿用 gpt-6.1-sol、gpt-5.6-sol，每模型各一次 native-execution profile、一次 resume/negative profile。同一候選、相同 fixture 與固定 oracle；這是相容性 smoke test，不作成功率或改善因果推論。

- native-execution：驗證 C1、C6–C8，含兩個獨立 worker 再交接到 coordinator integration；每 run 最多兩 workers，共最多四 workers。plan-only 子案例先獨立回合驗證，後續才給 execute 授權。
- resume/negative：以預置且可追溯的歷史 fixture 驗證 C2–C6；不另派 workers。歷史資料是 fixture，不偽稱本次 agent 已執行它。
- 不要求 worker 實際時間 overlap，也不要求 dispatch 早於自動 completion；仍以現行 Skill 的「群組 dispatch 完成前不主動 collect」判定。
- 開跑前確認無法經 agent listing、messaging、共享檔案或歷史 trace 取得其他 run／oracle verdict。fresh prompt 或 voluntarily scoped listing 不足以證明隔離。
- 若現有宿主無法提供上述隔離，停止 live model 比較並列 Inconclusive；不得為完成矩陣自行建立使用者 chats 或未授權新環境。

## 固定結束條件

本次**規劃 DoD**：已盤點 current runtime／研究依賴，辨識對話中尚未證明的保證，列出必要能力、單一推薦方案、PoC／任務／驗收／停止條件，文件讀回且正式檔案未變。這不代表 P1–P4 完成。

後續研究按下列規則結束：

1. **Go**：C1–C8 的適用條件均有直接證據；指定宿主的核心流程不需要額外語言 runtime；缺能力的分支不假成功；版本／退出碼／來源及 resume 可追溯；既有交接、授權與 no-blind-replay 契約未削弱。宣稱只涵蓋實測宿主與案例。
2. **No-Go**：必要 evidence 或正確接受條件確實無法成立；保留 mandatory-helper 基準，列最小缺口，不改驗收標準取得綠燈。
3. **Inconclusive**：缺能力證據、模型不可用、結果受污染或隔離不可證明；交付限制與結果，停止本輪，不補樣。
4. 候選最多一個。已知 oracle/fixture 操作錯誤最多修一次，只重跑受影響的工具案例並保留前後證據；不偷偷修改 Skill 候選，也不為全綠重跑固定模型樣本。若候選實際失敗，記錄並結束本輪。
5. 新 observability、措辭、平台、crash/cancellation 等一般 finding 記 follow-up，不自動增加本輪 blocker。只有直接違反既定 gate、data loss、incorrect acceptance、未授權副作用、unbounded retry／deadlock 或 evidence 歸屬失真才阻止 Go。
6. 歷史 handoff finding 不因 portability smoke pass 自動關閉。Hook 未成為 hard enforcement 不妨礙 B 的有限能力契約，但禁止宣稱已消除 LLM 不遵循協定的可能性。

Go 後若已獲正式實作授權，最小變更應限於 SKILL.md 的 evidence 路由、spec 的能力／限制及確有需要的 openai.yaml metadata；先保留 runner 內容，改成選配。研究／測試 scripts 不打包。所有執行期連結須在乾淨安裝位置可解析。回退為目前三檔基準與現行 spec；不改歷史 evidence。

成果已保存於 `docs/research/task-harness-portability-hooks-20261003.research.md`，原始證據放同名 `-evidence/` 目錄。研究報告包含能力矩陣、案例結果、候選 diff／版本、限制及唯一決策，不再產生重複 tracker。

## 正式基準 fingerprints

| 檔案 | SHA-256 |
| --- | --- |
| skills/task-harness/SKILL.md | 99114ea67a51c28339a595ed846b3942a5b7d3125327592e7d4f4f57fdbdaf0d |
| skills/task-harness/agents/openai.yaml | 76b6ed3aab887a5dcc9870d04d5596d176cd512c7c6bc432511a29fc24271310 |
| skills/task-harness/scripts/run_check.py | f25835aac47953927da5e13c711eebad3ffaca8426a2cc548b57dbacb4d7b988 |
| docs/specs/task-harness.spec.md | 92e532f0a955eccffe75fad55a9a5fa577035546b5403554736fe2924870dcac |

**後續獨立建議：先查明 codex sandbox 與 codex exec 在相同 read-deny 意圖下的有效權限差異；在模型實際使用的工具路徑證明隔離後，才另立下一輪驗收。本輪不修改 Skill 候選或重跑矩陣。**
