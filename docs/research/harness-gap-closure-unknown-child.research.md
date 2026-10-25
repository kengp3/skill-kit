# Harness 補驗 G05：持久 child、transport 與未知啟動

日期：2026-10-26（Asia/Taipei）。所有 `session-*.excerpt.jsonl` 均為透明節錄：只省完整 `session_meta` 行，其餘工具 call／result 與其他行保持 bytes；完整原件留在私有 state。原始／公開 hash、行號省略索引及工具行數對照見[normal index](harness-gap-closure-unknown-child-evidence/session-excerpts-index.json)及[network index](harness-gap-closure-unknown-child-evidence/provider-preconnect/session-excerpts-index.json)。

**同 server／新 client 與同 state／新 server 的原 child 歷史查回通過；新主責查回部分受阻，真正 spawn 回覆遺失與 provider sampling 故障仍未通過，V02 整體保持部分。** 依[補驗規格 S7](../specs/harness-validation-gap-closure.spec.md)、[G05 ticket](../plans/harness-gap-closure-05-unknown-child.plan.md)、[可行性研究 V02](unified-project-settings-gap-fixtures-feasibility.research.md)與[核准總計畫](../plans/harness-validation-gap-closure.plan.md)執行。本檔保存單次實驗；持續狀態仍由中央報告彙整。

## 已確認輸入及 public seam

