import logging

def get_logger(name):
    """
    Returns a configured logger instance.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Create a console handler
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)

    # Create a formatter and add it to the handler
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    # Add the handler to the logger
    if not logger.handlers:
        logger.addHandler(handler)

    return logger

if __name__ == "__main__":
    logger = get_logger(__name__)
    logger.info("This is an informational message.")
    logger.warning("This is a warning message.")
