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

sections="$(grep -Ec '^## [1-6]\. ' "$cfg" || true)"
if [ "$sections" -eq 6 ]; then
  echo "PASS: 6 numbered rule sections present"
else
  echo "FAIL: expected 6 numbered rule sections, found $sections"
  fail=1
fi

has "rule 1: Chinese conversation, English reports" '中文.*英文|英文.*报告'
has "rule 2: karpathy-guidelines skill" 'karpathy-guidelines'
has "rule 3: commit on every change" 'git commit'
has "rule 3b: config updated on important changes" '重要变动必须回写本文件'
has "rule 4: test + simulate before commit" '测试.*模拟'
has "rule 5a: requirement/tech doc linked" '1gtXetjRMJPsyf2Oy3_ry1-jAWAEhTNbjVmHc7na862s'
has "rule 5b: assignment guideline path" 'CSC60904-Deep Learning Group Assignment 30%\.pdf'
has "rule 5c: report doc linked" '1TewRPdkWW4jRivSg-_MLOrYXNsRWVOR0tHExsaQ_LjQ'
has "rule 5d: no cached requirements copy" '禁止在仓库里缓存'
has "rule 5e: doc A date is internal, not assignment deadline" '内部截止日期'
has "rule 5f: report doc read-only unless authorized" '默认只读'
has "rule 5g: code source registered as code/" 'code/'
has "rule 5h: single TensorFlow/Keras stack" '统一使用 TensorFlow / Keras'
has "rule 5i: three-dataset and label plan recorded" 'SIIM-ISIC 2020'
has "rule 6a: local tests use conda dev" 'conda activate dev'
has "rule 6b: Colab is the delivery runtime" 'Google Colab'

code_dir="$root/code"
if [ -d "$code_dir" ]; then
  echo "PASS: code/ directory present"
  notebooks="$(find "$code_dir" -maxdepth 1 -type f -name '*.ipynb' | sort)"
  count="$(printf '%s\n' "$notebooks" | grep -c . || true)"
  if [ "$count" -eq 0 ]; then
    echo "PASS: no .ipynb yet in code/ (allowed during development; final must have exactly one)"
  elif [ "$count" -eq 1 ]; then
    echo "PASS: exactly one .ipynb in code/ ($(basename "$notebooks"))"
  else
    echo "FAIL: expected at most one .ipynb in code/, found $count"
    fail=1
  fi
else
  echo "FAIL: code/ directory not found"
  fail=1
fi

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