- 候選為指定 0.3.0，manifest SHA-256 `7e37d77315faee550e3f2e1edc4b3a621da490f50ce4a8d937c78f9d71fbfd9e`；控制器在複製前逐檔對照 manifest。case 只複製 `define-task`、`project-setting`、`task-harness`、`ai-code-review`，略過 `scripts`／`__pycache__`。來源 manifest 見[原始指紋](harness-gap-closure-unknown-child-evidence/candidate-manifest.json)。沒有變更產品、候選、demo、全域設定或舊 driver。
- case 是 `/private/tmp/g05-3e62e27f-7caf-4067-9749-eafaf5e6a5f1/case`；同層 `state` 為 0700、auth 為 0600，認證不進本 evidence。已直接複製 demo 當前 `AGENTS.md`、`project-setting.md`；保留 demo 的 current-source truth／歷史 `.planning/` 不執行語意，沒有把產品 repo 設定當 demo 設定。來源及 case 檔案 hash 見[baseline](harness-gap-closure-unknown-child-evidence/baseline.json)。
- 自有 native binary 為 `/Users/kengp3/.local/share/nvm/v26.7.0/lib/node_modules/@openai/codex/node_modules/@openai/codex-darwin-arm64/vendor/aarch64-apple-darwin/bin/codex`，CLI 0.164.0；[version](harness-gap-closure-unknown-child-evidence/native-version.json)、[help](harness-gap-closure-unknown-child-evidence/native-help.json)保存原 stdout／stderr，包含既有 PATH alias 權限警告。
- 已核准 public seam 是真原生 App Server：`thread/start`／`turn/start`、`thread/read`、`thread/turns/list`、`thread/list`。只有原 child／turn 身分、真終態及字面成果能接受。`idle`、`notLoaded`、timeout、控制器 exit 0 均不足。新 client、同 state 新 server、全新主責 thread 分開。
- 只使用自有 `ws://127.0.0.1:61195` listener，未使用 shared daemon；[live 身分](harness-gap-closure-unknown-child-evidence/live.json)保存原 PID。依[官方 App Server 文件](https://learn.chatgpt.com/docs/app-server)，WebSocket 是 experimental／unsupported，不能外推 production 重連保證。stdio EOF 會結束其 server；本案不用 stdio 讀取 timeout 冒充斷線。
- 每次 thread 使用 `runtimeWorkspaceRoots=[case]`、workspace-write、on-request、auto_review。child 的「唯讀」指授權及實際工作只有讀檔與等待 gate；[官方 Subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents)說明其繼承 parent 權限，角色設定不會建立獨立 OS read-only sandbox。本案不聲稱該隔離。

## 資格探查及故障界線

| 分支 | Expected → observed → raw evidence → verdict |
| --- | --- |
| 同 server、新 client | 原 child persistent、原 turn `inProgress` 時 client1 實際斷開，client2 先查回原身分／原 active turn 才放 gate；同原 turn 後續 `completed`、精確字面成果、唯一 task child，**通過**。故障點尚未觀察到 child 的等待 shell，不能聲稱命中既有 shell 中斷。 |
| 同 state、新 server | 原 parent／child 均終態後才關自有 server1，server2／client3 查回同 child／原 completed turn／精確成果，**通過，限已終態歷史查回**；未驗證執行中 worker 跨 server 存活。 |
| 新主責 thread | 第一回合因 prompt 對 CLI 限制過廣，未讀本地合約，該結果保留。同 persisted thread 澄清後已成功讀規則／原合約／本地輸入與 gate、更新並讀回原約；原生清單仍只見目前 `/root`，原 child 前綴為空，模型正確保留原 child／turn／返回成果 unknown、T1 未核實、不重派。**本地合約恢復通過，跨 root 原生 child 查回受阻**；兩者分開。 |
| 真正主責 spawn 結果遺失 | 175 個本機 ClientRequest methods 與 relevant schema 已實際產生並檢視；沒有找到在真 spawn tool 結果交付主責前丟棄一次結果的介面。`thread/inject_items` 是向模型歷史附加原始項目，不能作該故障證據；沒有使用。**資格受阻**，不是測試通過或功能失敗。 |
| app-server → provider 網路故障 | 自有程序 egress deny 已能執行；真原生 turn 終態 failed，錯誤 `workspace routing discovery failed`。命中 OpenAI workspace routing／周邊服務預連線，未取得 provider sampling URL 的故障證據。**部分、目標分支仍未命中**，未修改全機網路／防火牆／代理。 |

本機 schema 由 `codex app-server generate-json-schema --experimental --out /private/tmp/g05-schema` 產生；[schema excerpts](harness-gap-closure-unknown-child-evidence/schema-excerpts.json)保存完整 method names、實際版本支援的 `sourceKinds`／`parentThreadId`／分頁、thread/turn/skills/config 請求型別。沒有改 Codex 本體、合成工具或操作全機網路。

最小解鎖條件：spawn 分支需宿主提供真 tool-result delivery fault boundary，另有不依賴該回覆的原 child 查詢；provider sampling 分支需能在原生 routing／startup 完成後精確控制自有 provider 連線，並保存真 sampling URL／錯誤。沒有以 client 通知遺失、合成工具、context injection 或新 prompt 替代。

## 同 server、新 client 與同 state、新 server

| 身分 | 原生值 |
| --- | --- |
| parent／原 turn | `01a173d5-39ad-7302-a738-6ad1ea098ec1`／`01a173d5-3a23-7b23-9099-bdeeee8cbb88` |
| task child handle／thread | `/root/g05_reader`／`01a173d6-2300-7ff1-8cce-47d315fb2933` |
| 原 child turn | `01a173d6-231a-7321-911f-83a6a9975cbd` |
| server1／server2 | PID 5495／11927；同 state、同自有 endpoint |
| 實際模型 | 宿主 child metadata／session context 為 `gpt-6.1-sol`、`low`；模型合約內未觀測到該值而填 null，未事後美化合約 |

Expected → observed → raw → verdict：

1. 原生主責讀四候選技能／規則後保存唯一合約並真 spawn 一個 `fork_turns=none` child；[原提示](harness-gap-closure-unknown-child-evidence/parent-prompt.json)、[派工後合約](harness-gap-closure-unknown-child-evidence/artifacts-before-new-owner/docs/plans/g05-3e62e27f-7caf-4067-9749-eafaf5e6a5f1.task-contract.md)及[主責工具行 excerpt](harness-gap-closure-unknown-child-evidence/session-01a173d5-39ad-7302-a738-6ad1ea098ec1.excerpt.jsonl)可核對真 `collaboration.spawn_agent` 僅一次，成功 handle 後繼續保存工作／恢復依據。
2. 16:12:56Z 前，[原 child read](harness-gap-closure-unknown-child-evidence/before-disconnect-child.json)為 `ephemeral=false`、parent ID 相符、status active；[原 turn](harness-gap-closure-unknown-child-evidence/before-disconnect-child-turns.json)為 `inProgress`。同一 terminal／literal-result assertion 此時[真 red](harness-gap-closure-unknown-child-evidence/active-child-red-check.json)：`inProgress` 不等於 `completed`。gate 尚未放行，但等待 shell 還沒開始；這是 active child 的 client 斷線，並非已開始 shell 的故障窗口。
3. 16:12:56.483Z 控制器請求 close(4001)，真正 close event 為 **1006、wasClean=false**；兩者分開記錄。16:12:58.493Z 新 client2 先[讀回同 child](harness-gap-closure-unknown-child-evidence/reconnect-initial-child.json)及[同 inProgress turn](harness-gap-closure-unknown-child-evidence/reconnect-initial-child-turns.json)，16:12:58.494Z 才由控制器建立 gate。[原始 RPC](harness-gap-closure-unknown-child-evidence/rpc.jsonl)保存 request／event／新 initialize／query 順序；未丟主責 spawn tool 回覆、未改 server、未重送 turn/start。
4. [同原 turn 終態](harness-gap-closure-unknown-child-evidence/reconnect-child-turns.json)為 completed，最終精確 `G05_CHILD_RESULT g05-3e62e27f-7caf-4067-9749-eafaf5e6a5f1 KEEP_EXISTING_CONTENT`。child 只有兩個 shell 指令：先 `cat preserve.txt`，再有界 gate 輪詢／讀回；皆 exit 0，沒有寫檔、Node/Python/helper 或另派 agent，見[child 工具行 excerpt](harness-gap-closure-unknown-child-evidence/session-01a173d6-2300-7ff1-8cce-47d315fb2933.excerpt.jsonl)。[parent 終態 query](harness-gap-closure-unknown-child-evidence/query-parent-turns.json)也為 completed，並未把較早 `reconnect-parent-turns` 的 inProgress 當結束。
5. 原 parent／child 均終態後才送 SIGTERM。最初 workspace 內 signal 被拒的[錯誤](harness-gap-closure-unknown-child-evidence/error-restart-read.json)保留；外層核准只限自有程序 lifecycle，16:14:43.952Z 確認原 PID 不存在，再啟動 server2／client3。[新 server child metadata](harness-gap-closure-unknown-child-evidence/new-server-child.json)的 `notLoaded` 只表示未載入；真正接受依據是[同原 turn completed 與字面成果](harness-gap-closure-unknown-child-evidence/new-server-child-turns.json)。這是已終態儲存歷史跨 server 查回，沒有證明 running worker 跨 restart。
6. 每次列表使用此版本實際支援的 source／parent filters，持續至 nextCursor=null；[limit=1 多頁結果](harness-gap-closure-unknown-child-evidence/new-server-all-own-threads.json)含 auto-review guardian，廣義列表也沒有涵蓋全部已知 task thread，不能用空缺推定 worker 不存在。[最後 task-child 精確 filter](harness-gap-closure-unknown-child-evidence/final-task-children.json)使用 `sourceKinds=[subAgentThreadSpawn]`、原 `parentThreadId`，只查到原 task child；另以原生 spawn call 一次、確定原 handle 直接 read 及新主責未派工交叉核對無重派。guardian 是 auto_review 的宿主工作，不冒稱另一個 task worker，也不把列表當全機 inventory。

[初次恢復 checker green](harness-gap-closure-unknown-child-evidence/green-check.log)、[新 server green](harness-gap-closure-unknown-child-evidence/new-server-green-check.log)均有直接原始回應支撐。checker 原先錯將 requested close 4001 當 observed code，導致[checker 假設 red](harness-gap-closure-unknown-child-evidence/checker-close-code-assumption-red.log)，修正為核對實際 close event，未更動 raw 或放寬原 child／turn／成果驗收。

## 全新主責 thread 的能力界線

新主責為 `01a173d8-fa8f-7ae1-9aca-627a718ec36e`，第一回合 `01a173d8-faeb-7cc0-801d-f4b98b5635c3` completed。它沒有看到控制器 child result，只收到原合約路徑／handle／thread／turn 身分，[提示](harness-gap-closure-unknown-child-evidence/new-owner-prompt.json)與[原回合](harness-gap-closure-unknown-child-evidence/new-owner-turns.json)保留。

[真 query call／output 摘錄](harness-gap-closure-unknown-child-evidence/new-owner-query-excerpts.json)可回溯原 session 行號：`list_agents({})` 回傳當前 `/root running`，`list_agents({path_prefix:"/root/g05_reader"})` 回傳 `agents:[]`。這是其目前 root 的可觀測結果，不證原 worker 終態或不存在。模型沒有重派，也沒有把控制器 API query 冒充自身能力。

第一回合將 prompt「不跑 CLI」廣義理解為不可 shell cat，因而未讀取合約／技能且未寫回；這是控制器額外提示限制，不能據此宣稱產品無法讀檔。已保留[第一輪工具行 excerpt](harness-gap-closure-unknown-child-evidence/session-01a173d8-fa8f-7ae1-9aca-627a718ec36e-before-correction.excerpt.jsonl)與 snapshot，case/state 未刪，在同 state 的 server3（PID 14569）以 `thread/resume` 恢復同新主責 thread，見[resume readback](harness-gap-closure-unknown-child-evidence/new-owner-resume.json)。

取得新 slot 後，[澄清 prompt](harness-gap-closure-unknown-child-evidence/owner-correction-prompt.json)明確允許宿主普通檔案工具／shell cat；只禁止額外 codex／dispatcher／helper、state 查詢及 agents mutation。沒有供應控制器 child result。第二 turn `01a173e2-6fa6-7e63-8426-1525cf56060f` 在同 persisted 新主責 thread 完成，[完整 turn／命令與輸出](harness-gap-closure-unknown-child-evidence/owner-correction-turns.json)及[完整工具行 excerpt](harness-gap-closure-unknown-child-evidence/session-01a173d8-fa8f-7ae1-9aca-627a718ec36e.excerpt.jsonl)證明：

- 成功讀取 `project-setting.md`、原合約、task-harness／project-setting 與模型／合約規則、AGENTS；普通 shell 指令均 exit 0，排除第一回合的提示混淆。
- 真讀回本地 `preserve.txt=KEEP_EXISTING_CONTENT` 及 gate 內 task ID，只將它們當本地輸入／gate 現況，不當作原 child 返回結果。
- 再以原生 `list_agents` 查詢，仍僅目前 root，原 child 前綴為空；原 child 即時狀態／原 turn 終態／返回結果保留 unknown，不因控制器已知結果而替模型填通過。
- 成功更新並讀回[同一份原約](harness-gap-closure-unknown-child-evidence/artifacts-after-owner-correction/docs/plans/g05-3e62e27f-7caf-4067-9749-eafaf5e6a5f1.task-contract.md)，記錄可查的本地現況與無法核實的原生結果，T1 保持未完成；原 phase1 合約的 overall／T1 原本均為 `in_progress`，原 parent 兩次寫入都未寫 `done`，本輪沒有將既有已完成結果降級。API 的原 turn completed 與模型尚未核實仍分開。沒有建立另一份合約、spawn／followup／send／interrupt 或重做 T1。

判定：**本地同約續作與 unknown 時不重派通過；新主責跨 root 原生 child 查回能力未取得。** 不把普通讀檔成功、控制器 API 查回或模型誠實 unknown 等同模型已查明原 child 終態。

## 自有程序網路預連線負例

1. 最初在 workspace 沙箱內執行無副作用 `sandbox-exec ... true`，exit 71、`sandbox_apply: Operation not permitted`，[完整原始結果](harness-gap-closure-unknown-child-evidence/network-sandbox-qualification.json)保留。使用已核准的外層 `require_escalated` 後，同一限制型 profile／true exit 0，見[資格 readback](harness-gap-closure-unknown-child-evidence/network-sandbox-escalated-qualification.json)。這是程序繼承限制，不是變更系統網路。
2. profile 為 `(version 1)(allow default)(deny network-outbound)(allow network-outbound (remote ip "localhost:*"))`。第一個 hostname probe 得 `ENOTFOUND`，對「應為 EPERM」的 assertion 失敗；[真 red](harness-gap-closure-unknown-child-evidence/network-policy-probe.log)未刪。改以不依賴 DNS 的 TEST-NET `192.0.2.1` 後，[probe](harness-gap-closure-unknown-child-evidence/network-policy-probe.mjs)取得本案 loopback health 200 與 `connect EPERM 192.0.2.1:443`，見[原始 green](harness-gap-closure-unknown-child-evidence/network-policy-probe-direct-ip.log)。這只證政策生效，不是 provider request。
3. 另建立獨立 case `/private/tmp/g05-network-11689d5f-3c87-4586-a8e5-6acc60cef2f7/case`／state，使用同一候選及 demo 指示，state 0700、auth 0600。限制型 profile 內啟動原生 server PID 8198，loopback `ws://127.0.0.1:61779` 的 initialize／config／forceReload skills 成功；其[metadata](harness-gap-closure-unknown-child-evidence/provider-preconnect/metadata-preflight.json)與[config](harness-gap-closure-unknown-child-evidence/provider-preconnect/config-read.json)獨立於正常案。
4. 真 `turn/start` 僅一次：thread `01a173d1-e5f5-7210-9cab-c769082768ee`，turn `01a173d1-f23f-7e22-bf7b-2c02dcdb28e0`，提示只回覆字面值，不呼叫工具／建立 child。第一個 history query 命中 rollout 尚空的 `-32603`；[控制器真錯誤](harness-gap-closure-unknown-child-evidence/provider-preconnect/error-network-turn.json)保留。沒有重送 turn、換模型或 restart；新 client 查原 handle，得到[原 turn 終態 failed](harness-gap-closure-unknown-child-evidence/provider-preconnect/query-parent-turns.json)，error=`workspace routing discovery failed`、codexErrorInfo=`other`。
5. [原始 RPC](harness-gap-closure-unknown-child-evidence/provider-preconnect/rpc.jsonl)及[server stderr](harness-gap-closure-unknown-child-evidence/provider-preconnect/server1.stderr.log)顯示原生 sampling retry 的 routing discovery failure，另有 models／plugins／MCP 網路錯誤，MCP URL 為 `https://chatgpt.com/backend-api/ps/mcp`；這些不是 provider sampling URL。未收到 provider 模型回覆，不因出現 native「sampling retry」字樣就判成已到 provider sampling 層。
6. [session 工具行 excerpt](harness-gap-closure-unknown-child-evidence/provider-preconnect/session-01a173d1-e5f5-7210-9cab-c769082768ee.excerpt.jsonl)與[全部自有 threads](harness-gap-closure-unknown-child-evidence/provider-preconnect/final-own-threads.json)保存，只有原 thread、原 turn，沒有 child。全部已終態後才停止自有 PID；workspace 沙箱最初 signal 得 EPERM，保存[原錯誤](harness-gap-closure-unknown-child-evidence/provider-preconnect/error-network-collect.json)，外層核准後只對 PID 8198 送 SIGTERM，再以 ESRCH 確認退出，見[process proof](harness-gap-closure-unknown-child-evidence/provider-preconnect/process-exit.json)。[preservation](harness-gap-closure-unknown-child-evidence/provider-preconnect/preservation.json)確認原輸入及全域 auth/config hash 不變；state 保留，auth 未歸檔。

判定：**精確作用於自有程序的 network-deny 與原生 routing 預連線失敗通過取證；provider sampling、中途斷線、未知 child 啟動仍未因此通過。** 不再反覆改 endpoint 或錯誤探測以湊目標。

## 隔離及驗證安排

[config/read](harness-gap-closure-unknown-child-evidence/config-read.json)及 `skills/list forceReload=true` 的[完整回應](harness-gap-closure-unknown-child-evidence/skills-list.json)確認：四個 case 技能及 isolated state 的 bundled system skills 啟用，HOME 的 archify／define-task／project-setting disabled；沒有意外 enabled skill source，見[preflight 判定](harness-gap-closure-unknown-child-evidence/metadata-preflight.json)。本案 hooks=false，只測 transport／child，不代表正常 hook 信任已驗收。這是技能來源核對，不是封閉全部 native account tool 的證明；原生 startup 仍出現 `xcodebuildmcp` 初始化失敗等 warning，未修改它或把它列為產品依賴。受測模型實際使用 shell／apply_patch／collaboration；普通 shell 初始遇巢狀 sandbox 限制後，宿主 auto_review 核准的普通工具成功，原始失敗及成功都留在 raw。

[維護用 driver](harness-gap-closure-unknown-child-evidence/native-unknown-child.mjs)只使用已安裝 Node 26.7.0 built-ins，沒有新 runtime dependency。控制器允許 Node；受測產品模型提示禁止 Node／Python／helper。新控制器不取代模型的語義合約寫入。發生觀測 timeout 時保留 state、PID 及原 handle，不重派。

[checker](harness-gap-closure-unknown-child-evidence/check-evidence.mjs)以 public API 保存的原 turn 終態與已知字面成果作獨立核對，不只比控制器摘要。第一個[red](harness-gap-closure-unknown-child-evidence/red-check.log)因真 child readback 尚未存在而 exit 1，僅是「證據未完成」負例，並非產品 regression red。正式實驗已在真 child `inProgress`、gate 未放行時以同一 terminal/result assertion 取得[有效 precondition red](harness-gap-closure-unknown-child-evidence/active-child-red-check.json)，再於恢復後 green，另保留前述 close-code checker 假設錯誤。這是維護者 acceptance evidence check，不是改產品修 bug 的假 regression。

正常案先因其他案 provider 429／native backoff 等待排程；只在排程放行後新增模型 turn，原 handle 持續觀測，未重派。case/state 保留；已終態 server 的關閉與下一個 server 的身分分開記錄，不在待恢復階段刪 state。整體補驗仍有明確資格缺口，不以本案可測分支完成冒稱全部 V02 done。

最終[checker](harness-gap-closure-unknown-child-evidence/final-check.log)核對原身分、persistent／parent、故障前真 active、故障後同原 turn completed／精確輸出、原生 spawn 僅一次、新主責無 agents mutation、task-child filter 唯一結果及原輸入／global hash 保留；不是僅接受 driver 摘要。[最後 preservation](harness-gap-closure-unknown-child-evidence/preservation.json)與[network preservation](harness-gap-closure-unknown-child-evidence/provider-preconnect/preservation.json)均為 true。衍生 [session context](harness-gap-closure-unknown-child-evidence/session-contexts.json)只輸出必要 id／source／cwd／time／model／effort 白名單，沒有 creator account/user ID；完整 session 原件保留在私有 state（0700，原件 0600），Git 只存省 metadata 的透明 excerpt。[敏感內容 audit](harness-gap-closure-unknown-child-evidence/sensitive-audit.json)以 auth token／account_id leaf 及原 session creator identity 實值精確核對，僅輸出位置／key，不輸出值；全部公開證據的 token/API key、account/user identity 實值及 creator 欄位零命中，公開 session excerpt 無 session_meta 行。安全衍生 context 保留 type=session_meta 及白名單欄位；[第一次 audit 分類過廣](harness-gap-closure-unknown-child-evidence/audit-safe-context-type-red.json)將此安全型別也算 full metadata，修正為分別核對 excerpt 與衍生白名單，沒有刪除失敗紀錄。只有透明省 metadata，沒有修改其餘工具行冒充完整 raw。

全部已知 model／auto-review turn 都已終態後，[最終自有 server PID 14569 退出確認](harness-gap-closure-unknown-child-evidence/process-exit.json)為 true；8198／5495／11927 的較早退出各有原始 lifecycle 證據。兩案 case/state 保留供精確重查，沒有歸檔 auth，沒有殘留本案 listener。[文件核對](harness-gap-closure-unknown-child-evidence/document-check.json)記錄實際路徑／連結檢查；只改本報告、自有 supporting evidence 及 G05 ticket，未跑 full suite，由主責統一驗證。

2026-10-26 收尾：核對既有終態／退出證據及四個自有 PID 均為 ESRCH 後，只移除 normal／network 兩份已無需 sampling 的 owned `state/auth.json`；[cleanup receipt](harness-gap-closure-unknown-child-evidence/credential-copy-cleanup.json)記錄存在 → 刪除 → 不存在與操作前後全域 auth/config SHA 不變，兩案 case/state、私有完整 raw、IDs 及其他檔案保留。
