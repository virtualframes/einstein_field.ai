from pathlib import Path
import nbformat
from nbclient import NotebookClient
import hashlib
from typing import List, Dict
from agents.jules.provenance import record_execution

import json

def validate_notebook(path: str, env_spec: dict = None, baseline_path: str = None) -> dict:
    """Runs notebook in a reproducible ephemeral environment."""
    # This is a placeholder implementation.
    # A real implementation would use a container or virtual environment.
    with open(path) as f:
        nb = nbformat.read(f, as_version=4)

    client = NotebookClient(nb)
    client.execute()

    outputs_hash = hashlib.sha256(str(nb).encode('utf-8')).hexdigest()

    status = "success"
    failures = []

    if baseline_path:
        with open(baseline_path) as f:
            baseline = json.load(f)
        if outputs_hash != baseline["expected_outputs_hash"]:
            status = "failure"
            failures.append("outputs_hash mismatch")

    provenance_id = record_execution(
        target=path,
        actor="jules-validator",
        inputs={"env_spec": env_spec, "baseline_path": baseline_path},
        outputs={"outputs_hash": outputs_hash},
        metadata={}
    )

    return {
        "status": status,
        "failures": failures,
        "execution_times": {},
        "outputs_hash": outputs_hash,
        "provenance_id": provenance_id,
    }

def extract_citations(path: str) -> List[dict]:
    """Scans markdown and code cells for citation keys and DOI/URL references."""
    # This is a placeholder implementation.
    return []

def validate_plan(plan_path="agents/jules/PLAN.md"):
    p = Path(plan_path)
    content = p.read_text()
    if "Intent" not in content:
        raise AssertionError("Missing Intent section")
    if "- [ ]" not in content:
        raise AssertionError("No tasks found")
    # basic dependency presence check
    if "Dependencies" not in content:
        raise AssertionError("Missing Dependencies section")
    print("Plan validation passed.")
