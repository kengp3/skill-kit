# 個人 Coding Harness 首版交付與三組 Smoke 報告

日期：2026-10-24（Asia/Taipei）
範圍：本機 Codex 內附 CLI／App Server 原生引擎；首個真實 bug 的流程 smoke。Desktop 主視窗 Stop 尚未通過。

首版可進行受控 CLI 試用：完整套件、專案啟停／回退、原生證據取回及本輪必要控制已有直接證據，三組各一次 trial 已完成。**尚未證明新版能減少人工投入，也不能以這輪結果判斷能力優劣。** 主指標人工 active time 缺值；配置、答案隔離與樣本數不支援此類結論。

## 本次交付

- `skills/task-harness` 改為精簡的 coding 流程：驗收依據、風險驗證、單一 owner、有進展的修復、結果不明先核對、最終整合與證據。按需連接 define-task／ai-code-review，不固定增加 tracker 或角色。
- 共用來源維持在 repo；Codex 套件含四個 skills 與完整依賴，版本 0.1.0、19 個 runtime files。`scripts/package_harness.py` 建包／核對，目的地不得已存在；發佈內容排除研究、grader 與答案。
- 原生 marketplace 與專案 opt-in 支援載入、停用、更新及回退。本 repo 保留開發啟用；沒有把候選設為全域強制啟用。
- 沒有新增強制 hook。文件提醒仍屬 advisory；本輪寫入、網路、取消與證據能力重用宿主，依實際路徑驗證。控制不足先停止相依操作。
- 保留固定 B／C 套件、48 個共同初始檔案、產品 patches、grader 版本、完整原生 RPC 與來源指紋，供後續按影響回歸。一次性評測 driver 是研究資產，沒有納入 runtime 或冒稱通用 runner。

目前0.164的啟用4個技能、停用0個、0.1.1更新與0.1.0回退亦已重驗，僅用程序內配置覆寫，沒有模型回合或全域設定變更；見[current-version adoption](codex-coding-harness-implementation-evidence/current-version-adoption-2/summary.json)。首次CLI keyPath引號格式導致未載入，原失敗紀錄保留，未當作成功。

套件可信 manifest SHA-256：`cdd9c5a7dd48c40993de8eaab226d98cb4bd79faed76ae76b322ef4392f5eb9d`。新建套件、既有 release 與本 repo 的開發快取均相符，見 [runtime 核對](codex-coding-harness-implementation-evidence/final-runtime-verification.json)。

## 三組實際結果

共同：Desktop 內附 0.164.0-alpha.11.1；配置 gpt-6.1-sol／high；Java 25.0.1、Maven 3.9.10；離線執行；各一個原始任務上下文、900 秒總上限、不整次補跑。A→B→C 依序執行。配置模型識別不證明實際 serving build。

| 組別 | 額外配置 | 實測總 wall time | 原生模組測試 | 凍結版外部驗收 V2 | 交付後診斷／品質 |
| --- | --- | ---: | --- | --- | --- |
| A | 原生流程，無 B/C 額外 harness 入口 | 236.74 秒 | 90／0 失敗／0 略過 | 13／13 通過 | factory-close 診斷通過；source review 未發現實質違反 |
| B | 固定舊版 task-harness | 297.71 秒 | 91／0 失敗／0 略過 | 13／13 通過 | **新增診斷確認 P1 read-lock 升級死鎖**；交付保留未修 |
| C | 四個候選 skills 的完整套件，明確呼叫新版 task-harness | 657.25 秒 | 93／0 失敗／0 略過 | 13／13 通過 | 同一 trial 有一次 controller 故障續作；自身獨立 review finding 修正，外部 source review 與 factory-close 診斷通過 |

