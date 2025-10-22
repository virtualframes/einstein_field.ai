from agents.jules.validator import validate_plan
from pathlib import Path

def test_validate_plan_accepts_valid(tmp_path):
    p = tmp_path / "PLAN.md"
    p.write_text("Intent\n\n- [ ] x\n\nDependencies\n- a\n")
    validate_plan(str(p))
