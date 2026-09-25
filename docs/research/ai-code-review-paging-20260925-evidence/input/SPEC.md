# 游標分頁重構驗收規格

輸入 `rows` 按唯一、遞增的整數 `id` 排序；`cursor` 是已交付的最後一筆 ID，初始值為 0；`limit` 與 `max_pages` 是正整數。`page_after` 必須只回傳 `id > cursor` 的資料。`list_page` 的 `next_cursor` 是該頁最後一筆 ID，空頁為 `None`。`export_ids` 應恰好輸出每筆 ID 一次並在資料結束時停止；`max_pages` 是防止異常分頁無限循環的保護。此次重構允許整理比較式，但必須保留上述對外行為。

本包是固定 base/head 檔案快照，沒有 Git commit、PR 或真實服務部署。