這些時間不是人工投入，也不是可排名的無干擾性能數據。C 包含 controller 故障、修復、等待與原上下文續作；原始 900 秒上限沒有重設，沒有重建初始副本或重跑整次 trial。完整數據見 [outcomes](codex-coding-harness-implementation-evidence/flow-smoke-outcomes.json)、[A](codex-coding-harness-implementation-evidence/cli-smoke-A/summary.json)、[B](codex-coding-harness-implementation-evidence/cli-smoke-B/summary.json)、[C](codex-coding-harness-implementation-evidence/cli-smoke-C/summary.json)。

## 不可省略的修正與限制

**驗收也可能錯。** V1 grader 手動加入 internal post-processor，繞過公開 annotation 的 bean 生命週期，錯誤拒絕 A 的合法 disposal 解法。獨立 review 後只修正 bootstrap，兩個行為斷言與 TTL 有效性檢查未變。V2 parent 仍失敗，reference、共用 scheduler 替代解法與 A 固定產物均通過，全部 lifecycle 2 tests、0 skipped。A 只重評固定產物，沒有續作模型。見 [grader 升版紀錄](codex-coding-harness-implementation-evidence/frozen-trial-grader-v2.json)。

**主回合與子回合必須分辨。** C 首段 controller 誤把 reviewer 子回合完成視為主回合完成，主回合實際被提前中斷。確認原生 interrupted、writer 停止後，以同一 thread／副本續作，剩餘預算包含之前執行、修復與等待。修正版按 thread_id／turn_id 核對，並保留快速完成事件；真實事件串流回歸確認只接受指定主回合。見 [故障診斷](codex-coding-harness-implementation-evidence/cli-smoke-C/controller-recovery.json)、[整次結果](codex-coding-harness-implementation-evidence/cli-smoke-C/reconciled-state.json)、[歸屬回歸](codex-coding-harness-implementation-evidence/controller-root-attribution-regression.json)。

**測試全綠不等於沒有回歸。** 交付後 source review 更正 B 的漏報：get 持有 read lock 執行 factory，factory 呼叫 context.close 時，destroy 嘗試取得 write lock，會等待自己。公開介面的有界診斷在 parent、reference、A、C 通過，只在 B 失敗，0 skipped。這是事後診斷，不覆寫原 V2 13/13，也不是事前凍結的比較指標；不把不合作 callback 的限制拿來掩蓋鎖造成的死鎖。見 [診斷結果](codex-coding-harness-implementation-evidence/post-smoke-quality-assessment.json)。

**流程 smoke 的隔離仍有限。** 三組共享其他全域 skills；C 原始紀錄也有共用記憶索引讀取。未完整限制其他可讀副本、記憶或答案來源，不能稱純淨 A/B/C 或 held-out 評測。凍結清單含宿主生成的 Git metadata／objects；不沿用早期「無 history」觀察。初始凍結檔也漏了獨立的外部回饋欄位，已明示補錄：模型交付後才外部驗收，不向任一組送回 grader 結果。這些缺口不包裝成公平比較資格。

## 控制、原工作與成本

