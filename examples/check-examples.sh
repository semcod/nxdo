#!/usr/bin/env bash
# Verify nxdo examples are present, non-empty, and valid.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

fail() {
  echo "FAIL: $*" >&2
  exit 1
}

pass() {
  echo "OK: $*"
}

require_file() {
  local path="$1"
  [[ -f "$path" ]] || fail "missing file: $path"
  [[ -s "$path" ]] || fail "empty file: $path"
  pass "file exists: $path ($(wc -c < "$path") bytes)"
}

echo "=== nxdo examples check ==="

require_file examples/nxdo-self-context.txt
require_file examples/nxdo-self-metrics.txt
require_file examples/nxdo-self-prompt.txt
require_file examples/nxdo-self-plan.json
require_file examples/nxdo-self-plan.txt

grep -q '^Project: nxdo' examples/nxdo-self-context.txt \
  || fail "context file should mention project nxdo"
pass "context mentions project nxdo"

grep -q 'Code Metrics for nxdo' examples/nxdo-self-metrics.txt \
  || fail "metrics file should report nxdo project"
pass "metrics report nxdo"

grep -q '=== PROJECT STATE ===' examples/nxdo-self-prompt.txt \
  || fail "prompt file should contain PROJECT STATE section"
pass "prompt contains PROJECT STATE"

python3 - <<'PY' || fail "plan JSON schema check failed"
import json
from pathlib import Path
data = json.loads(Path("examples/nxdo-self-plan.json").read_text())
assert data.get("project_name") == "nxdo", data.get("project_name")
tasks = data.get("tasks") or []
assert len(tasks) == 10, len(tasks)
for i, task in enumerate(tasks, start=1):
    assert task.get("number") == i, task
    assert task.get("title"), task
pass
print("OK: plan JSON has 10 tasks for nxdo")
PY

grep -q 'Task Plan' examples/nxdo-self-plan.txt \
  || fail "plan text output should contain Task Plan header"
pass "plan text contains Task Plan header"

if command -v nxdo >/dev/null 2>&1; then
  nxdo validate examples/nxdo-self-plan.json >/dev/null
  pass "nxdo validate examples/nxdo-self-plan.json"
else
  PYTHONPATH=src python -m nxdo validate examples/nxdo-self-plan.json >/dev/null
  pass "python -m nxdo validate examples/nxdo-self-plan.json"
fi

echo "=== all example checks passed ==="
