#!/usr/bin/env bash
# Minimal self-check for the AGENTS.md governance rules.
# Exit code 0 = pass, 1 = fail.
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cfg="$root/AGENTS.md"
fail=0

has() { # label, extended regex
  if grep -Eq -- "$2" "$cfg"; then
    echo "PASS: $1"
  else
    echo "FAIL: $1"
    fail=1
  fi
}

if [ ! -f "$cfg" ]; then
  echo "FAIL: AGENTS.md not found at $cfg"
  exit 1
fi

sections="$(grep -Ec '^## [1-5]\. ' "$cfg" || true)"
if [ "$sections" -eq 5 ]; then
  echo "PASS: 5 numbered rule sections present"
else
  echo "FAIL: expected 5 numbered rule sections, found $sections"
  fail=1
fi

has "rule 1: Chinese conversation, English reports" '中文.*英文|英文.*报告'
has "rule 2: karpathy-guidelines skill" 'karpathy-guidelines'
has "rule 3: commit on every change" 'git commit'
has "rule 4: test + simulate before commit" '测试.*模拟'
has "rule 5a: requirement/tech doc linked" '1gtXetjRMJPsyf2Oy3_ry1-jAWAEhTNbjVmHc7na862s'
has "rule 5b: assignment guideline path" 'CSC60904-Deep Learning Group Assignment 30%\.pdf'
has "rule 5c: report doc linked" '1TewRPdkWW4jRivSg-_MLOrYXNsRWVOR0tHExsaQ_LjQ'
has "rule 5d: no cached requirements copy" '禁止在仓库里缓存'
has "rule 5e: doc A date is internal, not assignment deadline" '内部截止日期'
has "rule 5f: report doc read-only unless authorized" '默认只读'

if grep -q '^\.DS_Store$' "$root/.gitignore" 2>/dev/null; then
  echo "PASS: .DS_Store ignored"
else
  echo "FAIL: .DS_Store not listed in .gitignore"
  fail=1
fi

if [ "$fail" -eq 0 ]; then
  echo "RESULT: PASS"
else
  echo "RESULT: FAIL"
fi
exit "$fail"
