import os
import time
import hashlib
import httpx

def summarize(text: str, max_tokens: int, model: str = "r1") -> dict:
    """Summarizes text using the DeepSeek API."""
    start_time = time.time()
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    api_base = os.environ.get("DEEPSEEK_API_BASE", "https://api.deepseek.com")

    with httpx.Client() as client:
        response = client.post(
            f"{api_base}/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": f"Summarize the following text in {max_tokens} tokens: {text}"},
                ],
            },
        )

    latency_ms = (time.time() - start_time) * 1000

    if response.status_code == 200:
        data = response.json()
        summary = data["choices"][0]["message"]["content"]
        return {
            "status": "success",
            "body": summary,
            "token_usage": data["usage"]["total_tokens"],
            "latency_ms": latency_ms,
            "input_hash": hashlib.sha256(text.encode()).hexdigest(),
            "output_hash": hashlib.sha256(summary.encode()).hexdigest(),
        }
    else:
        return {
            "status": "error",
            "body": response.text,
            "token_usage": 0,
            "latency_ms": latency_ms,
            "input_hash": hashlib.sha256(text.encode()).hexdigest(),
            "output_hash": None,
        }

# Other functions (reason, ocr) remain as placeholders for now.
def reason(prompt: str, model: str = "v3") -> dict:
    """Generates a reason using the DeepSeek API."""
    # This is a placeholder implementation.
    return {
        "status": "success",
        "body": "This is a reason.",
        "token_usage": 10,
        "latency_ms": 100,
        "input_hash": hashlib.sha256(prompt.encode()).hexdigest(),
        "output_hash": hashlib.sha256("This is a reason.".encode()).hexdigest(),
    }

def ocr(filepath: str) -> dict:
    """Performs OCR using the DeepSeek API."""
    # This is a placeholder implementation.
    return {
        "status": "success",
        "body": "This is the OCR text.",
        "token_usage": 10,
        "latency_ms": 100,
        "input_hash": hashlib.sha256(filepath.encode()).hexdigest(),
        "output_hash": hashlib.sha256("This is the OCR text.".encode()).hexdigest(),
    }
