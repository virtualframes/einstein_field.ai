from pathlib import Path

def validate_plan(plan_path="agents/jules/PLAN.md"):
    p = Path(plan_path)
    content = p.read_text()
    if "Intent" not in content:
        raise AssertionError("Missing Intent section")
    if "- [ ]" not in content:
        raise AssertionError("No tasks found")
    # basic dependency presence check
    if "Dependencies" not in content:
        raise AssertionError("Missing Dependencies section")
    print("Plan validation passed.")
