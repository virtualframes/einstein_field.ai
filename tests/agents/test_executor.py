from agents.jules.executor import execute_plan
from pathlib import Path

def test_execute_plan_writes_trace(tmp_path):
    p = tmp_path / "PLAN.md"
    p.write_text("# Intent\n\n- [ ] Do something\n")
    out = execute_plan(str(p), replay_mode=True, seed=42)
    assert Path(out).exists()
    data = Path(out).read_text()
    assert "trace" in data
