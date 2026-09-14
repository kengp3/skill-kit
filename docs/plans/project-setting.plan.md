# 執行計畫與驗收結果

使用者最新決定：skip claude code。本次交付與完成判定以 Codex 為範圍；Claude 轉接程式保留為未完成實測的選用功能，不再等待登入。

- [x] 1. 核心設定與路由：五種預設、自訂類型、路徑解析、選擇與安全邊界。
- [x] 2. Codex 整合：專案載入、參數改寫、建立／讀取／修改及防覆寫。
- [x] 3. 互動流程：未知、缺設定、多重匹配、缺名稱、確認後續作、新增類型及一次性位置。
- 第 4 項 Claude 整合：依使用者要求跳過，不宣稱驗收通過。
- [x] 5. 包裝與文件：可攜技能、隔離安裝、設定說明、啟用步驟與限制。
- [x] 6. 完成稽核：依更新後範圍逐項對照證據，獨立覆核通過。

## 完成條件稽核

| 規格完成條件 | 證據與結果 |
| --- | --- |
| 初始化、更新、自訂類型與五種預設 | 核心測試及新增 retrospective 真實互動通過。 |
| Codex 建立、讀取、修改與確認後續作 | 最新 runtime 與第三方技能流程通過，詳見以下證據。 |
| 衝突、越界、多重匹配、缺名稱／設定、設定改動、無關檔案 | 22 項測試涵蓋；Codex 防覆寫及互動流程另有實測。 |
| 可攜技能、validator、平台驗證與審查 | 可攜回放、validator、Codex 實測與獨立覆核通過。 |
| 支援範圍、啟用與限制文件 | SKILL.md 與 references/configuration.md 已包含，不宣稱全面攔截。 |

## 改名前的驗證證據

以下實測屬於 project-conventions 舊名稱版本；路徑與雜湊保留原值，不代表改名後的腳本。

未修改第三方 skill 的整合測試通過：agent-skills 0.6.9 planning-and-task-breakdown，SKILL.md SHA256 `ed0f90cc5951ddd4bcab7f871f64efec93a49af9279ef93bc470da77ad8da3f7`。模型讀取技能及根設定，先 resolve tasks/plan.md（missing_metadata）與 tasks/todo.md（unmatched），詢問後才保存選擇；產出 docs/plans/csv-summary.plan.md、docs/plans/csv-summary-tasks.plan.md，完成讀回及文字修改。磁碟確認原 paths 不存在、別名正確、skill checksum 不變，未實作範例 CLI。這是專案指令搭配共用 resolver 的協作案例；不宣稱所有第三方工具皆可攔截。

最新驗收：22 項測試與 compileall 通過（包含每種預設實際目的地、ADR 缺編號）。獨立代理覆核本輪防覆寫、別名鏈及啟用說明修正通過，未發現該範圍剩餘必修問題。

最新 Codex runtime 實測通過：release.plan.md 建立後導向 docs/plans/release.plan.md，讀取 draft、更新 verified、再次讀取；隨後刻意 Add File 到同一 canonical 位置，被拒絕且內容仍為 status: verified。來源不存在。測試 runtime 與工作區逐位元相同：conventions.py SHA256 b137f97241f04fb05b8265f09f21576fc74e24a6ba45fec1cf27edb600b7d632；hooks.py SHA256 3168f00fdd51c7970fccc7b4fc4e0226e0e3167596b05cd245cc43a70faa7c58。

- `python3 -m unittest discover -s tests -q`：22 項通過；`python3 -m compileall -q skills tests` 通過。
- skill-creator `quick_validate.py`：Skill is valid。PyYAML 僅用於臨時驗證環境，技能本身無第三方套件依賴。
- 可攜測試：技能複製到乾淨 Git 專案並安裝，移除來源副本後，runtime 仍可路由 portable.plan.md。證據目錄 `/private/var/folders/76/hd61cw513zbdlr0y7_h27dx80000gn/T/conventions-portable-x0uv0fb2`。
- Codex 實測目錄：`/private/var/folders/76/hd61cw513zbdlr0y7_h27dx80000gn/T/project-conventions-codex-inline-lva4j350`。正常 TUI 透過 /hooks 逐項信任 PreToolUse；實測未使用 inline 覆寫或信任繞過。
- 缺設定／一次性位置：briefing.md 回報 missing_config 並等待；模擬使用者確認 notes/briefing.md 後，建立、讀取、修改及再讀取成功，內容 one-time verified；當時 root JSON 仍不存在，未新增永久類型。
- 新增類型：retrospective.md 未匹配時先建議並等待；確認後新增類型、保留五種預設並產生 docs/retrospectives/sprint-one.md。
- 既有分類：investigation.md 未匹配時先建議 research，確認後建立並讀取 docs/research/investigation.research.md，沒有新增 match 規則。

## 實際限制

Claude 曾回傳 OAuth 401，本次依使用者要求不再驗收。SessionStart/SubagentStart 已提供指令注入，但未單獨做完整模型事件實測；Codex 實測依專案指令及 PreToolUse 完成。

shell 內部寫檔僅提供指引，無法透明改寫任意程式；不保證所有第三方固定路徑腳本或相對連結都能修正。受管文件重新命名尚未支援；既有文件不自動遷移。路由狀態存在不等於寫入成功。技能不檢查文件章節或內容範本。


