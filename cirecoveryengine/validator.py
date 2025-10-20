import json
import argparse
from pathlib import Path

def validate_checkpoint(checkpoint_path):
    """
    Validates a planner checkpoint file.
    """
    p = Path(checkpoint_path)
    if not p.exists():
        raise FileNotFoundError(f"Checkpoint file not found: {checkpoint_path}")

    try:
        data = json.loads(p.read_text())
    except json.JSONDecodeError:
        raise ValueError("Invalid JSON in checkpoint file.")

    # Basic schema validation
    required_keys = [
        "planner_checkpoint_id",
        "compression_method",
        "compressed_trace",
        "provenance_id",
    ]
    for key in required_keys:
        if key not in data:
            raise ValueError(f"Missing required key in checkpoint: {key}")

    print("Planner checkpoint validation passed.")
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--trace-checkpoint", required=True, help="Path to the planner checkpoint file.")
    args = parser.parse_args()
    validate_checkpoint(args.trace_checkpoint)
