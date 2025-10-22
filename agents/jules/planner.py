import re
from pathlib import Path
import time
import json

def stable_timestamp(seed=None):
    if seed is None:
        return int(time.time())
    # deterministic timestamp for replay/test fixtures
    return int(seed)

def revise_plan(plan_path="agents/jules/PLAN.md", seed=None):
    p = Path(plan_path)
    content = p.read_text()
    optimized = content.replace("TODO", "Optimized TODO")
    optimized = re.sub(r'^\s*-\s*\[ \]', '- [ ]', optimized, flags=re.M)
    # append revision metadata
    meta = {
        "revised_at": stable_timestamp(seed),
        "tool": "jules.planner.v1"
    }
    temp = p.with_suffix(".md.tmp")
    temp.write_text(optimized + "\n\n<!--REVISION-META: " + json.dumps(meta) + " -->\n")
    temp.replace(p)
    print(f"Plan revised and saved to {plan_path}.")
