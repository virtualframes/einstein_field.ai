import json
from cirecoveryengine.utils.io import canonical_write
import time
import argparse

def emit_debug_event(job_name, failing_step, error_message, suggested_fix, out="debug_event.json"):
    event = {
        "event": "debug",
        "agent": "jules",
        "job_name": job_name,
        "failing_step": failing_step,
        "error_message": error_message,
        "suggested_fix": suggested_fix,
        "timestamp": int(time.time())
    }
    canonical_write(out, event)
    print(f"Wrote debug event to {out}")
    return out

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--job", required=True)
    parser.add_argument("--step", required=True)
    parser.add_argument("--error", required=True)
    parser.add_argument("--fix", required=True)
    parser.add_argument("--out", default="debug_event.json")
    args = parser.parse_args()
    emit_debug_event(args.job, args.step, args.error, args.fix, args.out)
