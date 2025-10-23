import socket
import time

def wait_for_backend(host='localhost', port=8000, timeout=30):
    start = time.time()
    while time.time() - start < timeout:
        try:
            with socket.create_connection((host, port), timeout=2):
                print("✅ Backend reachable")
                return True
        except Exception:
            time.sleep(1)
    raise RuntimeError("❌ Backend not reachable after timeout")

if __name__ == "__main__":
    wait_for_backend()
