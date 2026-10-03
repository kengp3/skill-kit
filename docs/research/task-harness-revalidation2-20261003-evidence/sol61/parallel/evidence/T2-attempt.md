# T2 check attempt

Attempt 1 checks `labels.py` with the bundled `run_check.py` runner.
Receipt: `evidence/T2-check-1.json`.
Command: `python3 -c 'from labels import label; assert label("  Alice  ") == "Alice"; assert label("   ") == "Guest"'`.
The attempt is recorded before invoking the runner. No retry is authorized by this record.
