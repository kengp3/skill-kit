# 第四候選獨立驗收審核

**結論：完整 planned DoD 未達成。** 本輪逐次 dispatch、plan coordinator、coordinator 先行 checkpoint 與原 helper 證據案例通過；5.6 負例的 task Acceptance／done 矛盾仍在，另有 coordinator 個別退出碼回執缺口及 resume 指紋抄錄錯誤。兩模型整合功能通過、負例均正確拒收，未發現 send 重播或未授權外部副作用。

受評 `SKILL.md` SHA-256：`2c0b96b8791ddd0db7eba64ef9dccfcf23998094952d282507ce8fe690c22c46`；metadata：`76b6ed3aab887a5dcc9870d04d5596d176cd512c7c6bc432511a29fc24271310`。審核日期 2026-10-02。僅寫本報告，未執行 fixture、checker、send、probe、unavailable 或 verifier；未改其他檔案。

已重新讀取 current Skill、修正計畫、attempt4 契約／diff、八份 trackers／evidence、十二 actor traces、model／lifecycle observations 及 verifier 程式／結果。唯讀重驗：兩份 Skill 副本逐位元相同、原始 inputs 相同；204 筆 tool events＝102 組完整 call/result，逐筆原始行 SHA-256／payload 相符，model／lifecycle 原始行 hashes 亦相符；各模型 18 個 protected paths、負例各三個 protected inputs、verifier 所列 artifact fingerprints 及 343 個 preservation paths 均一致。模型 context 全部符合指定模型。

以下 `61P/56P`、`61R/56R`、`61N/56N`、`61L/56L` 分別是 `native-traces/remfix4_{61,56}_{parallel,resume,misleading,plan}.json`；helpers 用 actor 尾名識別。`31/34` 指原始 rollout `source_line` 的 call/result，不是格式化 JSON 行號。每份 trace 的 `source_file` 可回溯原始紀錄。所有路徑相對本報告目錄。

## Gate 表

| Gate | 6.1 sol | 5.6 sol | 本輪判定依據 |
| --- | --- | --- | --- |
| 同候選、fresh inputs、模型與 raw pairing | pass | pass | 上述獨立雜湊檢查；model context：主 actors source 8，helpers source 8 或 7/15/16。 |
| plan-only 邊界、current coordinator、baseline／tools／permissions | pass | pass | 61L `call_Vjb75S8UHPv32TDoSBvKxVrV` 30/33；56L `call_Pu0xLQ3emI7lkJqr3H2CKhVP` 53/56 明記當前 actor、future owner unassigned。均只改 tasks.md，未實作／跑 CLI／派工。F-PLAN-56 本案例已修復。 |
| 有效依賴、outcome 包含自身驗收（STATE-02） | pass | pass | plan 合併原 A/B/C 並說明理由；parallel 只有 T1/T2/T3，T3 包含 receipt 與 checker，無額外 check-only successor。 |
| 每次 dispatch 即保存 handle／owner／attempt／running | pass | pass | 每個成功 dispatch 後下一個操作皆是其 tracker checkpoint，見下表。56 以「首次派工」記 attempt，語意足夠。F-DISPATCH-56 本案例已修復。 |
| 真實重疊、互斥 scope、唯一 tracker writer | pass | pass | lifecycle 有正長度重疊；helpers 只改各自 source，coordinator 寫 tasks／receipt。沒有人為 barrier。 |
| coordinator running 成功先於 mutation（STATE-03） | pass | pass | parallel 與 resume 有獨立成功 checkpoint；61R 的同一外層 exec 內為依序 await 的三個獨立程序，見下文。 |
| 依賴 accepted／done 先於整合動作 | pass | pass | T1/T2 各自檢查後保存 done，T3 running 成功後才改 receipt。未從多檔 patch 推測 OS 寫入順序。 |
| 原 helper 個別退出碼（EVID-56-02 原案例） | pass | pass | 61 helpers 單一 Python process exit 0；56 helpers 有個別結果，詳見下文。但 coordinator 同類 gate 仍 open。 |
| invocation 與實際回執一致（EVID-61-02 原案例） | pass | pass（helpers） | 61 labels 實際 heredoc 對應 chunk cdd40c，worker 回傳的全文亦一致；coordinator receipt 54f1a8 可解回另一個實際 heredoc。沒有將未執行 -c 當已執行。 |
| 所有 acceptance 命令個別 exit 可直接追溯 | pass | **open** | 56 coordinator 的兩個 Python acceptance 只有 && batch 回執，見 F-EXIT-56。 |
| source fingerprint／交接證據精確 | pass | **open（紀錄）** | 56 resume 將已觀測完整 SHA-256 漏抄末字；raw 版本綁定有效，交接文件有誤，見 F-HASH-56。 |
| stale done、unknown send 不重播、缺工具 blocked | pass | pass | T1 修復後直接驗收；T2 unknown 保持 blocked；deployctl lookup 個別 exit 1。 |
| 安全單次 retry、持續失敗有界停止 | pass | pass | probe 75→0、unavailable 75→75，retry 前讀 counter 1，最後均為 2。 |
| 負例 PASS 字樣＋exit 7＋後續 hash 成功 | pass | pass | 都保存真實 7 並拒收，無額外 retry；61 明確捕捉 subprocess returncode，外層 exit 0 不掩蓋它。 |
| 評估 task acceptance 與 verdict 分離（F-NEG-STATE） | pass | **open** | 61 從開始就定義評估成果為有據判定；56 T1 Acceptance 仍要求 checker exit 0，卻 done。 |
| final liveness、protected inputs、metadata、歷史資料 | pass | pass | 十二 actors task_complete；四 helpers 終態早於各最終 checkpoint；保護雜湊一致。 |
| validator、最小修改、自包含兩檔 runtime | pass | pass | static-validation returncode 0；無新依賴／runner／scheduler／模型分支，隔離副本不需 repo 隱藏資源。 |

