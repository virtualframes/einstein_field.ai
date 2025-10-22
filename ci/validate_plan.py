import sys
from agents.jules.validator import validate_plan

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: validate_plan.py <plan_path>")
        sys.exit(2)
    validate_plan(sys.argv[1])
