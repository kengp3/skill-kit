# 統一設定改版：0.3.0 封裝與隔離安裝驗證

日期：2026-10-25。T07 的封裝、安裝／升級載入與指南同步已完成；本報告不是 A–G 整體任務行為驗收或正常 hook 信任通過證明。

## 變更與測試邊界

- 來源版本改為 0.3.0；發行包不再包含或要求舊 Python hook handler。保留四個 skills 及其新設定／移轉／模型參照與 assets，技能 scripts 仍為選配。
- SessionStart／UserPromptSubmit 使用 shell 內建 echo 輸出固定 ASCII 提醒；不解析事件、不讀寫專案，不自動啟用任務。Stop 固定輸出合法空物件 `{}`，是被動回應，沒有條件式阻擋或一次性補救保證。
- 使用者本地安裝可直接複製技能目錄；維護者建包 Python 與第三方 Skills CLI 的需求不轉成日常前提。原有 root marketplace 及舊候選保持原狀。
- README 與既有 HTML 手冊同步統一設定、三項移轉刪檔門檻、模型清單、回退、四時點檢查、失效接手與停止邊界。

## 預期 → 觀察 → 證據

| 查核 | 實際觀察 | 證據 |
| --- | --- | --- |
| 紅測試 | 在尚未修改 production hooks 時，空 PATH 回放三事件均 exit 127／找不到 python3，且包仍含舊 handler；新封裝測試失敗 | 本輪工具執行紀錄；測試為實際封裝 CLI 與註冊命令邊界，不是模擬 handler |
| 綠測試 | 改動後 8 項封裝測試通過；空 PATH 可執行固定命令，重複 Stop 均為空物件，專案檔案集合／內容未變 | tests/test_harness_package.py；完整套件測試也包含此組 |
| 完整維護測試 | 111 項，略過 1 項，通過；受限沙箱的 /bin/ps 錯誤以同一組測試在允許程序查核環境重跑釐清 | [完整測試輸出](unified-project-settings-package-evidence/full-tests.log) |
| 新候選 | 建包與 manifest verifier 成功，不覆寫目的地 | [build](unified-project-settings-package-evidence/build-new.json)、[verify](unified-project-settings-package-evidence/verify-new.json)、[manifest](unified-project-settings-package-evidence/candidate-manifest.json) |
| 舊版基準 | 從凍結提交 c7c769b 匯出到測試目錄，建立並原生安裝 0.2.1；讀回四 skills／三 hooks | [舊安裝](unified-project-settings-package-evidence/install-old.json)、[舊載入](unified-project-settings-package-evidence/loaded-old-rpc.json) |
| 升級 0.3.0 | 測試 catalog 指向新版本後，經 native plugin add 升級；新程序實際從 0.3.0 cache 載入四 skills／三個靜態 hooks，舊 handler 不存在，安裝內容驗證通過 | [升級](unified-project-settings-package-evidence/upgrade-new.json)、[讀回](unified-project-settings-package-evidence/loaded-upgraded-rpc.json)、[內容驗證](unified-project-settings-package-evidence/loaded-upgraded-verify-installed.json) |
| 全新 0.3.0 | 另一個全新 state 從同一測試 catalog 安裝，載入來源與內容驗證通過，沒有先裝舊版 | [新安裝](unified-project-settings-package-evidence/fresh-install-new.json)、[讀回](unified-project-settings-package-evidence/loaded-fresh-rpc.json)、[內容驗證](unified-project-settings-package-evidence/loaded-fresh-verify-installed.json) |
| 隔離 | state、catalog、project、舊來源匯出與新候選均位於自有暫存根；未複製 auth，明確移除認證環境變數。正常 config.toml／auth.json 前後 SHA 相同 | [摘要](unified-project-settings-package-evidence/summary.json)、[開發 probe](unified-project-settings-package-evidence/native-install-probe.py) |
| 手冊 | 保留既有 CSS、導覽與複製／列印互動；15 章、ID／本地連結／範例有效，內嵌 JS 語法檢查通過。桌面與窄視窗 headless render 正常初始化 | [render 結果](unified-project-settings-package-evidence/handbook-render.json)、[桌面](unified-project-settings-package-evidence/desktop.png)、[窄視窗](unified-project-settings-package-evidence/mobile.png) |

## 判定限制

- 原生安裝／升級和載入已直接觀測，但三個 hooks 的 trustStatus 仍為 untrusted。本輪沒有模型回合或真實 hook 觸發；T08 須取得任務行為證據。載入不是信任、執行或成果通過。
- 空 PATH 的 POSIX replay 證明 shipped 命令不需要外部 runtime，不能單獨證明模型遵循。Windows 命令依內建 cmd echo 提供，原生 Windows 測試仍略過。
- 窄視窗截圖採 Chrome 的 window-size 請求，未另以行動裝置 emulation 驗證內部 viewport；不宣稱已完成手機互動驗收。桌面首屏已人工檢視，完整導覽／複製互動未逐項點擊。
- 全域保留檢查直接比對 config/auth，並以全部 CLI／RPC 的隔離 state 與 cache 路徑佐證；沒有重新掃描所有全域檔案或 OS keychain。
- 本報告的候選指紋支持此次來源快照；後續整合若變更技能內容，應重新建包與核對，不能把本指紋當作未來候選。

## 整合後候選

同步整合分支的 glossary 與模型規則補充後，另建 `/private/tmp/unified-t07-integrated-0.3.0` 並通過內容 verifier，未覆寫上述已安裝候選。此候選供 T08 進行最終整合行為驗收；本報告的 native 讀回紀錄仍明確屬於前述原始候選快照，不冒充整合後候選已載入。
