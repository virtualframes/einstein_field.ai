import requests, time
BASE = "http://localhost:8000"
def test_submit_and_events():
    r = requests.post(f"{BASE}/submit", json={"text":"Test inflation claim."})
    assert r.status_code == 200
    claim = r.json()["claim"]
    # post an event
    ev = requests.post(f"{BASE}/events", json={"actor":"test-agent","action":"intent","payload":{"files":["x.py"],"branch":"feat/test"}})
    assert ev.status_code == 200
    events = requests.get(f"{BASE}/events")
    assert events.status_code == 200
    assert len(events.json()) >= 1