CLI 同連線取消取得 interrupted；背景 terminal 清理後空，父子 PID 缺席、heartbeat 穩定。40 秒縮短時限測試沿相同單調時鐘／保留20秒路徑約20.69秒收尾；沒有聲稱實際等待15分鐘測試。模擬原生 interrupt／clean 通訊失效時，獨立 writer 收尾約6.79秒完成；無標記負向 worker 保持存活。這些只覆蓋指定政策與保留專屬 TMPDIR 標記的程序，不是任意惡意 detached process 的通用容器保證。見 [正常控制](codex-coding-harness-implementation-evidence/cli-control-1/state.json)、[時限測試](codex-coding-harness-implementation-evidence/cli-deadline-1/state.json)、[故障收尾](codex-coding-harness-implementation-evidence/cli-fault-1/owner-check.json)。原生 API 依據為 [官方 App Server 文件](https://learn.chatgpt.com/docs/app-server)，結果仍以本機證據為準。

三組指定自身寫入成功、外部直接／symlink 寫入及 loopback 連線遭拒。外部 grader／產品來源唯讀，僅驗收副本 target 與獨立 tmp 可寫，且來源前後指紋相同。原 demo-002 的60個相關檔案與 git status 均未變；三組固定交付指紋仍相符，沒有剩餘 trial writer。新增的三項 trust 與 C 來源註冊已移除，其他設定及本 repo 開發來源保留。見 [原工作](codex-coding-harness-implementation-evidence/original-work-final-check.json)、[writer](codex-coding-harness-implementation-evidence/final-trial-writer-check.json)、[設定清理](codex-coding-harness-implementation-evidence/trial-environment-cleanup.json)。

主指標人工 active time 三組均標 unavailable，沒有填零。控制器在 trial 中沒有要求人工救援，但不代表使用者沒有觀察、審查或後續返工；觀察窗口尚未建立。準備階段至少記錄三次手動 Stop 回報、一次直接任務輸入；這不是完整打斷總數。沒有購買額外資源；原生 token 用量（含快取及重複模型輸入）保存在各 summary，不換算未確認的帳單金額。

## 目前判斷與後續優先序

首版可以作本機 CLI 的受控候選；不宣稱正式全面採用、一般省時、跨專案可移植，亦不擴張到其他宿主。必要控制缺口已透過本輪實際失敗補強，而不是為每個步驟增加固定角色或人工核准。

| 優先序 | 下一項工作 | 目前處置 |
| --- | --- | --- |
| P0 | 保留正確事件歸屬、失效收尾及公開啟用路徑的 regression | 已保留修正、真實事件回放與原始失敗，納入後續相關變更回歸 |
| P0 | B 的具體死鎖 | 保留原交付及可重現案例；本輪不改 B、不補跑，不當作可採用的該次產品修正 |
| P1 | 小量真實任務量測人工投入與返工，先同一專案 | 尚未執行；之後固定觀察窗口與接手政策，再決定採用價值 |
| P1 | 公平比較所需的配置／答案／記憶隔離，以及未見案例 | 尚未合格；原 smoke 不升格為能力比較 |
| P2 | 功能／重構、第二專案、其他宿主及 Desktop Stop | 保留後續階段，沒有越過本輪各一次上限擴樣 |

本機維護回歸：26項，25通過、1項需要原生 Windows cmd.exe 而略過；27個來源／測試輸入前後一致。見 [最終測試 receipt](codex-coding-harness-implementation-evidence/python-tests-final.json)。Windows、Desktop Stop、真實人工效益與第二專案均不以此結果宣稱通過。

完整設計與歷程：[設計規格](../specs/codex-coding-harness.spec.md)、[試行計畫](../plans/codex-coding-harness-pilot.plan.md)、[實作查核紀錄](codex-coding-harness-implementation.research.md)。持久回放輸入見 [retained-replay-inputs](codex-coding-harness-implementation-evidence/retained-replay-inputs.json)，不依賴暫存工作目錄長期存在。未 push、建立 PR 或部署。


## Standards

獨立 review 無新增可行動的 Standards 發現。已複核 staged runtime、封裝、測試、公開 bootstrap、有界 factory 診斷及完成文件；未發現硬規則違反或需處理的 Fowler smell。歷史快照與 patch 視為證據，不當作 runtime 重複程式。Windows、Desktop Stop、公平比較與一般效益未因此取得背書。

## Spec

獨立 review 無新增可行動 finding，確認足以關閉使用者核定的本機原生引擎首版與首次流程 smoke。完整 runtime、專案啟停回退、實際 C 交付、失效收尾、持久證據與來源綁定已有證據；三組各一次，原工作保護、異常及污染限制均保留。P5／P6、人工效益、公平比較、第二專案與 Desktop Stop 未達成，不包含於本次完成聲明。

兩軸總結：Standards 0、Spec 0 個新增可行動 finding；僅指本次 harness 來源與交付文件。B 產品的已確認 P1 診斷獨立保留，不被此 review 通過覆蓋。
