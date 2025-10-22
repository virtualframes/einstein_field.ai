#!/usr/bin/env bash
set -euo pipefail
receipt_dir="audit"
mkdir -p "$receipt_dir"
cat > "$receipt_dir/sha_pinning.$(date -u +%Y%m%dT%H%M%SZ).json" <<EOF
{
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "actor": "jules",
  "branch": "$(git rev-parse --abbrev-ref HEAD || echo unknown)",
  "commit": "$(git rev-parse --short HEAD || echo unknown)",
  "changed_files": "$(git diff --name-only HEAD~1 HEAD || echo unknown)"
}
EOF
git add "$receipt_dir"
git commit -m "chore(audit): add sha pinning receipt"
