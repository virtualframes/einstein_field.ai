from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Any, Dict, List
import sqlite3, json, os, hmac, hashlib, time, uuid

app = FastAPI()
DB = "provenance.db"
SECRET = os.environ.get("EFAIAGENTSECRET", "dev-secret")  # replace in prod

def init_db():
    conn = sqlite3.connect(DB)
    conn.execute("""CREATE TABLE IF NOT EXISTS events (
        event_id TEXT PRIMARY KEY, actor TEXT, action TEXT, payload TEXT, signature TEXT, ts REAL
    )""")
    conn.commit()
    conn.close()

def sign_event(payload: str) -> str:
    return hmac.new(SECRET.encode(), payload.encode(), hashlib.sha256).hexdigest()

class EventIn(BaseModel):
    actor: str
    action: str
    payload: Dict[str, Any]

@app.on_event("startup")
def startup():
    init_db()

@app.post("/events")
def post_event(e: EventIn):
    event_id = str(uuid.uuid4())
    ts = time.time()
    payloadjson = json.dumps(e.payload, sort_keys=True)
    signature = sign_event(payloadjson + e.actor + e.action + str(ts))
    conn = sqlite3.connect(DB)
    conn.execute("INSERT INTO events(event_id, actor, action, payload, signature, ts) VALUES(?,?,?,?,?,?)",
                 (event_id, e.actor, e.action, payloadjson, signature, ts))
    conn.commit()
    conn.close()
    return {"event_id": event_id, "signature": signature, "ts": ts}

@app.get("/events")
def get_events(limit: int = 100):
    conn = sqlite3.connect(DB)
    rows = conn.execute("SELECT event_id, actor, action, payload, signature, ts FROM events ORDER BY ts DESC LIMIT ?", (limit,)).fetchall()
    conn.close()
    return [{"event_id": r[0], "actor": r[1], "action": r[2], "payload": json.loads(r[3]), "signature": r[4], "ts": r[5]} for r in rows]

@app.post("/submit")
def submit(doc: Dict[str, Any]):
    # Simple echo: create a 'submission' event and return claim placeholder
    actor = "agent:frontend"
    action = "submission"
    import time, uuid, json
    ts = time.time()
    event_id = str(uuid.uuid4())
    payloadjson = json.dumps(doc, sort_keys=True)
    signature = sign_event(payloadjson + actor + action + str(ts))
    conn = sqlite3.connect(DB)
    conn.execute("INSERT INTO events(event_id, actor, action, payload, signature, ts) VALUES(?,?,?,?,?,?)",
                 (event_id, actor, action, payloadjson, signature, ts))
    conn.commit()
    conn.close()
    # return minimal claim object for downstream agents
    claim = {
        "claim_id": str(uuid.uuid4()),
        "canonical_text": doc.get("text", "")[:200],
        "stubsympy": "Integral(Phiconst, (t, ti, tf)) >= rho_infl * V6",
        "fixtures": [{"Phiconst": 1e-5, "V6": 1e60, "rhoinfl": 1e-30, "ti": 1e-36, "tf": 1e-34}],
    }
    return {"event_id": event_id, "claim": claim}
