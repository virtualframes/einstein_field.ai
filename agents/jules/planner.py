import re
from pathlib import Path

def revise_plan(plan_path="agents/jules/PLAN.md"):
    p = Path(plan_path)
    content = p.read_text()
    # simple optimization: mark TODO->Optimized TODO and normalize task list
    optimized = content.replace("TODO", "Optimized TODO")
    # normalize checkboxes spacing
    optimized = re.sub(r'^\s*-\s*\[ \]', '- [ ]', optimized, flags=re.M)
    # atomic write
    temp = p.with_suffix(".md.tmp")
    temp.write_text(optimized)
    temp.replace(p)
    print(f"Plan revised and saved to {plan_path}.")

if __name__ == '__main__':
    revise_plan()
