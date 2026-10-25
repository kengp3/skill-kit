# 統一設定改版：獨立審查與修正

日期：2026-10-25。兩個獨立唯讀 agent 分別執行 Standards 與 Spec 審查。審查基準為 `c7c769b16842a0590820ccf56d1f42becd07571e`；初輪整合版本為 `dda6cb213f0c37dd4b35af857745fdd46a4e0596`。

依據：[實作規格](../specs/unified-project-settings.spec.md)、[ADR](../adr/0001-unified-project-settings.adr.md)與使用者已確認的 T01–T08 工作圖。本報告記錄來源審查，不取代真實 agent 或宿主能力驗收。

## 結果

- Standards 初輪及修正增量複查：未發現可成立的 actionable finding。涵蓋封裝器、hook 定義、公開封裝邊界測試、技能與設定／模型／移轉規則，以及 README／HTML 手冊。
- Spec：確認三項 P2，全部修正並由原 Spec reviewer 複查解除；沒有以模型接手為理由免除標準接入材料。
- 未提交的 `.codex/config.toml` 為工作開始前已有修改，未納入審查、提交或改寫。

| Finding | 影響 | 修正與複查 |
| --- | --- | --- |
| 純複製 skills 安裝沒有 harness hooks 接線材料 | 使用者無法僅依已安裝技能完成標準接入，只能另找來源或自行重建 | `03071a0c3a00856e9c70a9ccb1a11461e29a911a` 將唯一 hooks 範本放入 task-harness assets，封裝器從同一資源產生 plugin hooks；provider 提供合併、跨來源去重、信任與接手規則，指南連結同步。來源複查解除 |
| 入口 metadata 仍宣稱必要 hooks／有界補救 | 被動 Stop 與模型接手的實作會被入口文字誤述成舊控制能力 | 同一修正更新 short_description／default_prompt，不再宣稱被動 `{}` 提供條件續作。來源複查解除 |
| handler 去重未明定 matcher／有效事件範圍 | 既有 startup 限定群組可能被誤當成涵蓋 resume／compact 的標準定義 | `4df858de8226c101c288cf2bb1b6ecf70fac1d00` 明定等效必須包含實際事件涵蓋，受限或未知範圍保留並回報，不自動擴大 matcher 或加入重疊副本。原 reviewer 複查解除 |

另同步澄清 review snapshot helper 為選配；可使用宿主既有檔案／版本證據，無法核對的值維持未知，沒有降低證據要求。

## 審查與測試證據

1. 初輪 Standards／Spec 各自固定 `c7c769b...dda6cb2`，未修改來源。Standards 直接執行原八項封裝測試通過；Spec 依規格與關聯來源確認前兩項問題。
2. 修正的公開封裝測試先在缺少 copied-skill hooks asset 時失敗，再驗證「複製技能可取得範本、plugin 使用同一內容、空 PATH 可執行、檔案不被 handler 改寫」；封裝測試增為九項。
3. Standards 增量複查範圍為 `dda6cb2...8052115b52e521067f28daeec2d1214265913349`，直接執行九項封裝測試通過；Spec 在 `03071a0` 解除前兩項，再於 `03071a0...4df858d` 解除 matcher 問題。
4. [修改前完整測試](unified-project-settings-review-evidence/baseline-tests.log)：111 項，略過 1 項，其餘通過。最初在沙箱內因 `/bin/ps` 被禁止而失敗；本基準為相同測試在允許該系統能力後的真實結果，不將環境錯誤當成產品回歸。
5. [修正後完整測試](unified-project-settings-review-evidence/fixed-tests.log)：112 項，略過原生 Windows 1 項，其餘通過。最後 matcher 修正僅改 provider 文字，未重跑整個 suite；已讀回並核對本地連結與 diff。

上述測試是維護者檢查，涵蓋歷史 helper 與新封裝邊界，不代表所有舊 fixture 都是本版核心能力。真實安裝、模型與產物驗收需另依 A–G 對帳。

## 範圍限制

正常 hook 信任、原生 Windows、指定模型／強度的帳號可用性及主責手動模型切換等能力，不能由本次來源審查推定通過。靜態上下文、被動 Stop 與模型主動檢查的界線維持原規格；沒有新增必要 runtime、外部 dispatcher 或機械完成保證。

本報告的通過意義為「已確認來源問題完成修正且複查無剩餘 actionable finding」，不是所有宿主或任意任務都已驗收。
