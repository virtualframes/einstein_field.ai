import json
from pathlib import Path
from cirecoveryengine.utils.io import atomic_write

def emit_checkpoint(failure_event_path=None, output_path="planner_checkpoint.json", method="SAC"):
    # parse failure_event if provided, else create minimal stub
    if failure_event_path and Path(failure_event_path).exists():
        data = json.loads(Path(failure_event_path).read_text())
    else:
        data = {"jobname":"unknown","errormessage":"no event provided"}
    checkpoint = {
        "planner_checkpoint_id": "pc:v1:autogen",
        "compression_method": method,
        "compression_ratio": 8.0,
        "compressed_trace": "<base64-vec-stub>",
        "retrieval_ids": [],
        "hydration_hint": "hydrate_symbols:Phi_bulk",
        "provenance_id": "prov:autogen",
    }
    atomic_write(output_path, json.dumps(checkpoint, indent=2))
    print(f"Wrote planner checkpoint to {output_path}")
    return output_path

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--job", help="job name or failure event json path", default=None)
    parser.add_argument("--out", help="output path", default="planner_checkpoint.json")
    args = parser.parse_args()
    emit_checkpoint(args.job, args.out)
