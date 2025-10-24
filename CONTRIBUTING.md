# Contributing

## Pre-commit Hooks

To install the pre-commit hooks, run the following command:

```bash
git config core.hooksPath .githooks
```

## GitHub Actions SHA Pinning

All GitHub Actions used in this repository must be pinned to a specific commit SHA. This is a security measure to prevent the use of a compromised or malicious version of an action.

### How to Pin Actions

You can use the `scripts/pin-actions.sh` script to help with this process.

* **To preview the changes**, run the script with the `--preview` flag:
  ```bash
  ./scripts/pin-actions.sh --preview
  ```
  This will generate a `.github/PROVENANCE/actions-pin.json` file that shows the mapping between the action tags and their resolved SHAs.

* **To apply the changes**, run the script with the `--apply` flag:
  ```bash
  ./scripts/pin-actions.sh --apply
  ```
  This will update all the workflow files in `.github/workflows` to use the pinned SHAs.

### Pre-commit Hook

There is a pre-commit hook that will prevent you from committing any unpinned actions. If you see an error message about unpinned actions, please run the `pin-actions.sh` script to fix the issue.

## Notebook Commit Policy

When committing changes to a notebook, you must also update the corresponding `.audit.json` file. The pre-commit hook will check for this and will prevent you from committing if the audit file is not updated.

If you need to skip the audit for a specific commit, you can add the following tag to your commit message body:

```
NB-AUDIT-SKIP: <reason>
```

Replace `<reason>` with a brief explanation of why you are skipping the audit.

## Provenance Artifacts

For manual reviewer attestation, you can create and sign a provenance artifact using the `jules` CLI. This will be implemented in a future version.
