---
name: project-setting
description: Initialize, customize, explain, or troubleshoot a project's document placement conventions for PRD, spec, plan, ADR, research and user-defined types. Use when setting up project document structure or resolving an unclassified document; this skill manages placement, not the document's subject matter.
---

# 專案文件規範

在專案根目錄以 `project-setting.json` 定義文件位置。技能管理設定；專案指令與 hook 讓後續第三方技能也套用它。

Codex 已完成 macOS 實際平台驗收；Windows 相容程式已補齊，原生平台驗收尚未完成。Claude Code 依使用者要求跳過；其轉接程式僅通過本地回放，尚未完成實際平台驗證，預設不安裝。

## 初始化

1. 確認使用者指定的專案根目錄、已有設定與平台指令。已有 Git 儲存庫以其根目錄為界；沒有 Git 時先說明 hook 安裝目前需要 Git，不自行建立儲存庫。
   若發現舊版 `project-conventions.json`、`.project-conventions/` 或舊 Hook 註冊，先說明需要遷移並保留原設定與狀態；目前沒有自動遷移，不直接並裝新版。
2. Windows 先確認 `py -3 --version` 為 Python 3.9+，以下 `python3` 指令改用 `py -3 -X utf8`；Git 與 Python launcher 必須在 Codex 的執行環境可用。macOS/Linux 使用 `python3`。
   使用隨技能附帶的腳本（下文 SCRIPT 指本技能 scripts/ 下實際絕對路徑）：
   `python3 SCRIPT/conventions.py --root PROJECT init`
   使用者提供 JSON 時加 `--config FILE`。已有設定不覆寫。
3. 依使用者實際使用的平台執行：
   `python3 SCRIPT/hooks.py install --platform codex --root PROJECT`
   或 `--platform claude`。只安裝要求的平台，保留既有指令與設定。
4. Codex 既有 `.codex/config.toml` 保持原樣；確認 `[features]` 下 `hooks = true`。若使用者原本設為 false，先告知這會停用整合，依使用者啟用意圖調整，保留其他設定。在 `/hooks` 審查並信任新增 hook，再開始新工作階段。Claude 從專案 root 開始新工作階段。既有專案更新時重新執行 install，以更新 runtime 及補入 `commandWindows`；更新後重新審查 Hook。設定檔存在不等於已成功載入；用一次建立→讀取→修改確認。

## 解讀與調整

- `python3 SCRIPT/conventions.py --root PROJECT show` 查看設定。
- `python3 SCRIPT/conventions.py --root PROJECT resolve SOURCE` 取得分類結果與目的地。
- 使用者明確要求更改設定後，準備保留其他項目的完整 JSON，再執行 `configure FILE --confirmed`。不要藉更新設定搬移既有文件。
- 五種預設為 prd（產品目標）、spec（系統行為與驗收）、plan（實作步驟）、adr（架構決策）、research（研究證據）；不是每個功能都必須建立五份文件。

## 分類需要使用者決定時

看到 `need_input` 或 hook 的分類提示：

1. 看文件用途、當前設定與候選類型。提出一個最合適的既有分類及理由；確實沒有合適類型才建議新類型與路徑。
2. 每次詢問一個關鍵選擇，提供沿用既有類型、新增類型或本次位置。缺設定時先詢問是否初始化；未得到答覆不自行同意。
3. 確認後，以 `choose SOURCE --type TYPE --slug NAME [--id ID] --confirmed` 保存這份文件的路徑；本次位置用 `--destination PATH`。
4. 新增類型需先以 `configure` 保存使用者確認的設定。一次選擇不新增永久 match 規則。
5. 重試原本文件工作，使用 hook 回報的實際路徑讀取、修改、建立連結及交接。

`--confirmed` 是執行者對既有使用者選擇的聲明，不是取得同意的方法。禁止在使用者尚未回答時自行帶入。路徑衝突應保留文件並詢問，不能歸類成「新增類型」解決。

## 支援範圍

Codex `apply_patch` 與 Claude `Write/Read/Edit` 可改写已辨識文件。shell 提供指引，不透明改寫任意腳本；外部編輯器、固定路徑生成器和所有工具的全面覆蓋未保證。
未納管的既有文件不自動搬移。平台／技能內部文件及 README 等入口不套用一般文件分類。

詳細設定、安裝及限制見 [references/configuration.md](references/configuration.md)。
