# Planner Checkpoint: PR #7 - Harden CI / enforce SHA pinning

**Detected Failure:**
- **File:** `.github/workflows/agent-integration.yml`
- **Issue:** The "Enforce SHA Pinning" CI job failed because the workflow was using tags (`@v4`, `@v2`) instead of full commit SHAs for three GitHub Actions.

**Repo State:**
- **HEAD:** (Will be filled in with the actual commit SHA)

**Chosen Resolution Strategy:**
1.  **Resolve SHAs:** Use `git ls-remote` to get the full 40-character commit SHAs for `actions/checkout`, `docker/login-action`, and `actions/upload-artifact`.
2.  **Patch Workflow:** Replace the tags in `agent-integration.yml` with the resolved SHAs.
3.  **Verify:** Run `grep` to ensure no other workflows are using tags. Run `yamllint` to check for syntax issues.
4.  **Commit and PR:** Commit the change to a new branch (`fix/ci-pin-actions-pr-7`) and open a pull request.