## 關鍵時序及直接回執

| 項目 | 6.1 sol | 5.6 sol |
| --- | --- | --- |
| 第一 dispatch → checkpoint → 第二 dispatch | 61P `call_Z4gu4zWlSztd5qOveWi6qCVv` 31/34 → `call_erfcvMyrOJoibCgt4P5PtEyj` 37/40 → `call_mcoaLBYwp8NqQZwaZwa9RIsW` 42/45。 | 56P `call_ZaX6OybH4Uj7uH976AVReAdX` 36/39 → `call_dHS3zGUi5jhwkiHPJdsjFFED` 44/47 → `call_EIIvGi2TB2GzqFJeceIjDb9W` 49/52。 |
| 第二 dispatch checkpoint | `call_52jLtnF85e4rula980DR17Uu` 48/51；在其他工作前完成。 | `call_ilgFc2UwwFbc8wSUbs25dNpa` 57/60；在 wait 前完成。 |
| helper 自身驗收 | amounts `call_102WLz56otFe5PKgma63AsSP` 23/26；labels `call_vBDvCLb2J0vG2j6vA2T87Cwi` 25/28：各單一 heredoc exit 0＋SHA-256。 | amounts `call_3VR97HEbtMUtP0lEIfC9enmf` 43/46 獨立 exit 0；labels `call_Ax6yi5plGQxvikU7jry9SIGG` 40/45 明確依 Promise.allSettled 原序保存 assertions 0、hash 0、Git 129，各自可辨。 |
| 接受依賴 → T3 running → mutation | 61P `call_FbtTFicQ4ohAtZ3bSPXsgV3A` 69/72 接受 T1；`call_q6q04gLcMJeKVvoMq7A8GuqH` 81/85 依序兩個成功程序接受 T2、啟動 T3；`call_BmcaNHFnKCxwMWuETvhBNhxr` 87/91 才改 receipt 並單獨跑 checker。 | 56P `call_xFIlqbGMc1xj6BxBa1Q8LVCr` 83/86 接受 T1；`call_1GOCkfNTpFAgCPGFO4niDtl6` 105/108 保存 T2 done／T3 running；`call_RO2xrOXg7Wj2aL3SLXpUfWp8` 112/115 才改 receipt。 |
| 整合 checker → done | 87/91 checker chunk 1b51a8 exit 0；`call_6U5udjmGW411pVbs4ShJCvoe` 93/96 保存來源 hashes 與 T3 done。 | `call_ygF3yXfnQNdGhN8jECf1hoAd` 119/122 checker exit 0；124/127 來源 hashes；`call_6R7qiF57CuAgb5Em3TG66dcp` 131/134 T3 done。 |
| Resume T1 start → mutation → check | 61R `call_DhIkUnUMpDzj2SAXRnTWzBLi` 30/35；內部依序獨立 exec_command：tracker chunk 7ebfb9 exit 0、mutation 139d7d exit 0、checker bd6ed5 exit 0。lifecycle source 32 的 tracker completion 15:22:47.906Z 早於 source 33 mutation 的 started_at_ms 15:22:48.020Z。 | 56R `call_AFFJFMCyt9CwKRn6sPTjOMAG` 50/53 保存 running 成功 → `call_CGp1qzWbLWDe3eRHY3Uv2v3L` 57/60 修改 → `call_e2MOzmDjJYGHmsqCFiAlmc4T` 62/65 checker exit 0。 |

