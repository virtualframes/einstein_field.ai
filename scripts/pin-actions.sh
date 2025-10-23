#!/usr/bin/env bash
set -euo pipefail
PROG=${0##*/}
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || echo ".")"
PROVDIR="${REPO_ROOT}/.github/PROVENANCE"
PROVFILE="${PROVDIR}/actions-pin.json"
mkdir -p "$PROVDIR"
TS=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
SHORT_HEAD=$(git rev-parse --short HEAD 2>/dev/null || echo "nohead")
APPLY=false; DRY=false
case "${1:-}" in
  --apply) APPLY=true ;;
  --dry-run) DRY=true ;;
  --preview|"") ;;
  --help) cat <<EOF
Usage: $PROG [--preview|--apply|--dry-run]
--preview : discover and write provenance, no edits
--apply   : create branch, apply replacements, push (no merge)
--dry-run : verbose preview
EOF
exit 0 ;;
  *) echo "Unknown arg $1"; exit 2 ;;
esac

# discovery: anchored grep; fallback to python YAML line search
discover() {
  grep -RIn --exclude-dir=.git -E '^[:space:]*uses:[[:space:]]*[^@[:space:]]+@[^[:space:]]+' .github/workflows 2>/dev/null || true
}
discover_py() {
  python3 - <<'PY' 2>/dev/null || true
import glob,re
pat=re.compile(r'^\s(?:-\s)?uses:\s*([^\s/@]+/[^\s@]+)@([^\s#\s]+)')
files=glob.glob('.github/workflows/*.yml')+glob.glob('.github/workflows/*.yaml')
for p in files:
  with open(p,'r',encoding='utf-8',errors='ignore') as f:
    for i,l in enumerate(f,1):
      m=pat.match(l)
      if m:
        print(f"{p}:{i}:uses: {m.group(1)}@{m.group(2)}")
PY
}

raw=$(discover)
if [ -z "${raw// /}" ]; then raw=$(discover_py); fi
mapfile -t LINES < <(printf '%s\n' "$raw" | sed '/^\s*$/d' || true)
if [ ${#LINES[@]} -eq 0 ]; then
  printf '{"generatedat":"%s","invoker":"%s","reporef":"%s","entries":[]}\n' "$TS" "${GIT_AUTHOR_NAME:-jules-agent}" "$SHORT_HEAD" > "$PROVFILE"
  echo "No uses: entries found. Wrote empty provenance."
  exit 0
fi

TMP=$(mktemp)
echo -n "[" > "$TMP"
first=1
REPL=$(mktemp)
while IFS= read -r ln; do
  file=$(printf '%s' "$ln" | sed -E 's/^([^:]+):[0-9]+:.*$/\1/')
  line=$(printf '%s' "$ln" | sed -E 's/^[^:]+:([0-9]+):.*/\1/')
  token=$(printf '%s' "$ln" | sed -n 's/.uses:[[:space:]]//p')
  owner_repo="${token%@}"; ref="${token#@}"
  if printf '%s' "$ref" | grep -qE '^[0-9a-f]{40}$'; then
    continue
  fi
  repo_url="https://github.com/${owner_repo}.git"
  gittagout=$(git ls-remote "$repo_url" "refs/tags/${ref}" 2>&1 || true)
  sha=""; method=""
  if [ -n "${gittagout// /}" ]; then
    sha=$(printf '%s' "$gittagout" | head -n1 | awk '{print $1}')
    method="refs/tags"
  else
    githeadout=$(git ls-remote "$repo_url" "refs/heads/${ref}" 2>&1 || true)
    if [ -n "${githeadout// /}" ]; then
      sha=$(printf '%s' "$githeadout" | head -n1 | awk '{print $1}')
      method="refs/heads"
    else
      gitall=$(git ls-remote "$repo_url" 2>&1 || true)
      matched=$(printf '%s\n' "$git_all" | grep -E "/${ref}(\^{}|$)" | head -n1 | awk '{print $1}' || true)
      if [ -n "$matched" ]; then sha="$matched"; method="refs/tags(annotated)"; gittagout="$git_all"; fi
    fi
  fi

#json fragment
  entry=$(python3 - <<PY
import json,sys
print(json.dumps({
  "workflow_file":"$file",
  "line":int($line),
  "usesoriginal":"$owner_repo@$ref",
  "resolved_sha": "$sha" if "$sha"!="" else None,
  "resolution_method":"$method" if "$method"!="" else "failed",
  "gitlsremoteraw": """${gittagout:-$githeadout}"""
}))
PY
)
  if [ $first -eq 1 ]; then
    printf '%s' "$entry" >> "$TMP"; first=0
  else
    printf ',%s' "$entry" >> "$TMP"
  fi
  if [ -n "$sha" ]; then
    printf '%s\t%s\t%s\n' "$file" "${owner_repo}@${ref}" "${owner_repo}@${sha}" >> "$REPL"
  fi
done < <(printf '%s\n' "${LINES[@]}")
printf ']\n' >> "$TMP"
jq -c . "$TMP" >/dev/null 2>&1 || cat "$TMP" > "$PROV_FILE"

#Build final prov
script_hash=$(sha1sum "$0" | awk '{print $1}' 2>/dev/null || echo "")
python3 - <<PY > "$PROVFILE"
import json
import os
d=json.load(open("$TMP"))
out={
 "generated_at":"$TS",
 "invoker":"${GIT_AUTHOR_NAME:-jules-agent}",
 "reporef":"$SHORT_HEAD",
 "scriptversion":"$script_hash",
 "entries": d
}
# Use os.path.join for constructing file paths
prov_file_path = os.path.join(os.getcwd(), "$PROVFILE")
with open(prov_file_path, "w") as f:
    json.dump(out, f, indent=2)
PY
rm -f "$TMP"
echo "Wrote provenance to $PROVFILE"
echo "Preview of replacements:"
if [ -s "$REPL" ]; then
  while IFS=$'\t' read -r wf orig repl; do printf "%s: %s -> %s\n" "$wf" "$orig" "$repl"; done < "$REPL"
else
  echo "No resolved replacements"
fi

#unresolved check
UNRES=$(python3 - <<PY
import json
a=json.load(open("$PROVFILE"))
print(sum(1 for e in a["entries"] if e.get("resolution_method")=="failed"))
PY
)
if [ "$UNRES" -gt 0 ]; then
  echo "Warning: $UNRES unresolved entries recorded in provenance"
fi
if [ "$APPLY" != "true" ]; then
  echo "Run with --apply to create branch with replacements (requires git push permissions)."
  exit 0
fi

#apply
BR="pin-actions/${TS//[:]/}-${SHORT_HEAD}"
git fetch --all --prune >/dev/null 2>&1 || true
git checkout -b "$BR"
touched=()
if [ -s "$REPL" ]; then
  while IFS=$'\t' read -r wf orig repl; do
    [ -f "$wf" ] || { echo "skip missing $wf"; continue; }
    cp "$wf" "${wf}.bak"
    touched+=("$wf")
    perl -0777 -pe "s/\Q$orig\E/$repl/g" "${wf}.bak" > "$wf"
    echo "applied $orig -> $repl in $wf (backup ${wf}.bak)"
  done < "$REPL"
fi
git add "$PROVFILE"
for f in "${touched[@]}"; do git add "$f"; done
git commit -m "ci: pin GitHub Actions to SHAs; provenance: .github/PROVENANCE/actions-pin.json" || true
git push -u origin "$BR"
echo "Pushed branch $BR"
echo "PR body:"
printf '%s\n' "Automated pin PR. Provenance: .github/PROVENANCE/actions-pin.json"
