import json
import hashlib
from datetime import datetime, timezone
import os
import subprocess

def get_git_sha():
    """Gets the current git SHA."""
    try:
        return subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode('ascii').strip()
    except Exception:
        return None

def record_execution(target: str, actor: str, inputs: dict, outputs: dict, metadata: dict) -> str:
    """Creates a signed provenance JSON and returns provenance_id (SHA256 of canonical JSON)."""
    provenance = {
        "target": target,
        "actor": actor,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "inputs": inputs,
        "outputs": outputs,
        "metadata": {
            **metadata,
            "git_sha": get_git_sha(),
            "workflow_id": os.environ.get("GITHUB_RUN_ID"),
        },
        "signatures": []
    }
    canonical_json = json.dumps(provenance, sort_keys=True, indent=2)
    provenance_id = hashlib.sha256(canonical_json.encode('utf-8')).hexdigest()
    provenance["id"] = provenance_id

    # Persist to .provenance/<provenance_id>.json
    with open(f".provenance/{provenance_id}.json", "w") as f:
        json.dump(provenance, f, sort_keys=True, indent=2)

    # Append index in .github/PROVENANCE/notebook-runs.json
    # This will be implemented later

    return provenance_id

def load_provenance(provenance_id: str) -> dict:
    """Loads a provenance JSON."""
    with open(f".provenance/{provenance_id}.json", "r") as f:
        return json.load(f)

def verify_provenance(provenance_json: dict) -> bool:
    """Verifies a provenance JSON."""
    # This will be implemented later
    return True

def emit_deepseek_provenance(run_id: str, call_meta: dict):
    """Emits a provenance record for a DeepSeek API call."""
    provenance_id = record_execution(
        target="deepseek_api",
        actor="jules-deepseek-agent",
        inputs={"run_id": run_id},
        outputs=call_meta,
        metadata={}
    )
    with open(f"agents/provenance/deepseek/{run_id}.prov.json", "w") as f:
        json.dump(load_provenance(provenance_id), f, sort_keys=True, indent=2)