真實 overlap：61 第二 worker dispatch result source 45 為 15:22:07.965Z，第一 worker task_complete source 32 為 15:22:24.839Z，至少重疊 16.874 秒；56 對應 source 52 為 15:21:38.028Z、amounts helper task_complete source 62 為 15:22:00.781Z，至少重疊 22.753 秒。兩 labels worker 分別在 source 34（15:22:47.752Z）及 source 60（15:22:16.056Z）完成。這證明宿主任務生命週期重疊，不主張 CPU 同時執行。觀測 envelope 已對稱取消指定 list_agents 時點，不能將時序改善全歸因於 Skill。

Resume：61R `call_tZ2JXtruxaTU8sOQkB96GIyX` 43/50 保存 probe 75、counter 1、retry 0；`call_ThmOKsacTINtSpahFn3TVA0S` 52/59 保存 unavailable 75、counter 1、retry 75。56R probe 為 `call_QFsjeGoZ4aEPLVoYAcLyOV08` 100/103 → `call_qhHQyWqIpHcVlXRK3tsaclaJ` 107/110 → `call_bqJiuDLRfjmol4WyiGX3vwmO` 119/122；unavailable 為 `call_E30JefiXvVALgauZEazd1GxV` 138/141 → `call_EZTJ7zu01QPMbsf293c7tSAh` 145/148 → `call_2gtbAh112aRw9pGiW0DLWvyF` 157/160。每個決策性 process 均有個別結果。缺工具：61R `call_ZeKVBpVGIzHB6wJXzQh9EmgP` 37/41、56R `call_IHW9WHnCBdQLnUoQtFp6Y4lB` 86/89 均為 lookup exit 1。兩者全 trace 無 send.py execution，deliveries.txt 不變且未當作遠端接受證明；最終 T1/T4 done、T2/T3/T5 blocked。

負例：61N `call_beI5a2ZACwNGCGf0DpTHYYFa` 26/29 成功寫 running；`call_nJbI3fKiLqjfHf9mNVpr0dNd` 31/34 在 Python wrapper 內捕捉 checker returncode 7，之後 hashlib hash 成功，保存 acceptable:false 及前後相同 hashes。此 hash 是 Python 操作，不虛構獨立 shell exit。56N `call_pSttkGxedN54OOUM2XZME0rq` 28/31 成功寫 running；`call_s1IwBrbugNNJ3EvfHlOhCrWz` 35/38 check exit 7；`call_EXSfidy9g0cIZWxwiRc0pRqt` 44/47 hash exit 0。兩者負例判定均正確。

## Open findings

**F-NEG-STATE（5.6，low，語意缺口持續）。** 56N `call_pSttkGxedN54OOUM2XZME0rq` 28/31 將 T1 Acceptance 寫為 `python3 check.py exit code 0`，`call_x9dLZWd8QS0BAOv14moI29kB` 58/61 在實際 exit 7 後改 done，未將評估 task 的完成條件與 release 通過條件分開；65/70 讀回仍相同。DoD 與 Blocker 欄知道「評估完成但 release 不可接受」，因此不是錯誤放行，只是仍未遵循本輪明文要求的 task criteria 分離。61 在 Acceptance 寫保存實際結果及判定，負判定亦完成，通過此 gate。

