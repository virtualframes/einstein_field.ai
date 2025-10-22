from pathlib import Path
import json
import subprocess
import os

def execute_plan(plan_path="agents/jules/PLAN.md", replay_mode=False, seed=None):
    p = Path(plan_path)
    lines = p.read_text().splitlines()
    trace = []
    for line in lines:
        if line.strip().startswith("- [ ]"):
            task = line.split("]")[1].strip()
            entry = {"task": task, "status": "pending", "seed": seed}
            print(f"Executing: {task}")
            # deterministic routing placeholder: write trace entry
            # real routing would call model CLIs or local runners with seed
            entry["status"] = "skipped-stub" if replay_mode else "ok-stub"
            trace.append(entry)
    out = Path("agents/jules/execution_trace.json")
    out.write_text(json.dumps({"trace": trace}, indent=2))
    print(f"Wrote execution trace to {out}")
    return out
