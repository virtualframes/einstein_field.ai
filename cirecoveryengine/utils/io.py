from pathlib import Path
import json

def atomic_write(path, data):
    p = Path(path)
    tmp = p.with_suffix(".tmp")
    tmp.write_text(data)
    tmp.replace(p)

def canonical_write(path, obj):
    p = Path(path)
    tmp = p.with_suffix(".tmp")
    # canonical JSON: sorted keys, compact floats handled by default json
    tmp.write_text(json.dumps(obj, sort_keys=True, indent=2))
    tmp.replace(p)
