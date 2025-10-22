import json
import hashlib
from pathlib import Path
from cirecoveryengine.utils.io import canonical_write
import platform
import time

def hash_dependency_manifest(path="pyproject.toml"):
    p = Path(path)
    if not p.exists():
        return None
    return hashlib.sha256(p.read_bytes()).hexdigest()

def emit_checkpoint(failure_event_path=None, output_path="planner_checkpoint.json", method="SAC"):
    if failure_event_path and Path(failure_event_path).exists():
        data = json.loads(Path(failure_event_path).read_text())
    else:
        data = {"job_name":"unknown","error_message":"no event provided"}
    checkpoint = {
        "planner_checkpoint_id": "pc:v1:autogen",
        "seed": int(time.time()),
        "dependency_manifest_hash": hash_dependency_manifest("pyproject.toml"),
        "container_image_digests": [],
        "compression_method": method,
        "compression_version": "v1",
        "hydration_hint": "hydrate_symbols:Phi_bulk",
        "hardware_fingerprint": {"platform": platform.platform()},
        "provenance_id": "prov:autogen",
        "timestamp": int(time.time()),
        "failure_context": data
    }
    canonical_write(output_path, checkpoint)
    print(f"Wrote planner checkpoint to {output_path}")
    return output_path

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--job", help="job name or failure event json path", default=None)
    parser.add_argument("--out", help="output path", default="planner_checkpoint.json")
    args = parser.parse_args()
    emit_checkpoint(args.job, args.out)
