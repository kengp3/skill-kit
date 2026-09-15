# 專案文件規範技能

## 目標與範圍
實作使用者已討論並要求執行的 project-setting：專案 root JSON 是文件位置與檔名的唯一設定來源。技能管理設定，專案指令與 hook 套用它，第三方技能不必修改。

預設 prd、spec、plan、adr、research。本次驗收平台為 Codex；使用者已明確要求跳過 Claude Code，現有 Claude 轉接程式保留為未完成實測的選用功能。第一版不檢查文件章節、不搬移歷史文件、不改第三方技能、不把任意 shell 程式視為可透明路由。

## 設定與行為
- `project-setting.json`：version=1；documents[type] 有 path、description、可選 match 檔名模式。支援 {slug} 與 {id}，其他佔位符拒絕。
- 不依賴 Git：明確指定的根目錄優先；未指定時向上尋找最近的 `project-setting.json`，找不到則使用目前目錄。Hook 安裝需要有效設定，啟動命令以設定定位 runtime，支援子目錄及專案搬移；不得回退到上層專案的 runtime。
- 初始化保留已有設定；平台安裝保留既有指令與 hooks。檔案放在 project root，目錄按需要建立。
- 成功識別且資訊足夠時，寫入前改路徑，通知 AI 實際位置。相同來源後續讀寫使用同一路徑。
- 缺設定、未知類型、多重匹配或缺 slug/id 時，暫停該文件寫入並讓 AI 建議既有分類或新增分類，詢問使用者；不自行確認。使用者可選既有類型、新類型或本次自訂目的地。
- 一次選擇不自動變成永久匹配規則；別名僅維持該來源文件的後續讀寫。修改設定影響新文件，不偷偷搬移舊文件。
- 同名目的地不覆寫；路徑不能逃出專案或寫入 .git、平台設定、技能本體；錯誤設定需明確回報。
- Codex apply_patch 是本次正式驗收範圍；Claude Write/Read/Edit 保留但未完成平台實測；shell 僅提供指引，不重寫任意程式字串。未知一般文件也可使用一次性位置選擇，README/AGENTS 等慣用入口與技能內部 Markdown 排除。

## 實作結構與命令
- `skills/project-setting/SKILL.md`：技能入口。
- `skills/project-setting/scripts/conventions.py`：設定與路由核心、CLI。
- `skills/project-setting/scripts/hooks.py`：Codex/Claude 適配及初始化整合。
- `tests/`：Python unittest、隔離整合驗證。
- `docs/plans/project-setting.plan.md`：任務清單與驗證狀態。
- 測試：`python3 -m unittest discover -s tests -v`
- 語法：`python3 -m compileall -q skills tests`

## 品質與邊界
使用標準函式庫，不新增套件；以小函式及明確 JSON 錯誤輸出處理失敗。機器 JSON 不混入日誌。核心範例：`resolve(root, source)` 回傳 destination 或 need_input。
禁止以刪測試、隱藏例外或放寬路徑驗證取得綠燈。hook 改參數不代表取得原本不存在的操作權限。驗證需區分本地回放與真正平台執行。

## 完成條件
1. 初始化及更新支援使用者 JSON、五種預設、自訂類型且可重複執行。
2. Codex 受管路徑能建立→讀取→修改；未匹配經使用者選擇後可續作。
3. 衝突、路徑逃逸、多重匹配、未知名稱、無設定、設定改動及無關檔案有測試。
4. 技能可單獨複製到隔離目錄運作，完成 validator、Codex 實際平台驗證與審查。
5. 正式文件寫明支援範圍、信任啟用程序及未覆蓋情況；不宣稱涵蓋所有檔案系統寫入。
