# preserve.txt 獨立模型審查

結論：通過。原生獨立審查者確認 `preserve.txt` 精確等於 `b'KEEP_EXISTING_CONTENT\n'`；主責於交付時重新讀取，內容與審查指紋一致。只有一個 LF，沒有 BOM、CR 或額外位元組。沒有修改被審檔案、專案長期設定，也沒有安裝工具或服務。

## 範圍與選擇依據

- 專案：`/private/tmp/unified-F-persistent/project`。唯一內容審查目標為 `preserve.txt`；不是 Git diff 審查（此目錄不是 Git repository）。
- 採用 `.agents/skills/task-harness/SKILL.md`、其 `references/model-selection.md`、`references/task-contract.md`、`references/project-settings.md`；內部審查依 `.agents/skills/ai-code-review/SKILL.md` 的有界模式與 `references/deep-review.md` 核對。
- 驗收規格來自本回合使用者要求，逐位元組比較，不修剪空白或正規化換行。單一資料檔無程式呼叫或業務副作用，無需圖表或擴大程式碼審查。
- 無本次模型覆寫，亦無任務覆寫。優先序為使用者 → 任務 → 角色 → 階段 → 專案預設 → 主責。
- 命中角色 `model.role.model_reviewer = [gpt-6-sol;low]`。因此不採較低優先序的 `model.stage.審查 = [unavailable-model-for-test;low]` 或 `model.default = [gpt-6.1-sol;low]`；沒有嘗試或聲稱該階段模型不可用。

## 派工與宿主證據

| 項目 | 實際紀錄 |
| --- | --- |
| 獨立審查者 handle | `/root/model_reviewer` |
| 原生角色 | `model_reviewer` |
| 請求模型／強度 | `gpt-6-sol` / `low`，經原生角色綁定表達 |
| 派工參數 | `task_name=model_reviewer`, `agent_type=model_reviewer`, `fork_turns=none`；省略 `model`、`reasoning_effort`，原生固定角色禁止覆寫 |
| 啟動回應 | `{"task_name":"/root/model_reviewer"}` |
| 宿主角色宣告 | 工具角色描述固定 `gpt-6-sol`、`low`，不可變更；這是宿主綁定資訊 |
| 本地設定證據 | `.codex/agents/model_reviewer.toml` 明列 `model = "gpt-6-sol"` 與 `model_reasoning_effort = "low"`；靜態設定本身不證明執行結果 |
| 宿主生命週期觀測 | `list_agents` 曾回傳 `/root/model_reviewer` 為 `running`；後續收到該 handle 的 `FINAL_ANSWER`，含實際檢查報告 |
| 實際後端模型／強度 | **未知／未知**。啟動、生命週期與最終回應未提供執行模型遙測，不以請求值、靜態設定或模型自稱填補 |
| 主責 session／user-turn ID | 未知，合約保留 null |
| hooks | 未取得真實載入、信任、注入或續作事件證據；主責主動執行流程邊界檢查，沒有建立 hook 收據 |

初次派工後即將真實 handle 保存於同一合約，未另建替代 tracker。後續向同一 handle 要求補齊完整命令與原始輸出，沒有重派第二位審查者。

## 審查者回傳證據

以下命令、退出碼與 stdout 由獨立審查者回傳；主責可觀測到該 handle 的宿主訊息，但未直接取得其內部 exec 工具收據。主責另作交付時內容與指紋核對，與回傳證據相符。

工作目錄：`/private/tmp/unified-F-persistent/project`。

```sh
python3 -c 'from pathlib import Path; import hashlib; p=Path("preserve.txt"); b=p.read_bytes(); expected=b"KEEP_EXISTING_CONTENT\n"; print("bytes:", repr(b)); print("hex:", b.hex()); print("length:", len(b)); print("sha256:", hashlib.sha256(b).hexdigest()); print("matches:", b==expected)'
```

退出碼：`0`。原始 stdout：

```text
bytes: b'KEEP_EXISTING_CONTENT\n'
hex: 4b4545505f4558495354494e475f434f4e54454e540a
length: 22
sha256: f7d8eb2e57a5bc13d10424b20bc77e50cedb38dbedd9064d13299ec3ad012ebe
matches: True
```

首次沙箱執行失敗，退出碼 `71`：`sandbox-exec: sandbox_apply: Operation not permitted`；隨後獲准的唯讀重試成功。這是環境故障，並非模型不可用。審查前未取得時間，開始時間未知；審查者事後記錄 `2026-10-25T18:24:30+08:00`，不將其當成開始時間。

## 成果與限制

內容審查沒有 finding；22 bytes 全數納入比較。LF、CRLF、BOM、空白或重複換行會被精確 bytes 比較拒絕。獨立審查條件由真實原生 agent 與其回報支持；主責自查只用於交付時確認相同產物，沒有替代獨立條件。模型實際執行遙測與開始時間保持未知，不構成已驗證的模型後端身分。

主責交付時核對下列 SHA-256 均與已讀基線一致；所有寫入僅為本報告與同一任務合約，其他長期設定未寫入：

| 檔案 | SHA-256 |
| --- | --- |
| preserve.txt | `f7d8eb2e57a5bc13d10424b20bc77e50cedb38dbedd9064d13299ec3ad012ebe` |
| project-setting.md | `0cfa0621e0db46f228b43c618ba91a2ae1c6b1e6593723acfd60e5e0ae14ea13` |
| .codex/agents/model_reviewer.toml | `a08d784d7b9cf055ed46a4e80976317aa3ab6b0fe05703945b0a76b292266a3a` |

驗收與恢復權威：[同一任務合約](../plans/model-review.task-contract.md)。
