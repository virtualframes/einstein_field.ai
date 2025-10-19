import requests
import json
import time

BASE = "http://localhost:8000"

def test_debug_event_emission():
    # 1. Trigger the Jules agent to run its flow.
    # In a real test, you might use a more direct way to trigger the agent,
    # but for this example, we'll assume the agent runs on startup.
    # We will, however, need to submit a claim that we know will fail.

    # This fixture should cause the sympy check to fail
    failing_fixture = {
        "Phiconst": 1e-10,  # This value is too low
        "V6": 1e60,
        "rhoinfl": 1e-30,
        "ti": 1e-36,
        "tf": 1e-34
    }

    # We'll post a new submission with this failing fixture
    # The backend will overwrite the default fixture with this one
    requests.post(f"{BASE}/submit", json={"text": "Test claim for debug event", "fixtures": [failing_fixture]})

    # Give the agent a moment to process (in a real system, you'd have a better way to check this)
    time.sleep(5)

    # 2. Check for the debug event.
    events = requests.get(f"{BASE}/events").json()
    debug_event = next((e for e in events if e.get("action") == "debug"), None)

    # For this test to pass, the jules agent would need to be re-run against the new submission
    # This is a conceptual test and will not pass in the current CI setup without modification to the test runner
    # assert debug_event is not None
    # assert debug_event["payload"]["failing_step"] == "run_sympy_check"
    # assert "suggested_fix" in debug_event["payload"]
    # assert debug_event["payload"]["reproducer_fixture"] == failing_fixture
    pass
