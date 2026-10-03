# Task Harness 原生證據與可攜性實驗

日期：2026-10-03。依據：[固定計畫](../plans/task-harness-portability-hooks-20261003.plan.md)。**本輪執行結束，P4 = Inconclusive。原生證據工具 PoC 成立，唯一候選完成；模型隔離 preflight 未通過，未採用候選、未修改正式版。**

## P1 已得到的直接證據

| 項目 | 結果 | 證據與限制 |
| --- | --- | --- |
| 正常命令 | exit 0，前後受測檔案 Git blob OID 相同 | [native-tool-results.json](task-harness-portability-hooks-20261003-evidence/native-tool-results.json)，E1。Git 2.56.0 是此宿主既有能力，不冒充所有宿主都有，也不將 OID 稱 SHA-256。 |
| misleading success | stdout PASS，真實 exit 7 | 同上 E2；直接保存個別 exec_command result，未以外層 batch 成功判定。 |
| 啟動不存在的 checker | shell exit 127 | 同上 E4；這是 shell 的結果，不是 runner 的 not_started/returncode=null。 |
| 版本失效 | actual.txt 修改後 OID 改變，expected.txt 未變 | [rehydration-source-change.json](task-harness-portability-hooks-20261003-evidence/rehydration-source-change.json)，不得用 E1 舊成功接受新版。 |
| 落盤與重新讀取 | 完整原始 tool inputs/results 自動序列化後，以新的 functions.exec isolate 從磁碟成功解析 | 同上；證明 primitive 可重讀，尚未證明模型在真實 resume 中正確使用。 |
| oracle 負例 | 6 個合成分支均符合預期 | [oracle-calibration.json](task-harness-portability-hooks-20261003-evidence/oracle-calibration.json)；缺 final exit、缺版本、source changed、unknown side effect 不接受。不是六筆 Skill 行為通過。 |
| 現況讀取範圍 | 原設定仍可讀歷史研究 oracle | [host-capabilities.json](task-harness-portability-hooks-20261003-evidence/host-capabilities.json)，只測 readable，不讀 verdict 內容。fresh prompt 不等於隔離。 |
| 原生 sandbox 隔離 | 單次受限 profile 讓 fixture 可讀、歷史 evidence 不可讀，exit 0 | [sandbox-host-retry.json](task-harness-portability-hooks-20261003-evidence/sandbox-host-retry.json)。第一次巢狀 sandbox 因 sandbox_apply Operation not permitted、exit 71 未啟動；經正式審核後，以相同限制在 host 執行成功。沒有改全域設定或繞過 trust。 |

## P1 能支持的結論

**在目前桌面 code-mode 宿主，既有 Git／檔案工具搭配原生結果自動保存，可以不用 Python runner，建立可重新讀取且綁定內容的命令證據。** 此結論只涵蓋已實測 primitives，允許製作隔離候選，不能先宣告 C1–C8 的完整行為驗收通過。

實際 evidence path 使用宿主內建 functions.exec JavaScript 編排、exec_command、apply_patch，以及既有 git/cat。沒有另開 Python/Node process 來包裝 receipt；研究盤點曾用 Python 計算正式檔案保留 hash，與受測 evidence path 分開。

保留的限制：輸出為 merged；shell command 字串不是 process argv；一般 apply_patch 不是 exclusive-create；Git 前後 OID 相同不是過程無修改證明；本地檔案可讀不是 crash durability 或防竄改保證。沒有將 chunk_id 假冒可跨 session 查詢的 receipt API。

## P2 候選與未完成的行為 gate

- P2 已完成：唯一[候選](task-harness-portability-hooks-20261003-evidence/candidate/task-harness/SKILL.md)只修改 evidence 路由與版本判讀；helper/yaml 與正式版 byte-identical。[版本與 diff](task-harness-portability-hooks-20261003-evidence/candidate-freeze.json)已固定。
- 官方 validator 首次因開發用 Python 缺 PyYAML 未啟動；使用已存在的 PyYAML 後[通過](task-harness-portability-hooks-20261003-evidence/candidate-validation-with-existing-yaml.json)。沒有安裝套件或修改候選；不能把 authoring dependency 誤記為 end-user runtime。
- P3：真實模型行為、resume、缺能力分支、plan-only、交接、選配相容性與乾淨安裝；固定矩陣與停止條件不變。
- 新模型宿主須先檢查工具與可見範圍；本次 sandbox probe 只驗證 shell 路徑，沒有證明 agent registry、MCP、app tools 的全部隔離。不能由 shell deny 外推其他工具。
- 若候選宿主不能自動保留足夠證據，或隔離無法成立，按計畫給 No-Go/Inconclusive，不將缺口移出 blocking gates。

## 來源及能力查證

