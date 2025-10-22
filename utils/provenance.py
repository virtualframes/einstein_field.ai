import json
import hmac
import hashlib
from pathlib import Path

def sign_checkpoint(path, key):
    p = Path(path)
    data = p.read_bytes()
    sig = hmac.new(key.encode(), data, hashlib.sha256).hexdigest()
    return sig

def verify_checkpoint(path, key, sig):
    expected = sign_checkpoint(path, key)
    return hmac.compare_digest(expected, sig)
