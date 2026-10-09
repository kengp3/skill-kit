# 第二階段：全目標關聯與影響

- pricing.py 唯一區塊：目的為將折扣邊界納入 1000 cents；原為 >1000，新為 >=1000，扣減固定 100 cents。完整函式只有兩行。入口為 api.checkout(cents)，傳入原整數，回傳 payable_cents；無外部呼叫或狀態副作用。影響為有效輸入恰好 1000 時從 1000 變成 900，這是核准功能而非回歸。
- api.py 未修改責任：公開入口先以 type(cents) is int 排除 bool、float 等，再以 cents < 0 排除負數，非法輸入皆 ValueError("amount")。guard 短路，不對非整數做大小比較；合法值才呼叫 price。
- 兩版本完整 Git 樹只有此兩檔；搜尋所有 caller 結果見 source-reads.json。price 是內部運算而非 contract 規定之公開 API，無須重複加入 checkout 已有 guard。沒有配置、交易、付款或持久化。
- 需解釋的問題是公開入口如何驗證與折扣邊界如何影響回傳，因此最終報告採一張流程圖，保留拒絕分支與比較條件。拓樸不變，舊条件用文字交代即可。
- 分析對帳：1/1 diff 檔案、1/1 區塊及必要 caller 已讀。以下進入深度查核，獨立以 contract 定義測試預期，不以現有實作作 oracle。