- [固定執行前契約](task-harness-portability-hooks-20261003-evidence/protocol.md)保留案例與依賴聲明。
- [Codex permissions](https://learn.chatgpt.com/docs/permissions)：官方提供原生 filesystem read/write/deny profiles；本次以單次 CLI overrides 加入唯讀限制，沒有改設定檔。實際通過範圍以上述原始結果為準。
- [Codex config schema](https://learn.chatgpt.com/docs/config-schema.json)：查核 filesystem entries 與 named permissions 欄位；文件存在不等於 runtime 已驗證。
- [Hooks](https://learn.chatgpt.com/docs/hooks)：既有 hook 提醒、部分工具攔截與完整強制邊界仍分開。本次沒有新增 hooks。

## P3 實際結果與 P4 決策

固定[矩陣](task-harness-portability-hooks-20261003-evidence/matrix.json)為兩模型、兩 profiles，共最多四個 coordinator sessions。唯一實際啟動的是 `p3_61_native-execution` 的 plan-only／隔離 preflight，CLI session ID `01a101fd-fb50-7c41-9bda-7d64a282e847`。使用 gpt-6.1-sol/high 的啟動參數見[launch](task-harness-portability-hooks-20261003-evidence/runs/p3_61_native-execution/initial-launch.json)。沒有啟動 workers、其餘三個模型案例或 resume turn。

[原始 CLI events](task-harness-portability-hooks-20261003-evidence/runs/p3_61_native-execution/initial.jsonl)中的 command 完成結果同時是：

```text
INPUT_READABLE=yes
OUTSIDE_READABLE=yes
```

此 command 只測可讀性，沒有讀 canary 內容；canary 也沒有 verdict。模型隨後回報 ISOLATION_UNVERIFIED 並停止，尚未讀 Skill 或產生任務表／產品。這證明實際模型命令路徑沒有符合本輪的隔離要求，**不證明 Skill 行為失敗，也沒有發生歷史 verdict 實際污染**。

CLI 進程已透過原生 write_stdin 確認終止；原始事件含 turn.completed。進程 exit 0 只代表 CLI 正常結束，不代表隔離或驗收通過。`initial-completion.json` 是人工整理的 terminal 觀察摘要，已明確標示非原始 receipt；本判定依據 initial.jsonl 的原生 command result，不依據該摘要。

### 能力矛盾與根因界線

- `codex sandbox -P portability_p1` 的受限 profile probe 確實讓歷史 evidence 不可讀。
- 模型經 `codex exec`、`default_permissions=portability_p3`、同樣 root-deny/minimal-read/fixture-write 意圖啟動，實際命令仍可讀同層 scope 外 canary。
- 兩者是不同入口及 profile，不冒稱完全相同有效設定。官方 [permissions](https://learn.chatgpt.com/docs/permissions) 文件指出舊 sandbox settings 與 permission profiles 有選擇優先序；這是待查方向，**尚未證明本次原因就是設定覆蓋**。
- 尚未測得 agent registry 或所有其他工具路徑隔離。不能因一個 shell sandbox probe 通過就宣稱整個模型宿主被隔離；CLI 的 code_mode 功能亦顯示 under-development 警告，沒有證據證明此警告造成讀取範圍問題。

### 唯一結束決策：Inconclusive

依固定計畫的隔離與停止條件，P3 到此停止，不調整候選、不補樣，也不為完成矩陣啟動其他模型。所有未執行 gate 保持 unverified：C1 的完整 Skill 執行、C5 真正 agent resume、C7 plan-only 成果／雙 worker／交接、C8 選配 helper 的完整行為驗收，均不能由 P1 工具結果代替。

P1 證明 native evidence 的技術路徑值得保留；P2 候選仍只是未採用的研究產物。正式 Skill 仍維持 mandatory Python runner 的原行為；原交接 finding 與既有 backlog 沒有關閉。這次完成的是有停止條件的研究／候選／gate 判定，不是 portable Core 發布。

本輪沒有 runtime 修正、全域設定變更、依賴安裝、commit/push 或自動啟動下一輪。後續只建議獨立釐清模型命令路徑的有效 filesystem policy，再考慮新一輪驗收；此建議不屬本輪尚欠工作。

## 完成稽核與問題處置

[逐案例結果](task-harness-portability-hooks-20261003-evidence/case-results.json)與[完成稽核](task-harness-portability-hooks-20261003-evidence/completion-audit.json)直接解析原始 CLI events、驗證 candidate freeze、六個正式／無關檔案基準 hash 及文件連結。結果：**一個 coordinator preflight，零個完成的 Skill 行為案例，零 workers；其他三個矩陣案例未啟動。**

| 問題／觀察 | 處置 |
| --- | --- |
| PORT-HOST-ISOLATION-01：模型命令可讀 scope 外 canary | 阻止候選採用；獨立宿主隔離調查的直接依據。未歸因 Skill，也未聲稱修復。 |
| 巢狀 sandbox 無法啟動（exit 71） | 經正式審核以相同唯讀限制重試一次成功；原失敗保留，不視為 policy deny 成功。 |
| 開發用 validator 缺 PyYAML | 使用已存在的套件後通過，無安裝、無候選修改；這是開發環境問題。 |
| terminal 觀察摘要原先命名易混淆為 raw result | 已更名為 manually_transcribed_poll_summary 並補來源限制；排除於 receipt 判定，使用原始 initial.jsonl。 |

依 code-review-and-quality 的五軸檢視：候選變更範圍集中、未新增 production runtime；但缺完整行為驗證且隔離失敗，**不予採用／發布**。研究結果與停止決策可交付；沒有以靜態 validator、合成 oracle 或 CLI exit 0 取代未完成的 acceptance。

## 後續診斷附註（不改寫本輪結果）

使用者其後要求繼續，已在[隔離續作紀錄](task-harness-isolation-20261003.research.md)確認原 profile 有生效；同一 tmp canary 在兩入口均能實際讀取。差異與 macOS process scratch grants 一致，不能歸因 codex exec 忽略設定。單次 profile 加入明確 tmp deny 後，原 session 的實際讀取拒絕及 plan-only 續作完成；候選未變，完整功能仍未驗收。原 Inconclusive 與所有歷史 evidence 保留。
