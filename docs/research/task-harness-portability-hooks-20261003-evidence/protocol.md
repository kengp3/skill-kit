# P1 工具能力 PoC：執行前固定契約

本目錄只供研究，不是正式 Skill runtime。coordinator /root；task P1 attempt 1。

環境：本 thread 的 functions.exec／exec_command／apply_patch；macOS 本機。正式 SKILL、runner、spec、hooks 不修改。

## 能力與依賴聲明

- 用 functions.exec 的宿主內建 JavaScript 組合工具結果；不另開 Node 或安裝 runtime。這是 Codex code-mode 依賴，不外推所有宿主。
- 用原生 exec_command 執行既有 git 2.56.0 作為版本 fingerprint 與 fixture checker。Git 是此 PoC 的既有額外工具能力，並非證明所有環境不需 Git；不將它變成 Core 強制依賴。
- 用 apply_patch 保存完整序列化的工具輸入／結果；不由 LLM 人工抄寫 exit code 或 hash。普通 patch 不當 exclusive-create 或原子 receipt reservation。
- 執行前將每項 check attempt、命令、預期寫入本文件；每個命令分別取得原生 result。絕不把 functions.exec 的成功當 child exit 0。
- snapshot 命令本身與產品 check 的結果分開。Git blob object ID 標記 git-blob-oid，不冒充 SHA-256。

## 固定案例

1. E1 正常：以兩份相同文字 fixture 執行 git diff --no-index --exit-code；前後分別 git hash-object。預期 rc=0、兩次 OID 相同。保存 inputs＋原生 results，不建立新的 runner script。
2. E2 誤導：shell 內建 printf PASS 後 exit 7。這是被測 checker fixture 的 shell 語言需求，不是新增 evidence wrapper；預期原生 rc=7，不能接受。
3. E3 來源改變：修改 E1 的 actual.txt，再取得 OID；預期不能用 E1 的成功接受新版。保留原 receipt。
4. E4 啟動失敗：直接呼叫目錄內不存在的 executable；預期 shell rc=127，標示 command-not-found，不混成 run_check 的 not_started/rc=null。
5. E5 落盤重讀：下一個全新 functions.exec isolate 從磁碟讀回 receipt，核對所有原始結果與 E2 rc。這只證明 tool-level rehydration；未執行真實 agent resume 時，跨 agent-resume gate 仍列 unverified。
6. E6 oracle 負例：結果缺 final exit、缺版本、來源改變、unknown side effect，均不得接受／重播。這是合成 oracle 校準，不能計為 live Skill 行為通過。

無需為失敗案例「修到成功」。各命令只跑一次；receipt 讀取不是重跑 check。啟動、未知副作用、重試與排他保留的工具契約未能實測時，列 unverified，不以原始 runner 能力代替 native 能力。

模型隔離另作能力盤點；不列舉無關 actor 內容，不讀歷史 verdict 作驗收材料。P1 必要 gate 不成立時按計畫進 P4，P2/P3 不啟動。

## E7：查得原生權限 profile 後的受限能力探測

官方 permissions 文件提供 filesystem deny/minimal/精確路徑 read；本機 codex sandbox --help 提供單次 -P 與 -c overrides。以一次命令內的 profile 加上限制，不寫全域／專案 config、不放寬目前權限、不繞過 trust。

預期：fixture 可讀、歷史 offline-result.json 不可讀。若 sandbox 尚未啟動即失敗，只代表此環境未驗證該能力，不能說 policy 成功阻擋或 Codex 不支援。即使通過，也只證明 shell sandbox 的檔案隔離，不證明 app/MCP/agent-registry 隔離或真實模型 resume。
