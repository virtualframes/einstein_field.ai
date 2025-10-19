import json, sys
from collections import defaultdict
from agents.planner.planner import PlannerAgent

with open(sys.argv[1]) as f:
    events = json.load(f)

planner = PlannerAgent()

for e in events:
    # Check if the event is an 'intent' and has a 'payload'
    if e.get("action") == "intent" and "payload" in e:
        # Check if 'files' is in the payload
        if "files" in e["payload"]:
            planner.register_intent(e["actor"], e["payload"]["files"])

resolutions, conflicts = planner.arbitrate_conflicts()

if conflicts:
    print("Conflicts were detected, but the planner has arbitrated them:")
    for file, winner in resolutions.items():
        print(f"  - The file '{file}' has been assigned to the agent '{winner}'.")
    # In a real CI/CD pipeline, you might want to fail the build here
    # or take other actions, but for now, we'll just print the resolutions.
else:
    print("No conflicts detected.")
