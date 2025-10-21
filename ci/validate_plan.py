import sys
from agents.jules.validator import validate_plan

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python ci/validate_plan.py <plan_path>")
        sys.exit(1)
    validate_plan(sys.argv[1])
