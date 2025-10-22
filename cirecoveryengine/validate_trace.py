#!/usr/bin/env python3
import json
from pathlib import Path
from cirecoveryengine.utils.io import canonical_write

def validate_replay(checkpoint_path):
    p = Path(checkpoint_path)
    if not p.exists():
        raise FileNotFoundError(checkpoint_path)
    checkpoint = json.loads(p.read_text())
    # minimal replay validation stub: assert required fields
    required = ["planner_checkpoint_id", "seed", "dependency_manifest_hash", "timestamp"]
    missing = [k for k in required if k not in checkpoint]
    if missing:
        raise AssertionError(f"Missing checkpoint fields: {missing}")
    print("Replay checkpoint validated (basic).")
    return True

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint", required=True)
    args = parser.parse_args()
    validate_replay(args.checkpoint)
