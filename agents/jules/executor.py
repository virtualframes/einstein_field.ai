from pathlib import Path
import subprocess

def execute_plan(plan_path="agents/jules/PLAN.md"):
    p = Path(plan_path)
    lines = p.read_text().splitlines()
    for line in lines:
        if line.strip().startswith("- [ ]"):
            task = line.split("]")[1].strip()
            print(f"Executing: {task}")
            # placeholder routing: choose model or local handler
            # e.g., subprocess.run(["python", "agents/jules/task_runner.py", "--task", task])
            # For now, record execution trace

if __name__ == '__main__':
    execute_plan()
