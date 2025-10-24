import os
from agents.jules.clients import deepseek_client
import json

def main():
    """Runs a smoke test for the DeepSeek client."""
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        print("DEEPSEEK_API_KEY not set. Skipping smoke test.")
        return

    # Test summarization
    summary = deepseek_client.summarize("This is a test.", 10)
    print(json.dumps(summary, indent=2))
    if summary["status"] != "success":
        print("Summarization failed.")
        exit(1)

    print("DeepSeek smoke test passed.")

if __name__ == "__main__":
    main()
