import json, sys
from collections import defaultdict

with open(sys.argv[1]) as f:
    events = json.load(f)

claims = defaultdict(list)
for e in events:
    # Check if the event is an 'intent' and has a 'payload'
    if e.get("action") == "intent" and "payload" in e:
        # Check if 'files' is in the payload
        if "files" in e["payload"]:
            for f in e["payload"]["files"]:
                claims[f].append(e["actor"])

conflicts = {k: v for k, v in claims.items() if len(v) > 1}
if conflicts:
    print("Conflict detected:", conflicts)
    sys.exit(1)
else:
    print("No conflicts.")
