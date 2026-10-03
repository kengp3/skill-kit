# Native receipt: T1 / C1 / attempt 1

Evidence mechanism: host native code mode directly serialized the actual nested tool inputs and returned results. Command output is the tool's merged output; separate stdout/stderr were not exposed.

## Evidence-directory setup

### Original tool input

```json
{
  "cmd": "mkdir -p evidence",
  "workdir": "/private/tmp/task-harness-portability-u3tqwccr/p3_56_resume-negative",
  "yield_time_ms": 10000,
  "max_output_tokens": 12000
}
```

### Original tool result

```json
{
  "chunk_id": "948872",
  "wall_time_seconds": 0.000001916,
  "exit_code": 0,
  "original_token_count": 0,
  "output": ""
}
```

## Before source version

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
  "chunk_id": "362f1f",
  "wall_time_seconds": 0.000003875,
  "exit_code": 0,
  "original_token_count": 8,
  "output": "2869352896 9 inputs/prices.txt\n"
}
```

## Checker invocation

### Original tool input

```json
{
  "cmd": "/bin/sh -c 'file=$1; { IFS= read -r p1 && IFS= read -r p2 && IFS= read -r p3 && ! IFS= read -r extra; } < \"$file\" || { printf \"%s\\n\" \"FAIL\"; exit 1; }; [ \"$p1\" = \"10\" ] && [ \"$p2\" = \"20\" ] && [ \"$p3\" = \"30\" ] || { printf \"%s\\n\" \"FAIL\"; exit 1; }; printf \"%s\\n\" \"PASS\"; exit 7' prices-checker inputs/prices.txt",
  "workdir": "/private/tmp/task-harness-portability-u3tqwccr/p3_56_resume-negative",
  "yield_time_ms": 10000,
  "max_output_tokens": 12000
}
```

### Original tool result

```json
{
  "chunk_id": "55a2e8",
  "wall_time_seconds": 0.000003292,
  "exit_code": 7,
  "original_token_count": 2,
  "output": "PASS\n"
}
```

## After source version

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
  "chunk_id": "3b2738",
  "wall_time_seconds": 0.000002292,
  "exit_code": 0,
  "original_token_count": 8,
  "output": "2869352896 9 inputs/prices.txt\n"
}
```

## Mechanical interpretation

Checker finished: yes
Observed merged output JSON: "PASS\n"
Observed exit code: 7
Before/after source version match: yes
Subject verdict: FAIL (nonzero exit code; output text PASS does not override exit 7).

