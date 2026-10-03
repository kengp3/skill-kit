# 隔離判讀續作：固定診斷範圍

使用者於 2026-10-03 要求繼續。保留前輪 Inconclusive 與全部原始 evidence；本輪調查 PORT-HOST-ISOLATION-01，不先修改正式 Skill 或已凍結候選。

假設 H1：test -r 是 metadata/access 判斷，可能在 actual file-read 被拒時仍為 true。假設 H2：codex exec 的有效 policy 與配置意圖不同。假設 H3：有效 policy 正確，但實際工具路徑未強制執行。均先視為待證。

1. 讀前輪 session 的 selected turn_context metadata，保留 source-line hash，不匯出內部 reasoning；只作研究，不引入 Skill runtime dependency。
2. 使用前輪原封不動的 non-sensitive canary，比較 test -r 與實際 /bin/cat read 在明確受限 profile 下的結果。輸出僅此測試字串；不讀歷史 verdict。
3. 用原模型 session、相同 candidate 與同樣 read-deny profile，做一次實際 open/read probe。native tool 最終 rc 與 stdout/stderr 才能證明內容是否可讀；metadata alone 不再作接受／拒絕依據。
4. 若確認是 oracle 誤判，新增更正附註，不抹除歷史觀察；保持相同候選，先通過工具路徑隔離後再恢復驗收。若 actual read 可成功，保留 genuine isolation failure，不用放寬 policy 或刪掉 gate 取得綠燈。

不修改全域 host 設定、既有 hooks 或安裝依賴。每次原始 native result 以宿主自動序列化保留；命令與案例各自有結果，不以外層成功代替內層結果。

## 診斷後的最小設定修正

同一 canary 在原 profile 下實際可讀，因此排除 H1；session metadata 顯示原 profile 已載入，因此不支持設定被忽略的 H2。matching-tag 的 Seatbelt source 顯示 process platform defaults 會加入 scratch 存取。先前兩入口的比較還同時改變了目標位置，不能歸因入口。

本輪只修研究用單次 filesystem profile：增加 `/private/tmp`、`/private/var/tmp` 的 explicit deny，保留案例 workspace 的更窄 allow 及 inputs/skill 的 read-only。直接工具對照顯示此修正讓 own input 可讀、外部 canary 實際讀取失敗。使用者本次「繼續」範圍下，對原 session resume 驗證修正，不建立新 coordinator sample、不改候選、不改驗收標準。preflight 通過後只先完成原定 plan-only，再依 gate 決定執行。

後續若遇到必要宿主能力缺口，仍依原規則記錄並停止；不進行無上限的 permission/profile 調整，也不將此 shell/file probe 稱作所有工具的安全認證。
