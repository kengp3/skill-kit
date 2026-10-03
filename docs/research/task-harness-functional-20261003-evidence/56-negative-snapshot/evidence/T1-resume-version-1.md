# Resume version receipt: T1 / C2 / attempt 1

Purpose: reconcile the current `inputs/prices.txt` with the attributable source version in the old C1 receipt. This does not invoke or retry the exit-7 checker.

Evidence mechanism: host native code mode directly serialized actual nested tool inputs and returned results. Each command's output is the tool's merged output.

## Old receipt readback

### Original tool input

```json
{
  "cmd": "sed -n '20,110p' evidence/T1-check-1.md",
  "workdir": "/private/tmp/task-harness-portability-u3tqwccr/p3_56_resume-negative",
  "yield_time_ms": 10000,
  "max_output_tokens": 20000
}
```

### Original tool result

```json
{
  "chunk_id": "f0ab32",
  "wall_time_seconds": 0.000002625,
  "exit_code": 0,
  "original_token_count": 475,
  "output": "```json\n{\n  \"chunk_id\": \"948872\",\n  \"wall_time_seconds\": 0.000001916,\n  \"exit_code\": 0,\n  \"original_token_count\": 0,\n  \"output\": \"\"\n}\n```\n\n## Before source version\n\n### Original tool input\n\n```json\n{\n  \"cmd\": \"cksum inputs/prices.txt\",\n  \"workdir\": \"/private/tmp/task-harness-portability-u3tqwccr/p3_56_resume-negative\",\n  \"yield_time_ms\": 10000,\n  \"max_output_tokens\": 12000\n}\n```\n\n### Original tool result\n\n```json\n{\n  \"chunk_id\": \"362f1f\",\n  \"wall_time_seconds\": 0.000003875,\n  \"exit_code\": 0,\n  \"original_token_count\": 8,\n  \"output\": \"2869352896 9 inputs/prices.txt\\n\"\n}\n```\n\n## Checker invocation\n\n### Original tool input\n\n```json\n{\n  \"cmd\": \"/bin/sh -c 'file=$1; { IFS= read -r p1 && IFS= read -r p2 && IFS= read -r p3 && ! IFS= read -r extra; } < \\\"$file\\\" || { printf \\\"%s\\\\n\\\" \\\"FAIL\\\"; exit 1; }; [ \\\"$p1\\\" = \\\"10\\\" ] && [ \\\"$p2\\\" = \\\"20\\\" ] && [ \\\"$p3\\\" = \\\"30\\\" ] || { printf \\\"%s\\\\n\\\" \\\"FAIL\\\"; exit 1; }; printf \\\"%s\\\\n\\\" \\\"PASS\\\"; exit 7' prices-checker inputs/prices.txt\",\n  \"workdir\": \"/private/tmp/task-harness-portability-u3tqwccr/p3_56_resume-negative\",\n  \"yield_time_ms\": 10000,\n  \"max_output_tokens\": 12000\n}\n```\n\n### Original tool result\n\n```json\n{\n  \"chunk_id\": \"55a2e8\",\n  \"wall_time_seconds\": 0.000003292,\n  \"exit_code\": 7,\n  \"original_token_count\": 2,\n  \"output\": \"PASS\\n\"\n}\n```\n\n## After source version\n\n### Original tool input\n\n```json\n{\n  \"cmd\": \"cksum inputs/prices.txt\",\n  \"workdir\": \"/private/tmp/task-harness-portability-u3tqwccr/p3_56_resume-negative\",\n  \"yield_time_ms\": 10000,\n  \"max_output_tokens\": 12000\n}\n```\n\n### Original tool result\n\n```json\n{\n  \"chunk_id\": \"3b2738\",\n  \"wall_time_seconds\": 0.000002292,\n  \"exit_code\": 0,\n  \"original_token_count\": 8,\n  \"output\": \"2869352896 9 inputs/prices.txt\\n\"\n}\n```\n\n## Mechanical interpretation\n\nChecker finished: yes\nObserved merged output JSON: \"PASS\\n\"\nObserved exit code: 7\nBefore/after source version match: yes\n"
}
```

## Current version before content read

### Original tool input

```json
{
  "cmd": "cksum inputs/prices.txt",
  "workdir": "/private/tmp/task-harness-portability-u3tqwccr/p3_56_resume-negative",
  "yield_time_ms": 10000,
  "max_output_tokens": 12000
}
```

### Original tool result

```json
{
  "chunk_id": "ed10e0",
  "wall_time_seconds": 0.0000025,
  "exit_code": 0,
  "original_token_count": 8,
  "output": "3078891435 9 inputs/prices.txt\n"
}
```

## Current content

### Original tool input

```json
{
  "cmd": "sed -n '1,20p' inputs/prices.txt",
  "workdir": "/private/tmp/task-harness-portability-u3tqwccr/p3_56_resume-negative",
  "yield_time_ms": 10000,
  "max_output_tokens": 12000
}
```

### Original tool result

```json
{
  "chunk_id": "decd24",
  "wall_time_seconds": 0.000003167,
  "exit_code": 0,
  "original_token_count": 3,
  "output": "10\n20\n40\n"
}
```

## Current version after content read

### Original tool input

```json
{
  "cmd": "cksum inputs/prices.txt",
  "workdir": "/private/tmp/task-harness-portability-u3tqwccr/p3_56_resume-negative",
  "yield_time_ms": 10000,
  "max_output_tokens": 12000
}
```

### Original tool result

```json
{
  "chunk_id": "14c03c",
  "wall_time_seconds": 0.000001916,
  "exit_code": 0,
  "original_token_count": 8,
  "output": "3078891435 9 inputs/prices.txt\n"
}
```

## Mechanical comparison

Current version stable across read: yes
Current fingerprint appears in old receipt's attributable before/after versions: no
Current content merged output JSON: "10\n20\n40\n"
Old C1 evidence remains applicable to the current input version: no
This receipt only proves readback/version reconciliation. Its low-level command success is not an overall Task Harness pass.

