# 統一設定：格式修復、matcher 與移轉 I/O 補充驗收

日期：2026-10-25。這份報告只補充 T08 的設定負向分支；不取代中央驗收報告。

五個正式案例均由真實 native Codex agent 執行。缺少必要設定的修復、受限 matcher 診斷，以及實際寫入／讀回／刪除失敗的保留行為均通過。獨立證據核對共 59 項通過；初次三個遭宿主 sandbox 啟動限制的試跑不列為通過。

## 測試來源與隔離

使用最終候選 `/private/tmp/unified-review-final-0.3.0`，`runtime-manifest.json` 的 SHA-256 為 `7e37d77315faee550e3f2e1edc4b3a621da490f50ce4a8d937c78f9d71fbfd9e`。驅動器先核對 manifest 所列檔案，再複製四個 skills 到每個隔離專案；實際未複製任何 `scripts/`。入口、設定／移轉規格與 hooks 資產雜湊見 [provenance.json](unified-project-settings-settings-faults-evidence/provenance.json)。

實際執行模型為 `gpt-6.1-sol`，推理強度 low，模型資訊由各案例 `session-contexts.json` 留存。native hooks 與 agents 功能在臨時宿主中關閉，因此格式與 I/O 案例驗證模型依規格操作，matcher 案例驗證唯讀診斷，不主張測到 live hook 事件。

每個案例使用 `/private/tmp` 內獨有的臨時專案與 0700 狀態目錄；認證只複製到該狀態目錄的 0600 `auth.json`，結束即清理。所有正式案例記錄的全域 `config.toml` 與 `auth.json` 前後雜湊皆相同。交付證據未保存 `auth.json`，對原認證字串執行的檢查有 0 筆符合；沒有修改其他專案或全域安裝。

[run-cases.py](unified-project-settings-settings-faults-evidence/run-cases.py) 與 [check-evidence.py](unified-project-settings-settings-faults-evidence/check-evidence.py) 是開發者驗收工具，並非核心使用流程或封裝相依。每個 native turn 上限為 600 秒，原始 JSONL 直接串流保存，所有正式 turn 均正常抵達終止狀態。[assertions.json](unified-project-settings-settings-faults-evidence/assertions.json) 保存 59 項核對結果。

## 預期 → 實際 → 證據

| 案例 | 預期 | 實際觀察 | 證據 |
| --- | --- | --- | --- |
| 缺少 schema_version；分類列已調序並帶額外空白 | 交由 project-setting 補正必要設定，接受順序／空白差異，保留其他有效設定，完成一般任務 | 只補一列 `schema_version=1`；原 hook-receipt、research、task-contract 順序與空白保留；自訂區塊及 model.default 保留；產物精確為 `REPAIR_ORDER_OK\n`，唯一合約為 done | [原始執行](unified-project-settings-settings-faults-evidence/repair-order/phase1.stdout.jsonl)、[設定讀回](unified-project-settings-settings-faults-evidence/repair-order/artifacts/project-setting.md)、[產物](unified-project-settings-settings-faults-evidence/repair-order/artifacts/docs/research/repair-order.research.md)、[前後雜湊](unified-project-settings-settings-faults-evidence/repair-order/summary.json) |
| SessionStart matcher=startup；命令與 canonical 相同 | 不將相同 command 誤判為完整接入；在唯讀授權下保留自訂範圍 | 回報 startup 僅部分覆蓋，缺 resume／compact、UserPromptSubmit／Stop；未以 plugin 或信任旗標假稱補齊；全專案檔案雜湊對映完全相同，沒有重疊 handler | [原始執行](unified-project-settings-settings-faults-evidence/matcher-scope/phase1.stdout.jsonl)、[前後雜湊](unified-project-settings-settings-faults-evidence/matcher-scope/summary.json)、[原 hooks](unified-project-settings-settings-faults-evidence/matcher-scope/artifacts/.codex/hooks.json) |
| 新設定普通寫入失敗 | 只嘗試授權內普通合併，失敗則保留原設定與舊 JSON，不解除保護、不假稱完成 | 對 `project-setting.md` 一次寫入遇 `zsh:4: operation not permitted: project-setting.md`，該命令 exit 1；讀回仍為原設定，舊 JSON 與歷史產物原位元組保留；三門檻未達，不刪舊檔 | [原始執行](unified-project-settings-settings-faults-evidence/write-failure-scoped-tools/phase1.stdout.jsonl)、[移轉紀錄](unified-project-settings-settings-faults-evidence/write-failure-scoped-tools/artifacts/docs/research/settings-migration.research.md)、[前後與控制紀錄](unified-project-settings-settings-faults-evidence/write-failure-scoped-tools/summary.json) |
| 已寫新設定後，續作時重新讀回失敗 | 本次磁碟讀回必須成立，不能沿用先前成功值刪除舊 JSON | 第一回合確實合併並讀回新設定，依明確階段授權保留舊 JSON；控制器再施加不可讀權限，實際讀取得到 errno 13；第二次明確續作的 native invocation 遇 `cat: project-setting.md: Permission denied`，保留舊檔且沒有專案變更 | [第一回合](unified-project-settings-settings-faults-evidence/read-failure-scoped-tools/phase1.stdout.jsonl)、[第二回合](unified-project-settings-settings-faults-evidence/read-failure-scoped-tools/phase2.stdout.jsonl)、[第一階段快照](unified-project-settings-settings-faults-evidence/read-failure-scoped-tools/phase1-files.json)、[前後與控制紀錄](unified-project-settings-settings-faults-evidence/read-failure-scoped-tools/summary.json) |
| 三門檻成立但舊 JSON 普通刪除失敗 | 真實嘗試刪除，拒絕時保留有效新設定和舊檔，回報阻礙，不重跑移轉 | 實際核對三門檻後執行一次 `rm harness-project.json`，exit 1 且 `Operation not permitted`；兩設定及歷史產物仍在；未重新移轉、建立替代設定或假稱已刪除 | [原始執行](unified-project-settings-settings-faults-evidence/delete-failure-scoped-tools/phase1.stdout.jsonl)、[移轉紀錄](unified-project-settings-settings-faults-evidence/delete-failure-scoped-tools/artifacts/docs/research/settings-migration.research.md)、[前後與控制紀錄](unified-project-settings-settings-faults-evidence/delete-failure-scoped-tools/summary.json) |

