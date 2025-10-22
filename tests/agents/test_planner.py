import tempfile
from agents.jules.planner import revise_plan
from pathlib import Path

def test_revise_plan_creates_file(tmp_path):
    src = tmp_path / "PLAN.md"
    src.write_text("# Intent\n\n- [ ] Task A\n")
    revise_plan(str(src), seed=12345)
    assert src.exists()
    content = src.read_text()
    assert "Optimized TODO" in content or "Task A" in content
