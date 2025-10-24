from typing import List, Dict
from pyzotero import zotero
import json

def sync(api_key: str, user_id: str, collections: List[str] = None) -> Dict:
    """Fetches metadata from Zotero."""
    zot = zotero.Zotero(user_id, 'user', api_key)
    if collections:
        items = []
        for collection_id in collections:
            items.extend(zot.collection_items(collection_id))
    else:
        items = zot.top()

    # Create a snapshot ID (you can use a timestamp or a hash of the data)
    snapshot_id = f"zotero-snapshot-{len(items)}-{hash(str(items))}"

    # Save the data to a file
    with open("citations/zotero_export.json", "w") as f:
        json.dump(items, f, indent=2)

    return {"snapshot_id": snapshot_id, "item_count": len(items)}

def diff(snapshot_a_path: str, snapshot_b_path: str) -> Dict:
    """Returns added, removed, changed references."""
    with open(snapshot_a_path, "r") as f:
        snapshot_a = json.load(f)
    with open(snapshot_b_path, "r") as f:
        snapshot_b = json.load(f)

    # This is a placeholder implementation for the diff logic
    return {"added": [], "removed": [], "changed": []}
