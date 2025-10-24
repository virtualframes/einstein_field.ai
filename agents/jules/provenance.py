import json
import hashlib
from datetime import datetime, timezone

def record_execution(target: str, actor: str, inputs: dict, outputs: dict, metadata: dict) -> str:
    """Creates a signed provenance JSON and returns provenance_id (SHA256 of canonical JSON)."""
    provenance = {
        "target": target,
        "actor": actor,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "inputs": inputs,
        "outputs": outputs,
        "metadata": metadata,
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
