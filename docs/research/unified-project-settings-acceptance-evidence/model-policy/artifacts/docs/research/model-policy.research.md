# 模型政策判讀研究

本文件由主責模型直接閱讀 cases.json、project-setting.md 與已安裝 task-harness 規則後判讀，未執行解析／判斷 helper，未派工或探測 provider。

**cases.json 的 observed_unavailable、observed_effort_unsupported（統稱 observed_*）全部是明列的測試輸入，不是本次實際查到的 provider 事件。** host_default_effort 同樣只是案例提供的值。下表的選擇與回退均為規則推導；沒有列入失敗輸入，不代表已證明可用。所有案例的實際執行模型與強度皆不可觀測（null），沒有成功啟動或實際生效的結論。

## 依據與解讀範圍

- 輸入：[cases.json](../../cases.json)、[project-setting.md](../../project-setting.md)。唯一合約：[model-policy.task-contract.md](../plans/model-policy.task-contract.md)。
- 已安裝版本：`kengp3-harness/0.3.0/skills/task-harness/`；主規則 `SKILL.md`，以及 `references/model-selection.md` 的「每次派工前」「階段與主責模型」「候選與推理強度」「不可用、結果不明與回退」，並參照 `references/project-settings.md`、`references/task-contract.md`。
- 優先序：本次明確指定 > 個別任務覆寫 > 完整角色名稱 > 完整階段名稱 > 專案預設 > 主責原生繼承。current 在本組案例中代表本次明確指定，task 代表本任務覆寫；不是主責實際模型證據。
- candidates 表示該案已給定的待判讀候選清單；案例未交代其優先序來源，不擅自標成角色、任務或使用者指定。
- 專案預設為 gpt-6.1-sol／low；analyst 角色為 gpt-6.1-sol／high；自訂「研究」階段為 gpt-6-sol／medium。inherit 案明確模擬沒有專案預設，其餘案例沿用實際設定。

## 逐案判讀

表內「送入／待驗證」僅表示依規則選到該候選；不代表本次有發出請求。前五案未提供失敗事件，因此沒有已發生的回退；其回退欄補列條件路徑。

| case | 首選來源 | 首選模型 | 首選強度 | 依序回退結果及理由 |
| --- | --- | --- | --- | --- |
| user | 本次明確指定（current） | gpt-6-sol | low | 優先於 task 的 gpt-6.1-sol／medium、analyst 與研究設定。未給失敗輸入，停在首選待驗證。若此清單耗盡，末段專案預設為 gpt-6.1-sol／low；不串入 task、角色或階段清單。 |
| task | 個別任務覆寫（task） | gpt-6-sol | low | current 未設定，故採 task；不直接採角色或階段。未給失敗輸入，停在首選待驗證；清單耗盡才進專案預設 gpt-6.1-sol／low。 |
| role | 角色 model.role.analyst | gpt-6.1-sol | high | current 與 task 皆未設定，完整角色名稱命中。未給失敗輸入，停在首選待驗證；若模型不可用，末段專案預設的同識別字須跳過，即使其強度為 low 也不得另試。若僅 high 不支援且無禁止修正，可先採該模型宿主預設強度（值未知），仍無法啟動才進末段回退。 |
| stage | 階段 model.stage.研究 | gpt-6-sol | medium | 無 current、task、role，依完整自訂階段名稱命中，無須改成其他階段。未給失敗輸入，停在首選待驗證；清單耗盡才進專案預設 gpt-6.1-sol／low。 |
| project | 專案 model.default | gpt-6.1-sol | low | 未設定階段名稱不命中任何列，較高來源皆無設定。未給失敗輸入，停在首選待驗證；若清單耗盡，不重新進入自身，也不擅加主責模型。 |
| fallback | 案例提供的 candidates（來源層級未指定） | not-an-available-model | high | ① 測試輸入指首選不可用，移至 gpt-6-sol／none。② 測試輸入指 none 不支援；保留 gpt-6-sol，受控修正為案例提供的宿主預設 medium。③ 此案無後續失敗輸入，規則結果為 gpt-6-sol／medium 待驗證，不宣稱可用或已啟動。若修正後仍不能啟動，才走末段專案預設 gpt-6.1-sol／low。 |
| default | 案例提供的 candidates（來源層級未指定） | not-an-available-model | 未指定，使用該模型宿主預設（值未知） | ① 測試輸入指首選不可用，清單耗盡。② 即使未明列 default，也自動執行一次末段回退，選專案預設 gpt-6.1-sol／low 待驗證。其可用性未知；不以主責強度補入首選的空白強度。 |
| dedup | 案例提供的 candidates（來源層級未指定） | gpt-6-sol | low | ① 以模型識別字去重，保留第一次的 low。② 測試輸入指 gpt-6-sol 不可用，後面的 gpt-6-sol／high 跳過，不另試。③ 最後 default 解決一次末段回退，選專案預設 gpt-6.1-sol／low 待驗證；不因明列 default 再增加一次回退。 |
| strict | 案例提供的 candidates（來源層級未指定） | gpt-6-sol | none（不可變更） | ① 測試輸入指 none 不支援。② 使用者說「這個模型的強度不可變更」，故不得把 gpt-6-sol 改為宿主預設；維持原要求並離開此候選。③ 清單耗盡進入末段專案預設 gpt-6.1-sol／low 待驗證。限制針對 gpt-6-sol，不擴張成所有模型都只能 none。若預設也不可用則保留缺口，不擅加主責。 |
| inherit | 沿用主責（前五項皆未設定的案例情境） | 原生繼承，識別字不可觀測（null） | 一起原生繼承，值不可觀測（null） | project_defaults_present=false，且 current、task、role、stage 皆空，直接原生繼承，並非先套實際專案預設再回退。不臆造模型、強度或額外候選。此案沒有已試模型可造成去重歧義；若日後是耗盡清單後繼承且無法排除重複，須先查原生設定，查不明保留缺口。 |
| new-task | 新任務的專案 model.default | gpt-6.1-sol | low | ① new_task=true，previous_task_override 的 gpt-6-sol／high 不承接。② 本案沒有新的 current、task、role、stage，因此採專案預設，而不是沿用前任務覆寫。③ 未給失敗輸入，停在首選待驗證；若預設清單耗盡，不遞迴自身或擅加主責。 |

## 共通邊界與驗收

首選清單的同模型強度修正，必須以原要求未成功啟動為前提；真實啟動結果未知時，先對帳原 handle、宿主結果與產物，不能另派。這裡沒有啟動操作，案例輸入僅用於演繹分支，不構成該前提的真實 provider 證據。

末段預設回退只執行一次，沿用每個候選自己的強度、跳過已試識別字；專案預設失敗不額外加入主責。候選耗盡時，真實執行工作應保持未完成並取得必要決定。本任務驗收的是判讀，不要求各案例成功啟動，因此未實測 provider 不阻礙完成此研究。

已由主責逐案核對全部 11 個 ID、優先序、去重、強度修正、strict 限制範圍、隱式／顯式 default、原生繼承與新任務不承接覆寫。沒有以候選模型或案例 observed_* 作為主責實際模型證據；主責維持對話原生設定，未指定的實際模型與強度保持 null。此驗收是模型直接判讀與文件比對，不是 helper、provider 或獨立 agent 審查結果。
