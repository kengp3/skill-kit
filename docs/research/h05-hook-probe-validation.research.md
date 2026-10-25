# H05A C0 開發探針的離線驗證

日期：2026-10-25。基線 `27ead1b`，完成前合併 `953d6cb`。本切片只實作開發端 probe，H05A 的真實接入、事件與產品補救仍未驗收；不標 done。

## 公共接口與責任

`tests/harness/hook_probe.py` 使用 Python 3 標準函式庫，以 stdin 讀取單一 JSON event，stdout 回傳 hook JSON。必填 `--test-root ABS` 與 `--evidence-dir ABS`；不自動發現專案、不啟動 server 或模型、不變更產品 handler、合約或 host 資格。

證據目錄必須是指定測試 root 的子目錄，event cwd 也須位於該 root，拒絕 symlink、越界及非目錄。此命令只向指定證據目錄寫入；實際封存回 repo 由既有開發證據流程處理。不提供 OS 隔離或抗外部惡意目錄置換的安全沙箱。

每個證據目錄代表一個 C0 probe attempt，必須與產品 handler 的測試目錄／session 分開。固定 `continuation.json` 以 exclusive-create 保留最多一次額度，不按 turn 或 session 改變重置；既有空或部分收據亦不得清除重試。先保存收據，再保存事件，兩者成功後才可輸出 block。記錄失敗／結果不明不補救；已保留的額度不退還。

探針唯一續作指示是：

> C0 probe only: reply exactly C0_PROBE_CONTINUATION_CONFIRMED, then finish. Do not run tools, modify files or perform product work.

它只測試固定無害文字回應。SessionStart、UserPromptSubmit 及 `stop_hook_active=true` 都不要求工作。正常 Stop 須有原生非空 session_id 及明確布林 false 才可要求 canary；缺 session 或 Stop flag 時保留觀測、明示缺口。turn_id 缺失時不補值；probe 額度不依賴它，故仍可觀察一次 canary，但不能據此聲稱產品的 user-turn 資格成立。

## 記錄格式與限制

只保存原生 `hook_event_name`、`session_id`、`turn_id`、`stop_hook_active` 的實際存在值及本地 `sequence`；不存 prompt、transcript、cwd、額外 payload 或憑證。缺欄位保留缺失，null 保留 null。sequence 是不可覆寫事件檔的原子保留順序，提供本地觀測排序，並非宿主因果順序證明；並行程序的先後不能由它推論模型回合來源。

事件輸入上限 1 MiB，identity 字串上限 4096 字元，單一 attempt 最多 256 個事件記錄。錯誤以合法 JSON systemMessage 明示，return code 0 不代表行為通過；CLI 參數錯誤不使用可能觸發續作的 exit 2。保留的技術收據只證明預留一次 probe 嘗試，不能證明 stdout 已送達或模型真的續作。

## TDD 與直接結果

測試 seam 是 subprocess CLI → stdout／exit／測試證據檔，僅用合成事件與 TemporaryDirectory，不 mock 私有函式。依序完成觀測、canary、拒絕邊界三個 red→green 切片，最後補強受保護檔案未變與缺身分不保留額度的檢查。

| 階段 | Exit code | 實際執行摘要 |
| --- | --- | --- |
| observation-red | 1 | Ran 1 test in 0.017s |
| observation-green | 0 | Ran 1 test in 0.062s |
| canary-red | 1 | Ran 3 tests in 0.122s |
| canary-green | 0 | Ran 3 tests in 0.262s |
| boundary-red | 1 | Ran 9 tests in 0.803s |
| boundary-green | 0 | Ran 9 tests in 0.895s |
| final-probe-regression | 0 | Ran 9 tests in 0.870s |

第一個 red 是 handler 尚不存在；canary red 是缺少 block；boundary red 暴露格式錯誤未轉 JSON、預設 exit 2、路徑拒絕及保存失敗未處理。這些負例的寫入均侷限於測試擁有的臨時父目錄，結束後清除；未觸及日常設定或其他專案。

重現命令（repo root）：

```text
python3 -B -m unittest discover -s tests -p 'test_harness_hook_probe.py' -v
```

最終實際輸出：

```text
test_bad_input_or_missing_control_flag_is_visible_without_block (test_harness_hook_probe.HookProbeTest.test_bad_input_or_missing_control_flag_is_visible_without_block) ... ok
test_canary_is_once_per_attempt_even_when_native_turn_changes (test_harness_hook_probe.HookProbeTest.test_canary_is_once_per_attempt_even_when_native_turn_changes) ... ok
test_continuation_stop_is_observed_without_requesting_more_work (test_harness_hook_probe.HookProbeTest.test_continuation_stop_is_observed_without_requesting_more_work) ... ok
test_invalid_cli_arguments_do_not_use_exit_two (test_harness_hook_probe.HookProbeTest.test_invalid_cli_arguments_do_not_use_exit_two) ... ok
test_missing_native_identity_is_preserved_without_fabrication (test_harness_hook_probe.HookProbeTest.test_missing_native_identity_is_preserved_without_fabrication) ... ok
test_parallel_stops_have_one_reservation_and_unique_observation_order (test_harness_hook_probe.HookProbeTest.test_parallel_stops_have_one_reservation_and_unique_observation_order) ... ok
test_record_failure_consumes_attempt_without_continuation_or_retry (test_harness_hook_probe.HookProbeTest.test_record_failure_consumes_attempt_without_continuation_or_retry) ... ok
test_records_only_native_whitelist_in_observed_order_without_execution (test_harness_hook_probe.HookProbeTest.test_records_only_native_whitelist_in_observed_order_without_execution) ... ok
test_scope_and_symlink_rejections_do_not_write_outside_test_root (test_harness_hook_probe.HookProbeTest.test_scope_and_symlink_rejections_do_not_write_outside_test_root) ... ok

----------------------------------------------------------------------
Ran 9 tests in 0.870s

OK
```

9 個測試涵蓋白名單與序號、一次／重複／跨 turn 及 session／八程序並行去重、續作重入、輸出遺失不補發、scope/symlink 拒絕、記錄失敗不續作／不回補額度、缺少原生欄位、JSON／輸入上限／CLI 錯誤，以及產品／合約／host 資格檔案未變。

實測環境 Python 3.15.0。未執行新模型 trial、產品正向補救、原生信任／載入或真實 hook 事件；沒有資格翻旗、安裝、全域設定寫入、OS/watchdog 或通用 runner。這些離線結果只驗證探針確定性行為，不能替代 C0 或 H05A 驗收。
