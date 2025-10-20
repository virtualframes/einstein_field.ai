import json
from cirecoveryengine.utils.io import atomic_write

def emit_debug_event(jobname, failing_step, error_message, suggested_fix, out="debug_event.json"):
    event = {
        "event": "debug",
        "agent": "jules",
        "jobname": jobname,
        "failing_step": failing_step,
        "error_message": error_message,
        "suggested_fix": suggested_fix
    }
    atomic_write(out, json.dumps(event, indent=2))
    print(f"Wrote debug event to {out}")
    return out

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--job", required=True, help="The name of the CI job that failed.")
    parser.add_argument("--step", required=True, help="The name of the step that failed.")
    parser.add_argument("--error", required=True, help="The error message from the failed step.")
    parser.add_argument("--fix", required=True, help="A suggested fix for the failure.")
    parser.add_argument("--out", default="debug_event.json", help="The output path for the debug event.")
    args = parser.parse_args()
    emit_debug_event(args.job, args.step, args.error, args.fix, args.out)
