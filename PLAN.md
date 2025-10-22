# PLAN: CI SHA Enforcement and Auto-Pinning

- Detect workflows with semver-style or tag refs instead of full SHAs
- Run tools/ci/generate_pins.py (requires GITHUB_PAT) to replace refs with full SHAs
- Run tools/ci/validateshapinning.sh to confirm no remaining unpinned actions
- Commit and open PR titled "chore(ci): pin GitHub Actions to full SHAs"
- Add provenance receipt in audit/sha_pinning.log recording:
  - timestamp, commit sha, changed files, GITHUB_PAT masked, resolver output
- After merge, snapshot environment and run CI to validate
