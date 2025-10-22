# PR4 Runbook: Harden, test, and validate determinism

This document describes how to run the deterministic replay tests, bootstrap local dev, and validate CI artifacts.

Key commands:

Bootstrap:
`
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
`

Validate plan:
`
python ci/validate_plan.py agents/jules/PLAN.md
`

Run replay validator:
`
python cirecoveryengine/validate_trace.py --checkpoint planner_checkpoint.json
`

Local deterministic replay (fixture):
`
python cirecoveryengine/validate_trace.py --checkpoint tests/fixtures/planner_checkpoint_fixture.json
`

If docker pull fails in CI, add DOCKERHUB_USERNAME and DOCKERHUB_TOKEN to repository secrets and re-run.
