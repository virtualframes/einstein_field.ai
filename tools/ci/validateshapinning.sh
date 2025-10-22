#!/usr/bin/env bash
set -euo pipefail
repo_root="$(git rev-parse --show-toplevel)"
workflowsdir="$repo_root/.github/workflows"
echo "Scanning GitHub Actions workflows for unpinned actions..."

unpatched=0
while IFS= read -r -d '' file; do
  # Find lines with 'uses: owner/repo@ref' but where ref is not a 40-char SHA
  matches=$(grep -nE "uses: .*/.*@" "$file" | grep -vE "@[a-f0-9]{40}$" || true)
  if [[ -n "$matches" ]]; then
    echo "Unpinned actions in $file:"
    echo "$matches"
    unpatched=$((unpatched+1))
  fi
done < <(find "$workflowsdir" -name '*.yml' -print0)

if [[ $unpatched -eq 0 ]]; then
  echo "All workflows are pinned to full SHAs."
  exit 0
fi

echo "Generate automated pin suggestions with 'tools/ci/generate_pins.py' or pin manually."
exit 2
