import requests
import json
import time
import subprocess
import os

BASE = "http://localhost:8000"

def test_debug_event_emission():
    # This fixture should cause the sympy check to fail
    failing_fixture = {
        "Phiconst": 1e-10,  # This value is too low
        "V6": 1e60,
        "rhoinfl": 1e-30,
        "ti": 1e-36,
        "tf": 1e-34
    }

    # We'll post a new submission with this failing fixture
    requests.post(f"{BASE}/submit", json={"text": "Test claim for debug event", "fixtures": [failing_fixture]})

    # Re-run the jules agent to process the new submission
    # Set the BACKEND_URL so the agent can connect to the test server
    env = os.environ.copy()
    env["BACKEND_URL"] = BASE
    process = subprocess.run(["python", "agents/jules/jules.py"], capture_output=True, text=True, env=env)

    # Check stdout/stderr for debugging if the test fails
    print("Jules stdout:", process.stdout)
    print("Jules stderr:", process.stderr)

    assert process.returncode == 0

    # Check for the debug event.
    events = requests.get(f"{BASE}/events").json()
    debug_event = next((e for e in events if e.get("action") == "debug"), None)

    assert debug_event is not None
    assert debug_event["payload"]["failing_step"] == "run_sympy_check"
    assert "suggested_fix" in debug_event["payload"]
    assert "Phiconst" in debug_event["payload"]["reproducer_fixture"]
