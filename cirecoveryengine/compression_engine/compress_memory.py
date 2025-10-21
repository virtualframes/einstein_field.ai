def compress_memory(memory):
    """
    A placeholder for memory compression logic.
    In a real implementation, this could involve techniques like:
    - Creating summaries of past conversations
    - Using embedding-based retrieval for relevant memories
    - Forgetting older or less relevant information
    """
    print(f"Original memory length: {len(memory)}")
    # Simple compression: keep only the most recent 3 items
    compressed = memory[-3:]
    print(f"Compressed memory length: {len(compressed)}")
    return compressed

if __name__ == "__main__":
    original_memory = [
        "User asked about the weather.",
        "I told them it was sunny.",
        "User asked about the temperature.",
        "I told them it was 75 degrees.",
        "User asked if it would rain.",
        "I told them it was unlikely.",
    ]
    compress_memory(original_memory)
