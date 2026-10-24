# 任務合約與必要 hooks：整合驗證

日期：2026-10-25。整合分支 `codex/task-contract-hooks`。來源與離線候選完成；整套 Desktop harness 尚未完成，H05 保留必要缺口。

## 交付與直接證據

本輪恢復 task-harness 的任務生命週期，加入固定 Markdown／JSON 合約、Python 三事件 handler、一次補救技術收據與完整封裝。明確啟用由 skill 設定及流程共同表達；hook 不修改合約或自行取得授權。

最終產品來源：`81497d5d6c02a05598b6d8a2aadd305378509a87`。後續本報告與 tracker 提交不更動候選內容。

- 最終完整離線回歸：發現 102 項，101 項通過，1 項 Windows 原生測試跳過；12.011 秒，Python 3.15.0。[命令、版本及原始輸出](task-harness-lifecycle-evidence/integration-final.json)。
- 修正前完整回歸曾有 99 項通過、1 項跳過；仍由獨立審查找出缺口，保留[原始結果](task-harness-lifecycle-evidence/integration-before-review-fixes.json)，不改寫成修正後證據。
- 候選：`dist/candidates/personal-harness-0.2.0`，22 個 manifest 內容檔。manifest SHA-256：`3d7924929d77a659a7b67237e147f6d8150b5f10146da0e5086e8b08e348b9d5`。
- 實際候選在 checkout 外通過三事件 fixture；重複 Stop 不補發、合約不變；之後再驗內容 manifest 通過。[候選與保護檢查](task-harness-lifecycle-evidence/candidate-final.json)。
- 1,334 個既有保護檔案內容雜湊均未變，含日常 `.codex/config.toml` 的原有未提交還原及 1,333 個未追蹤檔案。未安裝候選、改啟用版本／快取、操作其他專案、push 或建立 PR。

## Standards

固定審查 `6829db5...75cf075`。獨立 reviewer 發現兩個 P2，屬信任邊界錯誤：

1. `cwd.is_relative_to(root)` 只做詞法判斷，`root/../other` 可取得補救。修正為保留 symlink 拒絕後解析實際 cwd，再查找與核對歸屬。
2. Python 3.15 的 `Path.glob()` 吞掉不可讀目錄錯誤，可能回傳空結果。改用會回報失敗的 `iterdir()`，沿用未就緒錯誤出口。

獨立複核 `b94b6e9`，兩個公共 CLI 負例實跑 2/2 通過；原 findings 全數關閉，新增 0。沒有為 smell 加入新抽象或無關重構。

## Spec

同一固定版本的獨立 Spec review 發現兩個 P2：cwd 歸屬錯誤（與 Standards 重複），及技能未設定 `policy.allow_implicit_invocation: false`。後者已補，對齊任務級明確啟用。

獨立複核 `b94b6e9`，hook 公共 CLI 26 項實跑通過；原 findings 全數關閉，新增 0。三個獨立問題的 red／green、設定與套件讀回證據見[修正紀錄](task-harness-hooks-review-evidence/review-fixes.research.md)。H05 未被改寫為可選或已通過。

## 需求對帳

| 必要行為 | 目前證據與界線 |
| --- | --- |
| 任務級啟用、唯一合約、五種狀態、必要成果對帳 | skill／reference 已實作；候選保留明確啟用 policy；真實模型遵循仍待 H05 |
| 執行前保存、依賴、授權、單一主責、跨對話接手 | skill 流程及完整合約範本；CLI 核對 schema／歸屬／依賴。離線不證明模型每次保存或安全接手 |
| 恢復、最新要求核對、有效授權內一次補救 | 三個事件與實際套件命令測試通過；宿主原使用者回合識別仍未合格 |
| 討論、停止、取消、blocked、過期授權不推進 | CLI 負例通過；使用者原生 Stop 與模型遵循須真實宿主驗證 |
| 未知操作先核對、不重播，讀取／收據失敗明示 | CLI 負例、不可讀目錄與部分 reservation 檢查通過；不宣稱語意提示可保證模型行為 |
| 重複／並行收尾最多一次、切任務不重置 | exclusive-create 收據、八事件並行、輸出遺失與 task 切換負例通過；原始 user-turn 真實鏈路仍屬 H05 |
| Python、完整候選、自含依賴、可辨識版本 | 22 檔內容 manifest、缺失／連結／篡改／覆寫拒絕及獨立目錄實際命令通過 |
| 不影響日常作業、低使用負擔 | 未安裝、不改日常設定；agent 維護合約，無人工監看或表單。實際負擔與省時效果尚無新模型證據 |

## 未完成與採用限制

H05 仍需要可用且明確授權的 Desktop 專案接入，取得 Python 啟動、hook 載入／信任、三事件、原始使用者回合與自動續作鏈、原生 Stop、跨對話恢復及模型遵循的直接證據。目前「不執行新模型 trial」限制仍有效，本輪新 trial 為零；不能用合成 host=true 取代資格。

Python 3.10 僅通過語法解析，未實跑該 runtime；Windows 新 hook 命令亦未原生驗證。候選未安裝，不能當成目前 Desktop 使用中的版本。來源／封裝完成不代表整套 harness 驗收完成。

## Retro

- 實際教訓：綠燈未涵蓋 `..` 與不可讀目錄；已將兩個可重現問題轉為既有公共 CLI 測試，無須另建監控框架。
- 接入設定也是行為的一部分；已修正明確啟用 policy，後續 Desktop 驗收要讀取實際載入版本，不能只看來源文件。
- Repo 沒有發現統一 CI／pre-commit 閘道。現有完整回歸含平台及子程序控制測試；未在本輪新增會影響每次開發的全域／自動關卡。日後若需要 CI，優先接既有 hook／package 公共測試，不另造測試框架。
