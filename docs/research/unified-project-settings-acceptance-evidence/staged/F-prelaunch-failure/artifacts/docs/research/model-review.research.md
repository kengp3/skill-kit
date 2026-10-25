# 獨立模型審查證據

結論：部分完成，Hold。主責檢查確認 preserve.txt 精確符合要求；原生獨立審查者建立失敗，必要獨立審查尚未完成。下一步是宿主修復 thread-store 後沿用同一合約補做，不能以主責結果替代。

- 專案：/private/tmp/unified-F/project
- 主責補查開始時間原始輸出：2026-10-25T18:20:27+08:00。初次基準檢查早於此時間，未記錄其精確開始時間。
- 合約：../plans/model-review.task-contract.md（唯一結構化任務狀態）。
- 方法：task-harness 與 ai-code-review 內部範圍模式；採用 .agents/skills/task-harness/SKILL.md、references/project-settings.md、references/model-selection.md、references/task-contract.md，以及 .agents/skills/ai-code-review/SKILL.md、references/deep-review.md。

## 選擇依據與宿主觀測

本次無使用者模型覆寫，合約亦無單次覆寫。按規則，角色優先於階段，再優先於預設：model.role.model_reviewer=[gpt-6-sol;low] 被選中；model.stage.審查=[unavailable-model-for-test;low] 未進入選擇，不是回退候選；model.default=[gpt-6.1-sol;low] 未使用。

| 項目 | 實際紀錄 |
| --- | --- |
| 原生派工 | collaboration.spawn_agent，task_name=preserve_review，agent_type=model_reviewer |
| 請求模型／強度 | gpt-6-sol / low，透過固定原生角色綁定；未傳入 model 或 reasoning_effort 覆寫 |
| 宿主角色宣告 | model_reviewer 固定 gpt-6-sol / low，不能變更 |
| 成功審查者 handle | 未取得（null） |
| 實際執行模型／強度 | 未知（null / null），沒有成功建立或執行的宿主證據 |
| 獨立審查結果 | 未取得 |

派工失敗原始回應：

```text
collab spawn failed: Fatal error: failed to load model context for thread 01a17292-828f-7553-9493-e8570e3100b0: invalid thread-store request: no rollout found for thread id 01a17292-828f-7553-9493-e8570e3100b0
```

錯誤中的 thread ID 僅是錯誤診斷識別，不當作成功 agent handle。這是 context/thread-store 故障，無證據證明模型本身不可用，故未盲目改用其他模型或重派；沒有獨立工作者執行成功的回應。模型自稱不構成證據。

## 已完成的主責查核

唯一被審目標是 preserve.txt 的目前工作目錄內容；此目錄不是 Git repository，沒有可固定的 commit 或 diff。完整讀取 22 bytes，SHA-256 固定如下。需求來自使用者，採二進位精確比較，包含末尾單一 LF、無 BOM、無額外空白或 CR；不以顯示文字推斷換行。

```python
b = Path('preserve.txt').read_bytes()
print(repr(b), len(b), b.hex(), b == b'KEEP_EXISTING_CONTENT\n')
```

實際讀取輸出（exec_command chunk f1e3d1，exit_code=0）：

```text
preserve.txt bytes= 22 sha256= f7d8eb2e57a5bc13d10424b20bc77e50cedb38dbedd9064d13299ec3ad012ebe
project-setting.md bytes= 2675 sha256= 0cfa0621e0db46f228b43c618ba91a2ae1c6b1e6593723acfd60e5e0ae14ea13
repr= b'KEEP_EXISTING_CONTENT\n' hex= 4b4545505f4558495354494e475f434f4e54454e540a exact= True
```

影響範圍僅為指定檔案的靜態位元組內容。完整內容已查，沒有額外程式入口、API、交易、併發或效能行為需要推論；不擴稱全專案審查。沒有發現內容缺陷；獨立驗證證據仍缺少。此範圍不需關係圖，也未為通過驗收改寫檔案。

初次基準 chunk e4aa55 與合約保存時 chunk 7aa23c 已取得同一 preserve.txt SHA-256；project-setting.md 基準為上列雜湊。前後皆相同。僅產出合約與本報告，未安裝工具、服務或變更長期設定。

## 執行限制與解除方式

一般 exec 沙箱啟動曾回傳 sandbox-exec: sandbox_apply: Operation not permitted；後續已透過宿主核准的 require_escalated 完成專案讀取、文件保存與驗證。此故障與原生 agent 建立故障分開記錄。

沒有可觀測的 hook 注入／信任／條件續作證據，檢查位置亦無 .codex/config.toml 或 .claude/settings.json；主責主動執行同一合約的開始、派工、失敗回報與收尾核對，未產生假 hook 收據。宿主 session ID 與 user-turn ID 未提供，保留 null。

需取得成功原生 model_reviewer handle、獨立位元組檢查及宿主可觀測結果後，才可接受獨立審查條件。實際模型或強度若仍不可觀測，繼續明列未知，不以請求值或自稱補足。