## 2026-09-15 集合分發與改名

- 技能、設定檔與本地 runtime 目錄統一為 project-setting；內部解析器檔名 conventions.py 維持原用途。保留舊實測路徑，不宣稱舊雜湊適用新版。
- 根 README 加入技能清單、單一／全部安裝、逐專案啟用、新增技能規則與改名相容性說明；Plugin 研究改列替代方案。
- 22 項 unittest 通過；skill-creator quick_validate 通過（PyYAML 僅安裝於暫存驗證環境）。
- 使用 skills CLI 1.5.26，以本機來源實測 --list、指定 project-setting 與 --skill '*' 安裝到 Codex；清單只含新名稱，安裝的技能資源與來源一致，安裝本身未建立專案 JSON 或 Hook。
- 隔離專案執行 init 與兩次 Hook install；產生 project-setting.json 與 .project-setting/runtime，重複安裝沒有重複註冊。移走安裝的技能後，專案 runtime 仍可將 portable.plan.md 路由至 docs/plans/portable.plan.md。
- 本輪 Hook 驗證為腳本協定回放，未重跑 Codex 模型與信任操作。遠端 repository 尚未設定，GitHub 來源下載未驗證；舊名稱專案的自動遷移與完整 Hook 移除仍未實作。
- 互動安裝亦通過：選擇 Project 並確認後，實際檔案完整。因僅有一個技能，CLI 直接選取，尚未實測多技能選單。
- 暫存驗證目錄：/private/tmp/simple-skills-install.Q49fj7。

## 既有未納管文件誤擋修正

將既有來源的略過判斷移到 missing_metadata／ambiguous 之前；已登記別名與符合設定目的地的文件仍走受管流程。
新增 Hook 回歸測試，修正前重現缺名稱／多重匹配下更新與刪除的 4 個失敗情境，修正後 23 項測試通過；來源不存在時仍要求分類確認，既有防覆寫測試維持通過。
乾淨 Git 專案安裝後，以獨立程序回放 runtime 的更新／刪除事件均原樣放行，Hook 未更動原文件；Python 語法檢查通過。本輪未重跑 Codex 模型與信任流程。

## 2026-09-15 完整流程驗證（修正後）

本輪以 Codex CLI 0.154.0 在 `/private/tmp/project-setting-qa.Yt1lZs` 執行真實模型與工具操作。透過正常專案信任及 `/hooks` 介面信任新加入的 3 個 Hook，確認 PreToolUse active=1；未使用 hook trust bypass。首次啟動因外層沙箱無法寫入 Codex 本機資料庫失敗，取得該次啟動權限後繼續，沒有修復或重設資料庫。

| 檢查 | 證據與結果 |
| --- | --- |
| 技能安裝 | skills CLI 1.5.26 從本機儲存庫以 `--skill '*' --agent codex --yes` 安裝，找到 project-setting；隨後執行 init 與 Hook install。 |
| 自動測試與格式 | 23 項 unittest 通過；skill-creator quick_validate 通過。 |
| 既有缺名稱文件 | 真實 apply_patch 更新 root plan.md，讀回 updated；再刪除，磁碟確認不存在。 |
| 新文件路由 | 真實 Add File 的來源為 release.plan.md，Hook 回報 docs/plans/release.plan.md；讀回 draft，再更新並讀回 verified，root 來源不存在。 |
| 防覆寫 | 對同一目的地刻意執行一次 Add File，工具回報 PreToolUse 拒絕；原內容仍為 status: verified。 |
| 未知文件互動 | 模型先建議 research 並等待；測試者下一輪確認後，以 choose 保存 briefing.md 的選擇，再建立並讀回 docs/research/briefing.research.md；未添加永久匹配規則。 |
| 多重匹配既有文件 | 測試者在暫存設定加入 spec 對 plan.md 的匹配，重建既有 plan.md；真實更新讀回 ambiguous updated，刪除後確認不存在。 |
| 多重匹配新文件 | 隨後唯一一次 Add File: plan.md 被拒絕，reason=ambiguous；模型詢問分類並停止，磁碟無該檔且路由表沒有未確認選擇。 |
| 腳本一致性 | 實測 runtime 與目前來源逐位元相同，雜湊如下。 |

- conventions.py SHA256：`61cd98ad21df3830c1de9b9317d7e30337140075015587f06783d73736711d01`
- hooks.py SHA256：`6298c872b2d887b30dadc80f064746e5ecbd79463a09d8ce8f58f0f3175e07f3`
- 原始工具紀錄：`/Users/kengp3/.codex/sessions/2026/09/15/rollout-2026-09-15T02-00-14-01a0a113-a6aa-7772-a15d-6c3048ade6b2.jsonl`。

結論：本次修正的兩個情境與安裝→啟用→建立／讀取／更新／刪除→拒絕／確認後續作流程通過，未發現新的失敗。缺設定、五種預設、自訂類型、路徑邊界等其餘情境由自動測試涵蓋；本輪未將每個自動測試情境逐一重跑為模型操作。SessionStart／SubagentStart 顯示啟用，但未獨立驗證各自的模型行為。GitHub 遠端下載、多技能選單、Windows、Claude 與舊版自動遷移不在本次通過宣告內。
