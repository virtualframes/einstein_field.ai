from pathlib import Path
import os

def atomic_write(path, data):
    p = Path(path)
    tmp = p.with_suffix(".tmp")
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp.write_text(data)
    tmp.replace(p)