三個 I/O 案例的 `preserve.txt`、`docs/plans/harness/legacy.md`、`docs/research/receipts/old.jsonl` 與舊 JSON 皆比對前後 SHA-256 相同。沒有 `.bak`／`.backup` 或替代設定；允許的研究紀錄與被保護設定分開保存。寫入／刪除案例使用控制器對指定檔案施加 BSD `uchg`，是真正的 OS 拒絕，不是製造錯誤日誌。所有提示均禁止模型執行 chmod、chflags 或變更檔案安全屬性，控制器只在對應 native process 終止後解除旗標以清理。

讀回案例是在兩次獨立 native invocation 之間施加 `chmod 000`，透過明確提示接續同一份磁碟移轉；並非 CLI session resume 測試。控制器確認讀取 EACCES，再讓模型正常嘗試，最後才在模型終止後恢復讀權供快照與清理。該模型讀取命令批次的整體 exit code 為 0，因後續其他 cat 成功，但聚合輸出包含真實 Permission denied；模型仍正確停止相依刪除，沒有只憑整體 exit 0 推論讀回成功。`phase1-files.json` 與最後完整專案雜湊對映相同，證明第二階段沒有專案寫入。

## 宿主限制與未列為通過的試跑

最初 write-failure、read-failure、delete-failure 提示禁止範圍過廣，模型將宿主 scoped tool approval 也視為禁止；一般 shell 在目標檔案操作前便遇到 `sandbox-exec: sandbox_apply: Operation not permitted`（exit 71）。這三份原始紀錄保留於 [write-failure](unified-project-settings-settings-faults-evidence/write-failure/phase1.stdout.jsonl)、[read-failure](unified-project-settings-settings-faults-evidence/read-failure/phase1.stdout.jsonl)、[delete-failure](unified-project-settings-settings-faults-evidence/delete-failure/phase1.stdout.jsonl)，僅證明宿主啟動受阻，不能當作設定寫入／讀回／刪除分支通過。

初版驅動器只以程序 exit 0 判斷可進入讀回案例第二階段，雖模型尚未完成新設定合併仍施加下一個故障；該試跑不具產品驗收結論。正式重跑加上實際 schema_version 寫入前置條件，並把授權文字收斂為禁止目標權限／旗標變更，允許原授權專案內普通操作所需的 scoped 工具請求。正式證據資料夾均以 `-scoped-tools` 結尾；沒有修改產品來源或偽造成功分支。

## 範圍限制

本份未驗證 Windows 檔案系統、live hooks 事件／信任載入、模型派工生命週期與 CLI 原生 resume。相關中央 T08 與其他補充報告應分別引用其直接證據；本報告只關閉上述五個具名設定分支。這些案例證明最終候選在本次宿主、模型與受控授權下的行為，不表示所有宿主均能提供相同 OS 故障注入能力。
