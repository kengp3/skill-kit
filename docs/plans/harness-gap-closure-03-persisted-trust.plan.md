# G03：V01 正常審閱及跨啟動持久信任

**What to build:** V01 正常審閱及跨啟動持久信任；交付完整外部行為及可核對證據。

**Blocked by:** G01; normal human review interface

**Status:** done — 使用者已審閱並明確核准；正常 CLI 信任與同 state 兩次全新 invocation 驗證通過

依據：[補驗規格](../specs/harness-validation-gap-closure.spec.md)、[核准工作圖](harness-validation-gap-closure.plan.md)、[可行性研究](../research/unified-project-settings-gap-fixtures-feasibility.research.md)。使用者已核准拆分與驗收邊界；G08另經明確排除。

## 驗收條件

- [x] 不使用bypass或改寫trust資料庫，正常審閱exact hook定義且保留過程。
- [x] 同state兩次invocation均有信任狀態及實際提醒證據。
- [x] project trust與hook trust分開，人工待完成時保持受阻。

## 本次結果

使用者直接回覆「已審閱，同意正常信任這五項精確定義」後，核對原定義 bytes／五個 currentHash 與正常 TUI，執行正常 `t trust all`；沒有 bypass 或直接寫 trust 資料庫。原預備 TUI 正常退出，不計入 post-trust invocation。

同 state 的兩個全新原生程序各完成一項固定 20-byte 成果與該任務唯一 done 合約；五項信任及 hash 均保留，每次兩個 SessionStart 提醒及 UserPromptSubmit 提醒真正進入 developer 訊息，Stop hook 也正常 completed。原生程序與全部命令項目已到終態，再清除 owned auth 副本；state／完整私有 raw 保留。清除 auth 後唯讀 hooks/list 仍顯示五項 trusted。

交付 [驗證研究](../research/harness-gap-closure-persisted-trust.research.md)、[正常信任操作來源配對](../research/harness-gap-closure-persisted-trust-evidence/normal-trust-operation.json)、[獨立事件／上下文核對](../research/harness-gap-closure-persisted-trust-evidence/observed-check.json) 與 [收尾證據](../research/harness-gap-closure-persisted-trust-evidence/cleanup.json)。[人工審閱包](../research/harness-gap-closure-persisted-trust-evidence/human-review.md) 保留為核准前歷史快照，不重寫精確定義／hash。驗證只支持本 case／state 的 V01；Windows、Desktop 及未觸發的 SubagentStart 不由本案外推。

## 證據要求

保存候選／宿主／任務身分、expected → observed → raw → verdict及無關內容保留證據。控制器exit 0、模型自述、fixture或checker不單獨證明通過。未驗證與受阻保留，不以實作完成取代行為驗收。
