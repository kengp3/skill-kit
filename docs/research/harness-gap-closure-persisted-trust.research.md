# G03：V01 正常持久 hook 信任

日期：2026-10-25（Asia/Taipei）。**驗證狀態：受阻，等待正常人工審閱及明確核准；未宣稱 V01 通過。**

## 預期與目前觀察

預期：使用者在正常介面審閱精確 hook 定義；不 bypass、不改信任資料庫；同一專用 state 的兩個 invocation 各完成小任務，均保存持久信任、實際提醒與終態證據。

目前已建立 demo 現行語意的獨立 case，原樣保留 AGENTS、project-setting、專案 hooks/config，從指定凍結 0.3.0 候選複製四個 skills 的非 scripts 資源並核對 manifest。正常原生 CLI 的文字 hook 審閱介面可用；尚未執行信任。`hooks/list` 確認五個 project 定義均 untrusted，sourcePath 全部為本 case 的 `.codex/hooks.json`，enabled 不作實際執行證據。

## 人工審閱與存續狀態

精確定義、currentHash、來源、風險及操作位置在 [人工審閱包](harness-gap-closure-persisted-trust-evidence/human-review.md)。保留活躍 exec session `49562`、TUI PID `98889`；專用 state `/private/tmp/g03-persisted-trust-state` 為 0700、auth 為 0600，認證位於 repo 與證據之外。case `/private/tmp/g03-persisted-trust-case` 不修改 demo。保持 state 至同案第二次 invocation 完成；人工等待不清理、不重啟。

project trust 已在專用 config 設定，只讓 project layer 載入；五個 hook trust 仍未完成。正常 TUI 明列 Hooks need review，並顯示完整命令與 `t trust`／`t trust all` 操作。審閱頁可經自有 terminal resize 完整顯示；沒有操作 Codex Desktop CUA 或 AppleScript。

## 證據與判定

| Expected | Observed | Raw | Verdict |
| --- | --- | --- | --- |
| 凍結候選與 demo 現行來源一致 | manifest 與 21 個非 scripts 資源逐檔核對；demo 四個基底檔 SHA 相同 | [preparation.json](harness-gap-closure-persisted-trust-evidence/preparation.json) | 前置通過 |
| 禁用 HOME 技能，原生載入本案四技能 | skills/list 確認三個 user disabled、四個 repo enabled | [skills-before.json](harness-gap-closure-persisted-trust-evidence/skills-before.json)、[plugins-before.json](harness-gap-closure-persisted-trust-evidence/plugins-before.json) | 前置通過 |
| 正常 exact-definition 人工信任 | CLI 正常審閱頁可用；尚未核准；五個仍 untrusted | [hooks-before.json](harness-gap-closure-persisted-trust-evidence/hooks-before.json)、[覆核 hooks/list](harness-gap-closure-persisted-trust-evidence/pre-review-check/hooks-list.json)、[TUI 寬版 raw](harness-gap-closure-persisted-trust-evidence/tui-review-wide.raw.txt) | 受阻：等候人工 |
| 同 state 兩次 invocation 的提醒、hook events 與 completed | 尚未啟動任務；不得以 enabled 冒稱已執行 | [review-state.json](harness-gap-closure-persisted-trust-evidence/review-state.json) | 未執行 |
| 日常 auth/config 保留 | 準備後 global hashes 與前置一致 | [review-state.json](harness-gap-closure-persisted-trust-evidence/review-state.json) | 目前保留 |

最小解鎖條件：使用者審閱人工包的完整 exact JSON／來源／hash，明確授權在既有正常 CLI 介面執行同一信任操作。之後仍須完成兩次 invocation 與直接證據，不能因核准就判 V01 通過。其他工作包可繼續。

官方依據：[Hooks — Review and trust](https://learn.chatgpt.com/docs/hooks)（本次已讀取）：非 managed 定義需審閱，信任綁定目前 hash，`/hooks` 提供正常信任介面。此說明支持試驗方法，不替代本案實際信任證據。

略過未獲人工核准的信任動作及兩次任務；保留專用 state 內的認證供同案恢復，V01 尚未通過。
