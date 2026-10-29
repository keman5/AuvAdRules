#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"
awake_pid=
if command -v caffeinate >/dev/null 2>&1; then caffeinate -di & awake_pid=$!; fi
cleanup() {
  local status=$?
  [[ -z "$awake_pid" ]] || kill "$awake_pid" 2>/dev/null || true
  if command -v go >/dev/null 2>&1; then go clean -cache -testcache || true; fi
  exit "$status"
}
trap cleanup EXIT
export PYTHONDONTWRITEBYTECODE=1
case "${1:-test}" in
  test) python3 -m unittest discover -s tests -v ;;
  update) shift; python3 -m unittest discover -s tests -v; python3 scripts/update.py "$@" ;;
  publish)
    git diff --check
    test -z "$(git status --porcelain)" || { echo 'Commit reviewed changes before publishing.' >&2; exit 1; }
    gh repo view keman5/AuvAdRules >/dev/null 2>&1 || gh repo create keman5/AuvAdRules --public --description 'Shared AdGuard Home and client DNS rules with validated upstream updates'
    git remote get-url origin >/dev/null 2>&1 || git remote add origin https://github.com/keman5/AuvAdRules.git
    git push -u origin main
    ;;
  pages)
    gh api repos/keman5/AuvAdRules/pages --jq .html_url 2>/dev/null || \
      gh api repos/keman5/AuvAdRules/pages --method POST --input - <<'JSON'
{"build_type":"legacy","source":{"branch":"main","path":"/"}}
JSON
    ;;
  pages-build)
    # GITHUB_TOKEN commits do not automatically trigger a branch-based Pages build.
    gh api repos/keman5/AuvAdRules/pages/builds --method POST
    ;;
  *) echo 'Usage: bash build.sh test|update [--source-file PATH]|publish|pages|pages-build' >&2; exit 2 ;;
esac
