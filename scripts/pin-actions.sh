#!/bin/bash
set -euo pipefail

# --- Configuration ---
# Set the default path for workflow files and the provenance file.
WORKFLOWS_PATH=".github/workflows"
PROVENANCE_FILE=".github/PROVENANCE/actions-pin.json"
LOG_DIR="logs"
PREVIEW_LOG="${LOG_DIR}/pin-preview.log"
APPLY_LOG="${LOG_DIR}/pin-apply.log"
# An array of known tags to resolve to SHAs. This can be expanded.
# Format: "user/repo@tag"
ACTIONS_TO_PIN=(
  "actions/checkout@v2"
  "actions/setup-python@v2"
  "docker/login-action@v2"
  "sigstore/cosign-installer@v3.5.0"
  "actions/upload-artifact@v2"
  "actions/download-artifact@v2"
  "docker/setup-buildx-action@v1"
  "docker/build-push-action@v2"
  "ihs7/action-sha-pinned-actions@v1"
  "actions/checkout@v3"
  "docker/login-action@v1"
  "docker/setup-buildx-action@v1"
  "docker/build-push-action@v2"
  "actions/setup-python@v4"
)

# --- Functions ---

# Log a message to stdout.
log() {
  echo "[*] $1"
}

# Log an error message to stderr.
log_error() {
  echo "[!] $1" >&2
}

# Ensure the necessary directories exist.
ensure_dirs() {
  mkdir -p "$(dirname "$PROVENANCE_FILE")"
  mkdir -p "$LOG_DIR"
}

# Resolve a single action tag (e.g., "actions/checkout@v2") to its commit SHA.
# Uses git ls-remote to find the SHA for the given tag.
resolve_sha() {
  local action_spec="$1"
  local repo_url="https://github.com/${action_spec%@*}"
  local tag="${action_spec#*@}"

  log "Resolving ${repo_url} for tag ${tag}..." >&2

  # Use git ls-remote to find the tag's SHA. We filter for the exact tag.
  local sha
  sha=$(git ls-remote --tags "$repo_url" "refs/tags/${tag}" | awk '{print $1}')

  if [[ -z "$sha" ]]; then
    log_error "Could not resolve SHA for ${action_spec}. Skipping."
    return 1
  fi

  echo "$sha"
}

# --- Main Script Logic ---

# Default mode is preview.
MODE="preview"
if [[ "${1:-}" == "--apply" ]]; then
  MODE="apply"
elif [[ "${1:-}" == "--preview" ]]; then
  MODE="preview"
fi

ensure_dirs

# Initialize logs.
> "$PREVIEW_LOG"
> "$APPLY_LOG"

log "Running in ${MODE} mode."

# For preview mode, we generate a JSON provenance file.
if [[ "$MODE" == "preview" ]]; then
  log "Generating provenance file at ${PROVENANCE_FILE}"
  echo "{" > "$PROVENANCE_FILE"

  first_entry=true
  for action in "${ACTIONS_TO_PIN[@]}"; do
    sha=$(resolve_sha "$action")

    if [[ -n "$sha" ]]; then
      # Add a comma before the new entry if it's not the first one
      if [ "$first_entry" = true ]; then
        first_entry=false
      else
        echo "," >> "$PROVENANCE_FILE"
      fi
      # Add the entry to the JSON file.
      echo "  \"${action}\": \"${sha}\"" >> "$PROVENANCE_FILE"
    fi
  done

  echo "}" >> "$PROVENANCE_FILE"
  log "Provenance file generated."

# For apply mode, we find and replace the tags in the workflow files.
elif [[ "$MODE" == "apply" ]]; then
  log "Applying pins to workflows in ${WORKFLOWS_PATH}"

  for action in "${ACTIONS_TO_PIN[@]}"; do
    sha=$(resolve_sha "$action")

    if [[ -n "$sha" ]]; then
      log "Pinning ${action} to ${sha}" | tee -a "$APPLY_LOG"
      # Use grep to find files and sed to replace the action tag with the SHA.
      files_to_update=$(grep -rl "uses: ${action}" "$WORKFLOWS_PATH" || true)
      for file in $files_to_update; do
        log "  -> Updating ${file}" | tee -a "$APPLY_LOG"
        sed -i "s|uses: ${action}|uses: ${action%@*}@${sha}|" "$file"
      done
    fi
  done

  log "Pinning complete."
fi
