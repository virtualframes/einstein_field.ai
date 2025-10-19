import argparse, requests, os, json
BACKEND = os.environ.get("BACKEND_URL", "http://localhost:8000")
AGENT = os.environ.get("EFAIAGENTID", "agent:cli")

def post_event(action, payload):
    r = requests.post(f"{BACKEND}/events", json={"actor": AGENT, "action": action, "payload": payload})
    r.raise_for_status()
    print(r.json())

parser = argparse.ArgumentParser()
sub = parser.add_subparsers(dest="cmd")
pintent = sub.add_parser("intent")
pintent.add_argument("--files", nargs="+")
pintent.add_argument("--branch")
pintent.add_argument("--eta", default="30m")
pintent.add_argument("--summary", default="")
pupdate = sub.add_parser("update")
pupdate.add_argument("--progress")
pupdate.add_argument("--note", default="")
pcp = sub.add_parser("checkpoint")
pcp.add_argument("--artifact", default="./checkpoint.txt")
args = parser.parse_args()

if args.cmd == "intent":
    post_event("intent", {"files": args.files, "branch": args.branch, "eta": args.eta, "summary": args.summary})
elif args.cmd == "update":
    post_event("update", {"progress": args.progress, "note": args.note})
elif args.cmd == "checkpoint":
    post_event("checkpoint", {"artifact_path": args.artifact})
else:
    parser.print_help()
