import os

def main():
    """Validates that the required secrets are present."""
    if not os.environ.get("DEEPSEEK_API_KEY"):
        print("DEEPSEEK_API_KEY not set.")
        exit(1)

    print("All required secrets are present.")

if __name__ == "__main__":
    main()
