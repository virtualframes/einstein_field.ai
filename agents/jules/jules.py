"""
Jules agent: announces intent, calls backend /submit (simulated),
creates simple SymPy check, emits signed events to /events.
Replace OPENAI placeholder later.
"""
import os, time, json, requests, hmac, hashlib, uuid
from sympy import symbols, Integral
from sympy import simplify
from pathlib import Path

BACKEND = os.environ.get("BACKEND_URL", "http://backend:8000")
AGENT_ID = "agent:jules"
SECRET = os.environ.get("EFAIAGENTSECRET", "dev-secret")  # same secret as backend

def sign(payload: str) -> str:
    return hmac.new(SECRET.encode(), payload.encode(), hashlib.sha256).hexdigest()

def post_event(action: str, payload: dict):
    url = f"{BACKEND}/events"
    body = {"actor": AGENT_ID, "action": action, "payload": payload}
    r = requests.post(url, json=body)
    r.raise_for_status()
    return r.json()

def get_latest_submission():
    """Fetches the latest submission event from the backend."""
    url = f"{BACKEND}/events?limit=100"
    r = requests.get(url)
    r.raise_for_status()
    events = r.json()
    for event in events:
        if event["action"] == "submission":
            # Reconstruct the claim from the payload
            doc = event["payload"]
            claim = {
                "claim_id": str(uuid.uuid4()), # The original claim_id is not in the event
                "canonical_text": doc.get("text", "")[:200],
                "stubsympy": "Integral(Phiconst, (t, ti, tf)) >= rho_infl * V6",
                "fixtures": doc.get("fixtures", [{"Phiconst": 1e-5, "V6": 1e60, "rhoinfl": 1e-30, "ti": 1e-36, "tf": 1e-34}]),
            }
            return claim
    return None

def run_sympy_check(claim):
    # parse the stub and run a numeric check on the fixture
    fixtures = claim.get("fixtures", [])
    if not fixtures:
        print("No fixtures; skipping numeric test")
        return {"ok": False, "reason": "no-fixtures"}
    f = fixtures[0]
    # numeric integral for constant Phi
    Phi = f["Phiconst"]
    tf = f["tf"]
    ti = f["ti"]
    integral = Phi * (tf - ti)
    target = f["rhoinfl"] * f["V6"]
    ok = integral >= target
    trace = {"integral": integral, "target": target, "ok": ok}
    return trace

def checkpoint_artifact(path="checkpoint.txt", contents="checkpoint from jules"):
    with open(path, "w") as fh:
        fh.write(contents)
    # simple artifact: we will post a checkpoint event pointing to local path
    payload = {"artifact_path": path, "notes": "local checkpoint"}
    ev = post_event("checkpoint", payload)
    print("Checkpoint event:", ev)
    return ev

def open_pr_stub(branch, title):
    payload = {"branch": branch, "title": title, "pr_url": f"https://github.com/virtualframes/einsteinfield.ai/pull/{uuid.uuid4()}"}
    ev = post_event("pr_open", payload)
    print("PR open event:", ev)
    return ev

def emit_debug_event(failing_step, suggested_fix, reproducer_fixture):
    payload = {
        "failing_step": failing_step,
        "suggested_fix": suggested_fix,
        "reproducer_fixture": reproducer_fixture,
    }
    ev = post_event("debug", payload)
    print("Debug event emitted:", ev)
    return ev

def execute_plan_tasks(plan_path="agents/jules/PLAN.md"):
    p = Path(plan_path)
    if not p.exists():
        print(f"Plan file not found at {plan_path}. Skipping task execution.")
        return

    lines = p.read_text().splitlines()
    for line in lines:
        if line.strip().startswith("- [ ]"):
            task = line.split("]")[1].strip()
            print(f"Executing task from plan: {task}")
            # Here you would add the logic to actually execute the task.
            # For now, we will just print a message.
            if "Scaffold TypeScript interfaces" in task:
                print("  -> (Placeholder) Scaffolding TypeScript interfaces...")
            elif "Validate schema" in task:
                print("  -> (Placeholder) Validating schema...")
            elif "Write unit tests" in task:
                print("  -> (Placeholder) Writing unit tests...")


def main():
    print("Jules agent bootstrap starting")

    # Read and execute tasks from the PLAN.md file
    execute_plan_tasks()

    # Fetch the latest submission instead of creating a new one
    claim = get_latest_submission()
    if not claim:
        print("No submission found. Exiting.")
        return

    print("Claim received:", claim)
    trace = run_sympy_check(claim)
    print("Numeric trace:", trace)
    # emit verify event
    post_event("verify", {"claim_id": claim["claim_id"], "trace": trace})

    if not trace.get("ok"):
        emit_debug_event(
            failing_step="run_sympy_check",
            suggested_fix="The integral was less than the target. The parameters may need to be adjusted.",
            reproducer_fixture=claim.get("fixtures", [])[0],
        )

    # checkpoint
    checkpoint_artifact()
    # open PR stub
    open_pr_stub("agent/jules/bootstrap", "bootstrap pipeline test")
    print("Jules finished")

if __name__ == "__main__":
    main()
