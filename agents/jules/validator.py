from pathlib import Path

def validate_plan(plan_path="agents/jules/PLAN.md"):
    p = Path(plan_path)
    content = p.read_text()
    if "Intent" not in content:
        raise AssertionError("Missing Intent section")
    if "- [ ]" not in content:
        raise AssertionError("No tasks found")
    print("Plan validation passed.")

if __name__ == '__main__':
    validate_plan()