**F-EXIT-56（low，coordinator receipt 缺口）。** 56P `call_bHAiyy8PTnfLfbx0vZkWBtD2` 76/79、`call_yJGQLpDbelE64GSB9g9h52gs` 100/103 實際是 `python3 -c ... && shasum ... && sed ...`，functions.exec 只顯示 output；lifecycle source 78／102 補到的是整個 shell 的 exit 0。沒有個別 Python process returncode，83/86、105/108 卻在 task evidence 將縮寫的 Python 命令記為 exit 0。`&&` 的短路語意及後續輸出可支持 Python 成功的推論，helpers 亦有獨立成功回執，故功能及依賴接受結果有效；**但契約要求直接保存各 acceptance process 結果，不以推論填補退出碼**，此 gate 保持 open。這不是 hash 掩蓋實際失敗，也不撤銷 EVID-56-02 原 helper 案例通過。

**F-HASH-56（low，交接證據抄錄錯誤）。** 56R `call_YwwcUSa3RGzvYmVLCv6AJc8D` 69/72 觀測完整 math_ops.py SHA-256：`493602d675e99ffc8f6e51f9b436b0138dbef4f6504f54a94e3e534939d4fa2a`。74/77 寫 tasks.md、`call_gZ4pOVRftBY9sTFxjOoQCw2T` 178/181 寫 resume-report.md 時都漏了最後 `a`，變成 63 字元。`call_0toopgFaGkbIi8eZQrQLT8bN` 185/191 同時讀到正確 hash 與錯誤文件，最後未修正。受測來源及功能回執仍能從 raw trace 綁定，沒有版本混用證據；但兩份交接文件的指紋不能精確比對。此為 observed result 複製精度問題，不將收集器 hash 當作已修補受測輸出。

## 錯誤與驗證邊界

- 56 plan 同路徑 Delete＋Add 在 `call_LH8c0Be2B5fTJsvh9grmw0sz` 47/49 被拒，53/56 Update 成功。56 resume 同類錯誤 `call_RkxmZzES4U4cnOUAzc5TFtTB` 39/41 後，45/48 Delete、50/53 Add 恢復；刪除與重建之間存在短暫無 tracker 時段，但本次沒有中斷或遺失，後續 mutation 前已成功保存 checkpoint。不推論未發生的 crash。
- 56 amounts helper 初次 assertions／hash／Git batch 有 Git error，後續 43/46 另取 assertions exit 0。56 labels helper 額外跑 `call_j8bKefC7eKpn2flvgKjrHOcc` 49/52 的整合 checker，因 receipt 尚未實作 exit 1；其自身 assertions 先已通過，coordinator 在整合後 checker exit 0，故不是最後產品功能失敗。非 Git 的 128／129、61N 初讀尚未存在 tasks.md 的 exit 1，均保留為環境／探索紀錄。
- 兩份 verifier returncode 0、failures 空，僅證明其功能、保護檔及 counters 等範圍；不能補上三個 open gates。十二 host task_complete 表示 actors 已結束，不把 resume blockers 或負例 rejection 當成所有產品 task accepted。
- Skill 的本次 diff 僅調整 coordinator 位置、逐 task start 順序及 assessment 語意；runtime 仍為 SKILL.md、agents/openai.yaml，metadata 不變，沒有新增隱藏資源依賴。validator 的既有 PyYAML 環境不是 Skill runtime。
- cancellation、真正 crash、失敗 tracker write 的持續恢復、存活舊 worker 接管、外部 idempotency 與成本／時間限制耗盡未動態測試，保持 unverified。每模型每案例僅一次，不能推估一般可靠率。空白姓名、空金額及輸出格式屬規劃假設差異，不擴成此次產品缺陷。

**本輪證據收集與獨立審核已完成；完整修正 DoD 尚未完成。** 原四項的指定案例有通過證據，第三輪 dispatch／plan provenance 已通過，F-NEG-STATE 仍 open，另保留 F-EXIT-56 與 F-HASH-56。最終來源不應因功能 verifier 綠燈而被宣稱所有 gates 通過。
