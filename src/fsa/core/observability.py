# src/fsa/core/observability.py
import logging
from langfuse import Langfuse
from functools import lru_cache

logger = logging.getLogger(__name__)

@lru_cache(maxsize=1)
def get_langfuse_client():
    """Initializes and returns the Langfuse client singleton."""
    try:
        # Requires LANGFUSE_SECRET_KEY, LANGFUSE_PUBLIC_KEY env vars
        client = Langfuse()
        client.auth_check()
        logger.info("Langfuse initialized and authenticated.")
        return client
    except Exception as e:
        logger.warning(f"Langfuse initialization or authentication failed: {e}. Tracing will be disabled.")
        return None
